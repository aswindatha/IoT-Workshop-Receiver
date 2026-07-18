"""Data models for messages, log entries and application settings."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


# Maximum payload size accepted from the server (bytes).
MAX_MESSAGE_SIZE = 64 * 1024  # 64 KiB

# Known message types that get a dedicated card styling.
KNOWN_MESSAGE_TYPES = {
    "temperature",
    "humidity",
    "gps",
    "alert",
    "custom",
}


@dataclass
class LogEntry:
    """A single received message stored in the live log."""

    timestamp: float
    device: str
    message_type: str
    raw_data: str
    parsed: Optional[dict] = field(default=None)

    @property
    def timestamp_str(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp))

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "timestamp_str": self.timestamp_str,
            "device": self.device,
            "message_type": self.message_type,
            "raw_data": self.raw_data,
            "parsed": self.parsed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LogEntry":
        return cls(
            timestamp=data.get("timestamp", time.time()),
            device=data.get("device", "unknown"),
            message_type=data.get("message_type", "custom"),
            raw_data=data.get("raw_data", ""),
            parsed=data.get("parsed"),
        )


def parse_message(raw: str) -> Optional[LogEntry]:
    """Validate and parse an incoming server message.

    Security:
      * Never executes received data.
      * Treats everything as text.
      * Validates JSON.
      * Enforces a maximum message size.
      * Protects against malformed messages.

    Returns a :class:`LogEntry` or ``None`` when the payload is invalid.
    """
    if not isinstance(raw, str):
        return None

    if len(raw.encode("utf-8")) > MAX_MESSAGE_SIZE:
        return LogEntry(
            timestamp=time.time(),
            device="system",
            message_type="alert",
            raw_data="[rejected] message exceeds maximum size",
            parsed=None,
        )

    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        # Non-JSON payload: store as raw text, never execute.
        return LogEntry(
            timestamp=time.time(),
            device="unknown",
            message_type="custom",
            raw_data=raw,
            parsed=None,
        )

    if not isinstance(payload, dict):
        return LogEntry(
            timestamp=time.time(),
            device="unknown",
            message_type="custom",
            raw_data=raw,
            parsed=None,
        )

    device = str(payload.get("device") or payload.get("deviceId") or "unknown")
    message_type = str(payload.get("type") or payload.get("messageType") or "custom").lower()
    if message_type not in KNOWN_MESSAGE_TYPES:
        message_type = "custom"

    return LogEntry(
        timestamp=time.time(),
        device=device,
        message_type=message_type,
        raw_data=raw,
        parsed=payload,
    )


@dataclass
class Settings:
    """Persisted application settings."""

    cloud_url: str = "wss://iot-workshop-server.example.com/ws/receiver"
    dark_mode: bool = True
    auto_reconnect: bool = True
    max_logs: int = 500

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        return cls(
            cloud_url=str(data.get("cloud_url", "wss://iot-workshop-server.example.com/ws/receiver")),
            dark_mode=bool(data.get("dark_mode", True)),
            auto_reconnect=bool(data.get("auto_reconnect", True)),
            max_logs=int(data.get("max_logs", 500)),
        )
