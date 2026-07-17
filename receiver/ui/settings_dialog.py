"""Settings dialog for editing cloud URL, dark mode, auto-reconnect, max logs."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QCheckBox,
    QDialogButtonBox,
    QVBoxLayout,
    QGroupBox,
)

from ..models.models import Settings


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(420)
        self._settings = settings

        form = QFormLayout()
        self.url_edit = QLineEdit(settings.cloud_url)
        self.dark_check = QCheckBox("Enable dark mode")
        self.dark_check.setChecked(settings.dark_mode)
        self.reconnect_check = QCheckBox("Enable auto reconnect")
        self.reconnect_check.setChecked(settings.auto_reconnect)
        self.max_logs_spin = QSpinBox()
        self.max_logs_spin.setRange(50, 100000)
        self.max_logs_spin.setSingleStep(50)
        self.max_logs_spin.setValue(settings.max_logs)

        form.addRow("Cloud URL:", self.url_edit)
        form.addRow("", self.dark_check)
        form.addRow("", self.reconnect_check)
        form.addRow("Maximum logs:", self.max_logs_spin)

        group = QGroupBox("Connection & Appearance")
        group.setLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(group)
        layout.addWidget(buttons)

    def to_settings(self) -> Settings:
        return Settings(
            cloud_url=self.url_edit.text().strip() or self._settings.cloud_url,
            dark_mode=self.dark_check.isChecked(),
            auto_reconnect=self.reconnect_check.isChecked(),
            max_logs=self.max_logs_spin.value(),
        )
