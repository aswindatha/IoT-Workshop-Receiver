"""Settings persistence service."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

from ..models.models import Settings

logger = logging.getLogger(__name__)


def _settings_path() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home())
    return Path(base) / "IoTWorkshopReceiver" / "settings.json"


class SettingsService:
    """Load and save :class:`Settings` to a local JSON file."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self._path = path or _settings_path()

    def load(self) -> Settings:
        try:
            if self._path.exists():
                data = json.loads(self._path.read_text(encoding="utf-8"))
                return Settings.from_dict(data)
        except Exception:
            logger.warning("Failed to load settings, using defaults")
        return Settings()

    def save(self, settings: Settings) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(
                json.dumps(settings.to_dict(), indent=2),
                encoding="utf-8",
            )
        except Exception:
            logger.exception("Failed to save settings")
