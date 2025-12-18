from PySide6.QtWidgets import QApplication, QStyleFactory, QDialog
from PySide6.QtGui import QIcon
from pathlib import Path
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

    # Slightly lighter dark palette (less heavy) with retro-friendly accents
    palette = QPalette()
    # make the overall app a bit lighter than before
    palette.setColor(QPalette.Window, QColor(70, 70, 78))
    palette.setColor(QPalette.WindowText, QColor(245, 245, 245))
    palette.setColor(QPalette.Base, QColor(58, 58, 62))
    palette.setColor(QPalette.AlternateBase, QColor(74, 74, 82))
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
    # Retro stripes colors (user provided): 531a46, 9f1e34, d82b2c, e4532e, eea83a
    app.setStyleSheet("""
        QToolTip { color: #ffffff; background-color: #2a2a2a; border: 1px solid #ffffff; }
        QMainWindow { background-color: #474750; }
        QWidget { background-color: transparent; }
        /* Make editable fields slightly lighter with thin border for better visibility */
        QLineEdit {
            background-color: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.12);
            color: rgba(255,255,255,0.95);
            padding: 4px;
            border-radius: 4px;
        }
        QPushButton { background-color: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); padding:6px; border-radius:4px; color: rgba(255,255,255,0.95); }
        QPushButton:hover { background-color: rgba(255,255,255,0.07); }
        QLabel { color: rgba(255,255,255,0.95); }
        /* App title with retro VHS stripes */
        QLabel#appTitle {
            color: #fff;
            padding: 8px 12px;
            border-radius: 6px;
            background-image: linear-gradient(90deg, #531a46 0%, #9f1e34 25%, #d82b2c 50%, #e4532e 75%, #eea83a 100%);
        }
    """)

    config = load_config()
    if config is None:
        dlg = ConfigDialog()
        if dlg.exec() != QDialog.Accepted:
            sys.exit(0)

    window = MainWindow()
    # Set application icon from assets/icon.ico if present
    icon_path = Path(__file__).resolve().parent.parent / "assets" / "icon.ico"
    if icon_path.exists():
        icon = QIcon(str(icon_path))
        app.setWindowIcon(icon)
        window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
