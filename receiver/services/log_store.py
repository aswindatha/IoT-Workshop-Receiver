"""In-memory log store with bounded capacity and export helpers."""

from __future__ import annotations

import json
from collections import deque
from typing import List

from ..models.models import LogEntry


class LogStore:
    """Thread-safe-ish bounded store of :class:`LogEntry` items.

    Access happens from the Qt thread only (signals are queued), so a lock is
    not required. Capacity is enforced via a ``deque``.
    """

    def __init__(self, max_logs: int = 500) -> None:
        self._entries: deque[LogEntry] = deque(maxlen=max_logs)
        self._max_logs = max_logs

    @property
    def max_logs(self) -> int:
        return self._max_logs

    def set_max_logs(self, max_logs: int) -> None:
        self._max_logs = max_logs
        self._entries = deque(self._entries, maxlen=max_logs)

    def add(self, entry: LogEntry) -> None:
        self._entries.append(entry)

    def clear(self) -> None:
        self._entries.clear()

    def all(self) -> List[LogEntry]:
        return list(self._entries)

    def newest_first(self) -> List[LogEntry]:
        return list(reversed(self._entries))

    def __len__(self) -> int:
        return len(self._entries)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_json(self) -> str:
        return json.dumps(
            [e.to_dict() for e in self.newest_first()],
            indent=2,
            ensure_ascii=False,
        )

    def export_txt(self) -> str:
        lines = []
        for e in self.newest_first():
            lines.append(
                f"[{e.timestamp_str}] device={e.device} type={e.message_type}\n"
                f"{e.raw_data}\n"
            )
        return "\n".join(lines)
