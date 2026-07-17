"""Entry point for the IoT Workshop Receiver application."""

from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from receiver.ui.main_window import MainWindow


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main() -> int:
    configure_logging()
    app = QApplication(sys.argv)
    app.setApplicationName("IoT Workshop Receiver")
    app.setOrganizationName("IoTWorkshop")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
