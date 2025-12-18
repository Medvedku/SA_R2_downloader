from PySide6.QtWidgets import QApplication
import sys

from app.ui import MainWindow
from app.config import load_config
from app.config_dialog import ConfigDialog


def main():
    app = QApplication(sys.argv)

    config = load_config()
    if config is None:
        dlg = ConfigDialog()
        if dlg.exec() != dlg.Accepted:
            sys.exit(0)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
