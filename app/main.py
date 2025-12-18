from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
import sys

from app.ui import MainWindow
from app.config import load_config
from app.config_dialog import ConfigDialog


def main():
    # Force a consistent dark theme regardless of system settings
    app = QApplication(sys.argv)
    # Use Fusion for predictable palette behavior
    app.setStyle(QStyleFactory.create("Fusion"))

    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(45, 45, 45))
    palette.setColor(QPalette.WindowText, QColor(230, 230, 230))
    palette.setColor(QPalette.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ToolTipBase, QColor(230, 230, 230))
    palette.setColor(QPalette.ToolTipText, QColor(230, 230, 230))
    palette.setColor(QPalette.Text, QColor(230, 230, 230))
    palette.setColor(QPalette.Button, QColor(50, 50, 50))
    palette.setColor(QPalette.ButtonText, QColor(230, 230, 230))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(100, 149, 237))
    palette.setColor(QPalette.Highlight, QColor(100, 149, 237))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

    # Small global stylesheet tweaks for minimal, translucent accents
    app.setStyleSheet("""
        QToolTip { color: #ffffff; background-color: #2a2a2a; border: 1px solid #ffffff; }
        QMainWindow { background-color: #2d2d2d; }
        QWidget { background-color: transparent; }
        QPushButton { background-color: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.04); padding:6px; border-radius:4px; color: rgba(255,255,255,0.95); }
        QPushButton:hover { background-color: rgba(255,255,255,0.05); }
        QLabel { color: rgba(255,255,255,0.95); }
    """)

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
