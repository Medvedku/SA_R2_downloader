from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton
)
from datetime import datetime

from app.calendar import YearCalendarWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("R2 Parquet Downloader")
        self.setMinimumSize(1200, 800)

        # --- Central widget ---
        central = QWidget()
        layout = QVBoxLayout()

        # --- Header ---
        title = QLabel("R2 Parquet Downloader")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # --- Year calendar ---
        year = datetime.now().year
        calendar = YearCalendarWidget(year)
        layout.addWidget(calendar)

        # --- Action buttons ---
        layout.addWidget(QPushButton("Refresh"))
        layout.addWidget(QPushButton("Download new files"))

        central.setLayout(layout)
        self.setCentralWidget(central)
