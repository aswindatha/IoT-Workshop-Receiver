"""Qt stylesheets for light and dark modes."""

DARK_QSS = """
* { font-family: 'Segoe UI', 'Inter', sans-serif; }
QMainWindow, QWidget { background-color: #0f1117; color: #e6e6e6; }
QFrame#HeaderFrame { background-color: #161922; border-bottom: 1px solid #232838; }
QFrame#CardFrame { background-color: #161922; border: 1px solid #232838; border-radius: 10px; }
QLabel#TitleLabel { font-size: 20px; font-weight: 700; color: #ffffff; }
QLabel#CodeLabel { font-size: 28px; font-weight: 800; color: #4fc3f7; letter-spacing: 2px; }
QLabel#StatValue { font-size: 16px; font-weight: 600; color: #ffffff; }
QLabel#StatLabel { font-size: 11px; color: #8a93a6; }
QLabel#StatusOnline { color: #4caf50; font-weight: 700; }
QLabel#StatusOffline { color: #f44336; font-weight: 700; }
QLabel#StatusConnecting { color: #ffb300; font-weight: 700; }
QPushButton {
    background-color: #232838; border: 1px solid #2e3548; border-radius: 6px;
    padding: 7px 14px; color: #e6e6e6;
}
QPushButton:hover { background-color: #2e3548; border-color: #4fc3f7; }
QPushButton:pressed { background-color: #1c2230; }
QPushButton#PrimaryButton { background-color: #1976d2; border-color: #1976d2; color: white; font-weight: 600; }
QPushButton#PrimaryButton:hover { background-color: #2196f3; }
QTableWidget { background-color: #0f1117; alternate-background-color: #141821; gridline-color: #232838; border: 1px solid #232838; border-radius: 8px; }
QHeaderView::section { background-color: #161922; color: #8a93a6; border: none; border-bottom: 1px solid #232838; padding: 6px; }
QScrollBar:vertical { background: #0f1117; width: 10px; }
QScrollBar::handle:vertical { background: #2e3548; border-radius: 5px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QTextEdit { background-color: #0f1117; border: 1px solid #232838; border-radius: 6px; color: #b9c2d0; }
QLineEdit, QSpinBox, QComboBox {
    background-color: #161922; border: 1px solid #2e3548; border-radius: 6px;
    padding: 6px; color: #e6e6e6;
}
QCheckBox { color: #e6e6e6; }
QDialog { background-color: #0f1117; }
QGroupBox { border: 1px solid #232838; border-radius: 8px; margin-top: 12px; color: #8a93a6; }
QGroupBox::title { left: 10px; padding: 0 4px; }
"""

LIGHT_QSS = """
* { font-family: 'Segoe UI', 'Inter', sans-serif; }
QMainWindow, QWidget { background-color: #f5f7fa; color: #1a1a1a; }
QFrame#HeaderFrame { background-color: #ffffff; border-bottom: 1px solid #e0e4ea; }
QFrame#CardFrame { background-color: #ffffff; border: 1px solid #e0e4ea; border-radius: 10px; }
QLabel#TitleLabel { font-size: 20px; font-weight: 700; color: #0f1117; }
QLabel#CodeLabel { font-size: 28px; font-weight: 800; color: #1976d2; letter-spacing: 2px; }
QLabel#StatValue { font-size: 16px; font-weight: 600; color: #0f1117; }
QLabel#StatLabel { font-size: 11px; color: #6b7280; }
QLabel#StatusOnline { color: #2e7d32; font-weight: 700; }
QLabel#StatusOffline { color: #c62828; font-weight: 700; }
QLabel#StatusConnecting { color: #ef6c00; font-weight: 700; }
QPushButton {
    background-color: #ffffff; border: 1px solid #d0d5dd; border-radius: 6px;
    padding: 7px 14px; color: #1a1a1a;
}
QPushButton:hover { background-color: #eef2f7; border-color: #1976d2; }
QPushButton:pressed { background-color: #e0e7f0; }
QPushButton#PrimaryButton { background-color: #1976d2; border-color: #1976d2; color: white; font-weight: 600; }
QPushButton#PrimaryButton:hover { background-color: #2196f3; }
QTableWidget { background-color: #ffffff; alternate-background-color: #f5f7fa; gridline-color: #e0e4ea; border: 1px solid #e0e4ea; border-radius: 8px; }
QHeaderView::section { background-color: #f5f7fa; color: #6b7280; border: none; border-bottom: 1px solid #e0e4ea; padding: 6px; }
QScrollBar:vertical { background: #f5f7fa; width: 10px; }
QScrollBar::handle:vertical { background: #c4cad4; border-radius: 5px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QTextEdit { background-color: #ffffff; border: 1px solid #e0e4ea; border-radius: 6px; color: #374151; }
QLineEdit, QSpinBox, QComboBox {
    background-color: #ffffff; border: 1px solid #d0d5dd; border-radius: 6px;
    padding: 6px; color: #1a1a1a;
}
QCheckBox { color: #1a1a1a; }
QDialog { background-color: #f5f7fa; }
QGroupBox { border: 1px solid #e0e4ea; border-radius: 8px; margin-top: 12px; color: #6b7280; }
QGroupBox::title { left: 10px; padding: 0 4px; }
"""
