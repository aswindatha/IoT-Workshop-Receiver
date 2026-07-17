"""Pretty JSON viewer widget used to render individual message cards."""

from __future__ import annotations

import json
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QVBoxLayout,
)

from ..models.models import LogEntry, KNOWN_MESSAGE_TYPES


_TYPE_COLORS = {
    "temperature": "#ff7043",
    "humidity": "#29b6f6",
    "gps": "#66bb6a",
    "alert": "#ef5350",
    "custom": "#7e57c2",
}


class MessageCard(QFrame):
    """A formatted card representing a single received message."""

    def __init__(self, entry: LogEntry, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("CardFrame")
        self._entry = entry

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        header = QHBoxLayout()
        type_label = QLabel(entry.message_type.upper())
        type_label.setStyleSheet(
            f"color: {_TYPE_COLORS.get(entry.message_type, '#7e57c2')};"
            "font-weight: 700; font-size: 12px; letter-spacing: 1px;"
        )
        device_label = QLabel(f"device: {entry.device}")
        device_label.setStyleSheet("color: #8a93a6; font-size: 11px;")
        time_label = QLabel(entry.timestamp_str)
        time_label.setStyleSheet("color: #8a93a6; font-size: 11px;")
        header.addWidget(type_label)
        header.addStretch()
        header.addWidget(device_label)
        header.addWidget(time_label)
        layout.addLayout(header)

        body = QTextEdit()
        body.setReadOnly(True)
        body.setMaximumHeight(160)
        body.setPlainText(self._pretty())
        layout.addWidget(body)

    def _pretty(self) -> str:
        if self._entry.parsed is not None:
            try:
                return json.dumps(self._entry.parsed, indent=2, ensure_ascii=False)
            except Exception:
                return self._entry.raw_data
        return self._entry.raw_data
