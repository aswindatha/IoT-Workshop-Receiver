"""Main application window for the IoT Workshop Receiver."""

from __future__ import annotations

import time
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QClipboard, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..models.models import LogEntry, Settings, parse_message
from ..network.ws_client import WebSocketClient
from ..resources.styles import DARK_QSS, LIGHT_QSS
from ..services.export_service import export_logs
from ..services.log_store import LogStore
from ..services.settings_service import SettingsService
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("IoT Workshop Receiver")
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)

        self.settings_service = SettingsService()
        self.settings: Settings = self.settings_service.load()
        self.log_store = LogStore(max_logs=self.settings.max_logs)
        self.client = WebSocketClient(
            url=self.settings.cloud_url,
            auto_reconnect=self.settings.auto_reconnect,
        )

        self._receiver_code: str = "—"
        self._connected_since: Optional[float] = None
        self._last_message_time: Optional[float] = None
        self._latency_ms: Optional[float] = None

        self._build_ui()
        self._apply_theme()
        self._connect_signals()
        self._start_clock()

        self.client.start()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(14)

        root.addWidget(self._build_header())
        root.addWidget(self._build_stats())
        root.addLayout(self._build_buttons())
        root.addWidget(self._build_logs(), 1)

        self.statusBar().showMessage("Ready")

    def _build_header(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("HeaderFrame")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)

        title = QLabel("IoT Workshop Receiver")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)
        layout.addStretch()

        status_box = QVBoxLayout()
        status_box.setSpacing(2)
        status_box.setAlignment(Qt.AlignRight)
        self.status_label = QLabel("Offline")
        self.status_label.setObjectName("StatusOffline")
        self.status_label.setAlignment(Qt.AlignRight)
        status_hint = QLabel("Cloud Status")
        status_hint.setObjectName("StatLabel")
        status_hint.setAlignment(Qt.AlignRight)
        status_box.addWidget(self.status_label)
        status_box.addWidget(status_hint)
        layout.addLayout(status_box)

        code_box = QVBoxLayout()
        code_box.setSpacing(2)
        code_box.setAlignment(Qt.AlignRight)
        self.code_label = QLabel(self._receiver_code)
        self.code_label.setObjectName("CodeLabel")
        self.code_label.setAlignment(Qt.AlignRight)
        code_hint = QLabel("Receiver Code")
        code_hint.setObjectName("StatLabel")
        code_hint.setAlignment(Qt.AlignRight)
        code_box.addWidget(self.code_label)
        code_box.addWidget(code_hint)
        layout.addLayout(code_box)

        return frame

    def _build_stats(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("CardFrame")
        grid = QGridLayout(frame)
        grid.setContentsMargins(16, 14, 16, 14)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(8)

        self.stat_messages = self._stat_cell(grid, 0, 0, "Messages Received", "0")
        self.stat_since = self._stat_cell(grid, 0, 1, "Connected Since", "—")
        self.stat_last = self._stat_cell(grid, 0, 2, "Last Message", "—")
        self.stat_latency = self._stat_cell(grid, 0, 3, "Server Latency", "— ms")
        return frame

    def _stat_cell(self, grid: QGridLayout, row: int, col: int, label: str, value: str) -> QLabel:
        value_label = QLabel(value)
        value_label.setObjectName("StatValue")
        hint_label = QLabel(label)
        hint_label.setObjectName("StatLabel")
        grid.addWidget(value_label, row, col * 2)
        grid.addWidget(hint_label, row + 1, col * 2)
        return value_label

    def _build_buttons(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        self.btn_copy = QPushButton("Copy Receiver Code")
        self.btn_copy.setObjectName("PrimaryButton")
        self.btn_copy.clicked.connect(self._copy_code)

        self.btn_clear = QPushButton("Clear Logs")
        self.btn_clear.clicked.connect(self._clear_logs)

        self.btn_reconnect = QPushButton("Reconnect")
        self.btn_reconnect.clicked.connect(self._reconnect)

        self.btn_export = QPushButton("Export Logs")
        self.btn_export.clicked.connect(self._export_logs)

        self.btn_settings = QPushButton("Settings")
        self.btn_settings.clicked.connect(self._open_settings)

        row.addWidget(self.btn_copy)
        row.addWidget(self.btn_clear)
        row.addWidget(self.btn_reconnect)
        row.addWidget(self.btn_export)
        row.addStretch()
        row.addWidget(self.btn_settings)
        return row

    def _build_logs(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("CardFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        header = QLabel("Live Logs")
        header.setObjectName("StatValue")
        layout.addWidget(header)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Device", "Type", "JSON Data"])
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.table, 1)
        return frame

    # ------------------------------------------------------------------
    # Signals / wiring
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self.client.status_changed.connect(self._on_status)
        self.client.code_received.connect(self._on_code)
        self.client.message_received.connect(self._on_message)
        self.client.latency_updated.connect(self._on_latency)
        self.client.info.connect(lambda msg: self.statusBar().showMessage(msg, 5000))

    def _start_clock(self) -> None:
        self.clock = QTimer(self)
        self.clock.setInterval(1000)
        self.clock.timeout.connect(self._refresh_time_stats)
        self.clock.start()

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_status(self, status: str) -> None:
        mapping = {
            "online": ("Online", "StatusOnline"),
            "offline": ("Offline", "StatusOffline"),
            "connecting": ("Connecting…", "StatusConnecting"),
        }
        text, obj = mapping.get(status, ("Offline", "StatusOffline"))
        self.status_label.setText(text)
        self.status_label.setObjectName(obj)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        if status == "online":
            self._connected_since = self.client.connected_since or time.time()
        else:
            self._connected_since = None
        self._refresh_time_stats()

    def _on_code(self, code: str) -> None:
        self._receiver_code = code
        self.code_label.setText(code)
        self.statusBar().showMessage(f"Receiver code assigned: {code}", 5000)

    def _on_message(self, raw: str) -> None:
        entry = parse_message(raw)
        if entry is None:
            return
        self.log_store.add(entry)
        self._last_message_time = entry.timestamp
        self._append_row(entry)
        self.stat_messages.setText(str(len(self.log_store)))
        self._refresh_time_stats()

    def _on_latency(self, latency_ms: float) -> None:
        self._latency_ms = latency_ms
        self.stat_latency.setText(f"{latency_ms:.1f} ms")

    def _refresh_time_stats(self) -> None:
        if self._connected_since:
            delta = time.time() - self._connected_since
            self.stat_since.setText(self._format_duration(delta))
        else:
            self.stat_since.setText("—")

        if self._last_message_time:
            ago = time.time() - self._last_message_time
            self.stat_last.setText(self._format_duration(ago) + " ago")
        else:
            self.stat_last.setText("—")

    @staticmethod
    def _format_duration(seconds: float) -> str:
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds}s"
        if seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        return f"{seconds // 3600}h {(seconds % 3600) // 60}m"

    def _append_row(self, entry: LogEntry) -> None:
        # Enforce max logs in the table as well.
        while self.table.rowCount() >= self.log_store.max_logs:
            self.table.removeRow(self.table.rowCount() - 1)

        row = 0
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(entry.timestamp_str))
        self.table.setItem(row, 1, QTableWidgetItem(entry.device))
        self.table.setItem(row, 2, QTableWidgetItem(entry.message_type))
        pretty = entry.raw_data
        if entry.parsed is not None:
            import json as _json
            try:
                pretty = _json.dumps(entry.parsed, indent=2, ensure_ascii=False)
            except Exception:
                pretty = entry.raw_data
        data_item = QTableWidgetItem(pretty)
        data_item.setToolTip(pretty)
        self.table.setItem(row, 3, data_item)

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------

    def _copy_code(self) -> None:
        clipboard: QClipboard = QGuiApplication.clipboard()
        clipboard.setText(self._receiver_code)
        self.statusBar().showMessage(f"Copied receiver code: {self._receiver_code}", 3000)

    def _clear_logs(self) -> None:
        self.log_store.clear()
        self.table.setRowCount(0)
        self.stat_messages.setText("0")
        self._last_message_time = None
        self._refresh_time_stats()
        self.statusBar().showMessage("Logs cleared", 3000)

    def _reconnect(self) -> None:
        self.client.reconnect()
        self.statusBar().showMessage("Reconnecting…", 3000)

    def _export_logs(self) -> None:
        if len(self.log_store) == 0:
            QMessageBox.information(self, "Export Logs", "No logs to export.")
            return
        fmt_filter = "JSON (*.json);;TXT (*.txt)"
        path, selected = QFileDialog.getSaveFileName(
            self, "Export Logs", "receiver_logs", fmt_filter
        )
        if not path:
            return
        fmt = "json" if selected.lower().startswith("json") else "txt"
        try:
            out = export_logs(self.log_store, path, fmt)
            QMessageBox.information(self, "Export Logs", f"Exported to:\n{out}")
        except Exception as exc:
            QMessageBox.critical(self, "Export Logs", f"Export failed:\n{exc}")

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self.settings, self)
        if dlg.exec():
            new_settings = dlg.to_settings()
            self.settings = new_settings
            self.settings_service.save(new_settings)
            self.log_store.set_max_logs(new_settings.max_logs)
            self.client.update_url(new_settings.cloud_url)
            self.client.set_auto_reconnect(new_settings.auto_reconnect)
            self._apply_theme()
            self.client.reconnect()
            self.statusBar().showMessage("Settings saved", 3000)

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def _apply_theme(self) -> None:
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.setStyleSheet(DARK_QSS if self.settings.dark_mode else LIGHT_QSS)

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        try:
            self.client.stop()
        except Exception:
            pass
        super().closeEvent(event)
