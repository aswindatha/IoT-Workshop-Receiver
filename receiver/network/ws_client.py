"""Async WebSocket client for the IoT Workshop Receiver.

Runs an asyncio event loop on a background thread and bridges events to the
Qt event loop via Qt signals. Supports auto-reconnect, heartbeat/ping and
latency measurement.
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from typing import Optional

from PySide6.QtCore import QObject, Signal

try:
    import websockets
    from websockets.exceptions import ConnectionClosed
except Exception:  # pragma: no cover - websockets is a hard dependency
    websockets = None
    ConnectionClosed = Exception

logger = logging.getLogger(__name__)


HEARTBEAT_INTERVAL = 15.0  # seconds between ping frames
RECONNECT_BASE_DELAY = 1.0  # initial backoff
RECONNECT_MAX_DELAY = 30.0  # cap for backoff


class WebSocketClient(QObject):
    """Bridge between an asyncio websocket connection and Qt signals."""

    # Emitted when the connection state changes.
    # status: "online" | "offline" | "connecting"
    status_changed = Signal(str)

    # Emitted with the receiver code assigned by the server.
    code_received = Signal(str)

    # Emitted with a raw text message (already validated upstream).
    message_received = Signal(str)

    # Emitted with the latest measured latency in milliseconds.
    latency_updated = Signal(float)

    # Emitted with a human readable error/info string.
    info = Signal(str)

    def __init__(self, url: str, auto_reconnect: bool = True) -> None:
        super().__init__()
        self._url = url
        self._auto_reconnect = auto_reconnect
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event: Optional[asyncio.Event] = None
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._connected_since: Optional[float] = None
        self._last_ping_sent: Optional[float] = None
        self._backoff = RECONNECT_BASE_DELAY
        self._running = False

    # ------------------------------------------------------------------
    # Public API (called from the Qt thread)
    # ------------------------------------------------------------------

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._loop and self._ws:
            try:
                asyncio.run_coroutine_threadsafe(self._ws.close(), self._loop)
            except Exception:
                pass
        if self._loop and self._stop_event:
            try:
                self._loop.call_soon_threadsafe(self._stop_event.set)
            except Exception:
                pass
        if self._thread:
            self._thread.join(timeout=5)

    def update_url(self, url: str) -> None:
        self._url = url

    def set_auto_reconnect(self, enabled: bool) -> None:
        self._auto_reconnect = enabled

    def reconnect(self) -> None:
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._force_reconnect(), self._loop)

    @property
    def connected_since(self) -> Optional[float]:
        return self._connected_since

    # ------------------------------------------------------------------
    # Background asyncio loop
    # ------------------------------------------------------------------

    def _run_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._stop_event = asyncio.Event()
        try:
            self._loop.run_until_complete(self._main())
        except Exception:
            logger.exception("Event loop crashed")
        finally:
            self._loop.close()

    async def _main(self) -> None:
        self._backoff = RECONNECT_BASE_DELAY
        while self._running and not self._stop_event.is_set():
            self.status_changed.emit("connecting")
            try:
                await self._connect_and_serve()
                self._backoff = RECONNECT_BASE_DELAY  # reset on clean disconnect
            except Exception as exc:
                logger.warning("Connection error: %s", exc)
                self.info.emit(f"Connection error: {exc}")
            finally:
                self._connected_since = None
                self.status_changed.emit("offline")

            if not self._running or not self._auto_reconnect:
                break
            if self._stop_event.is_set():
                break
            self.info.emit(f"Reconnecting in {self._backoff:.0f}s ...")
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self._backoff)
                break  # stop requested
            except asyncio.TimeoutError:
                pass
            self._backoff = min(self._backoff * 2, RECONNECT_MAX_DELAY)

    async def _force_reconnect(self) -> None:
        """Close the active connection so the auto-reconnect loop restarts."""
        self.info.emit("Manual reconnect requested")
        self._backoff = RECONNECT_BASE_DELAY  # reset backoff for immediate reconnect
        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass

    async def _connect_and_serve(self) -> None:
        if websockets is None:
            raise RuntimeError("websockets library is not installed")

        async with websockets.connect(
            self._url,
            ping_interval=None,  # we manage our own heartbeat
            ping_timeout=None,
            close_timeout=5,
            max_size=2 * 1024 * 1024,
        ) as ws:
            self._ws = ws
            self._connected_since = time.time()
            self.status_changed.emit("online")
            self.info.emit("Connected to cloud server")

            # Announce ourselves as a receiver.
            await self._safe_send(ws, json.dumps({"role": "receiver"}))

            heartbeat_task = asyncio.ensure_future(self._heartbeat(ws))
            try:
                async for raw in ws:
                    await self._handle_frame(ws, raw)
            finally:
                self._ws = None
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except (asyncio.CancelledError, Exception):
                    pass

    async def _handle_frame(self, ws, raw) -> None:
        if isinstance(raw, (bytes, bytearray)):
            try:
                raw = raw.decode("utf-8")
            except UnicodeDecodeError:
                self.info.emit("Received non-UTF8 frame, ignoring")
                return

        # Server may send control frames (code assignment, pong).
        try:
            control = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            control = None

        if isinstance(control, dict):
            event = control.get("event")
            if event == "connected":
                code = control.get("receiver_code") or control.get("receiverCode") or control.get("code")
                if code:
                    self.code_received.emit(str(code))
                return
            if event == "pong" and self._last_ping_sent:
                latency = (time.time() - self._last_ping_sent) * 1000.0
                self.latency_updated.emit(round(latency, 1))
                self._last_ping_sent = None
                return
            # Drop known control frames; let data messages (event == "message") fall through.
            if event in ("heartbeat_ack", "info", "timeout"):
                return

        # Normal data message.
        self.message_received.emit(raw)

    async def _heartbeat(self, ws) -> None:
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            self._last_ping_sent = time.time()
            await self._safe_send(ws, json.dumps({"event": "ping", "ts": time.time()}))

    async def _safe_send(self, ws, data: str) -> None:
        try:
            await ws.send(data)
        except ConnectionClosed:
            raise
        except Exception as exc:
            logger.warning("Failed to send: %s", exc)
