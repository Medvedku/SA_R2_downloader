from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox
)
from PySide6.QtCore import Signal, QTimer
from datetime import datetime
import threading

from app.calendar import YearCalendarWidget
from app.sync import (
    get_local_complete_weeks,
    get_bucket_complete_weeks,
    build_week_status,
    load_week_status,
    save_week_status,
)


class MainWindow(QMainWindow):
    # Use object so arbitrary Python objects (dicts with tuple keys) can be emitted
    week_status_updated = Signal(object)

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
        self._calendar = calendar
        layout.addWidget(calendar)

        # --- Action buttons ---
        # Action buttons
        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.clicked.connect(self._start_refresh)
        layout.addWidget(self._refresh_btn)

        layout.addWidget(QPushButton("Download new files"))

        # connect signal
        self.week_status_updated.connect(self._on_week_status_updated)

        # Load persisted week status and render immediately
        try:
            ws = load_week_status()
            if ws:
                self._calendar.set_week_status(ws)
        except Exception as exc:
            # non-fatal: show a message
            QMessageBox.warning(self, "Warning", f"Failed to load saved week status: {exc}")

        central.setLayout(layout)
        self.setCentralWidget(central)

    def _start_refresh(self):
        # disable UI while refreshing and run scan in background
        self._refresh_btn.setEnabled(False)
        self._refresh_btn.setText("Refreshing...")

        def _worker():
            try:
                local_weeks = get_local_complete_weeks()
                bucket_weeks = get_bucket_complete_weeks()
                status = build_week_status(local_weeks, bucket_weeks)
                # emit to UI thread
                self.week_status_updated.emit(status)
            except Exception as exc:
                # forward as signal with empty status and schedule message box in main thread
                self.week_status_updated.emit({})
                QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Refresh Failed", str(exc)))
            finally:
                # Re-enable button in main thread via emitted signal handler
                pass

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def _on_week_status_updated(self, status: dict):
        try:
            # Update calendar and persist
            self._calendar.set_week_status(status)
            try:
                save_week_status(status)
            except Exception:
                # ignore persistence errors for now
                pass
        finally:
            self._refresh_btn.setEnabled(True)
            self._refresh_btn.setText("Refresh")
