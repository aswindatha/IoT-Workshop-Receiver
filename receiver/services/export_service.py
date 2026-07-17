"""Export helper writing log data to JSON or TXT files."""

from __future__ import annotations

from pathlib import Path

from .log_store import LogStore


def export_logs(store: LogStore, path: str | Path, fmt: str) -> Path:
    """Write the current log store to ``path`` in the given ``fmt``.

    ``fmt`` must be ``"json"`` or ``"txt"``.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt.lower() == "json":
        path.write_text(store.export_json(), encoding="utf-8")
    else:
        path.write_text(store.export_txt(), encoding="utf-8")
    return path
