from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("R2 Parquet Downloader")
        self.setMinimumSize(500, 300)

        central = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("R2 Parquet Downloader"))
        layout.addWidget(QPushButton("Refresh"))
        layout.addWidget(QPushButton("Download new files"))

        central.setLayout(layout)
        self.setCentralWidget(central)