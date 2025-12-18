from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
    QGridLayout
)
from PySide6.QtCore import Signal, QTimer, Qt
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
from app.config_dialog import ConfigDialog
from PySide6.QtWidgets import QDialog
from app.config import load_config, save_config
from app import theme


class MainWindow(QMainWindow):
    # Use object so arbitrary Python objects (dicts with tuple keys) can be emitted
    week_status_updated = Signal(object)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PRJ-16 --Rubint Technologies")
        
        # Calculate height as 90% of available screen height
        screen_geo = self.screen().availableGeometry()
        target_height = int(screen_geo.height() * 0.9)
        target_width = 1200
        
        self.setFixedSize(target_width, target_height)

        # Load config (theme not needed anymore, but keeping for other potential settings)
        self._config = load_config()

        # --- Central widget ---
        central = QWidget()
        layout = QVBoxLayout()

        # --- Header (visible retro stripes bar) ---
        header = QWidget()
        header.setObjectName("appHeader")
        header.setFixedHeight(56)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 6, 12, 6)

        title = QLabel("Parquet Downloader for Structural Health Monitoring of Steel Arena")
        title.setObjectName("appTitle")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF; background: transparent;")
        # header_layout.addWidget(title, alignment=Qt.AlignVCenter | Qt.AlignLeft)
        header_layout.addWidget(title, alignment=Qt.AlignVCenter | Qt.AlignCenter)

        # Apply retro stripe gradient as background to the header so it's clearly visible
        header.setStyleSheet(f"background: {theme.STRIPE_GRADIENT};")

        layout.addWidget(header)

        # --- Year calendar ---
        year = datetime.now().year
        calendar = YearCalendarWidget(year)
        self._calendar = calendar
        layout.addWidget(calendar)

        # --- Grid Layout for Controls (3 columns) ---
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(12)
        
        def _legend_item(color: str, border_color: str, text: str):
            w = QLabel(text)
            w.setAlignment(Qt.AlignCenter)
            w.setFixedHeight(44)
            w.setStyleSheet(f"background-color: {color}; border-radius: 0px; color: #ffffff; font-size: 11px; border: 1px solid {border_color};")
            return w

        # Row 0: Legends
        grid.addWidget(_legend_item("rgba(83, 26, 70, 0.3)", "#531a46", "synced"), 0, 0)
        grid.addWidget(_legend_item("rgba(216, 43, 44, 0.3)", "#d82b2c", "available in bucket"), 0, 1)
        grid.addWidget(_legend_item("rgba(128, 128, 128, 0.1)", "#808080", "no data"), 0, 2)

        # Row 1: Action Buttons
        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.clicked.connect(self._start_refresh)
        grid.addWidget(self._refresh_btn, 1, 0)

        self._download_btn = QPushButton("Download new files")
        self._download_btn.setEnabled(False)
        self._download_btn.clicked.connect(self._on_download)
        grid.addWidget(self._download_btn, 1, 1)

        self._settings_btn = QPushButton("Settings…")
        self._settings_btn.setToolTip("Change R2 credentials, bucket and local folder")
        self._settings_btn.clicked.connect(self._open_settings)
        grid.addWidget(self._settings_btn, 1, 2)
        
        layout.addLayout(grid)

        # Apply initial stylesheet
        self.setStyleSheet(theme.get_stylesheet())

        # connect signal
        self.week_status_updated.connect(self._on_week_status_updated)

        # Load persisted week status and render immediately
        try:
            ws = load_week_status()
            if ws:
                self._calendar.set_week_status(ws)
                # enable download button if anything available
                self._update_download_button(ws)
        except Exception as exc:
            # non-fatal: show a message
            QMessageBox.warning(self, "Warning", f"Failed to load saved week status: {exc}")

        # Year navigation now uses mouse wheel (scroll down = next year, scroll up = previous year)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def _start_refresh(self):
        # disable UI while refreshing and run scan in background
        self._refresh_btn.setEnabled(False)
        self._refresh_btn.setText("Refreshing...")
        # snapshot the existing week status to detect changes after refresh
        old_status = dict(self._calendar._week_status)

        def _worker(old_status=old_status):
            try:
                local_weeks = get_local_complete_weeks()
                bucket_weeks = get_bucket_complete_weeks()
                status = build_week_status(local_weeks, bucket_weeks)
                # log whether refresh discovered new available weeks
                from app.logger import logger
                old_available = {k for k, v in old_status.items() if v.get("bucket") and not v.get("local")}
                new_available = {k for k, v in status.items() if v.get("bucket") and not v.get("local")}
                added = new_available - old_available
                if added:
                    logger.info("Refresh: new data found for %d weeks", len(added))
                else:
                    logger.info("Refresh: everything up to date")
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
            # update download availability
            self._update_download_button(status)
            # reset download button label in case it was showing progress
            self._download_btn.setText("Download new files")
            try:
                save_week_status(status)
            except Exception:
                # ignore persistence errors for now
                pass
        finally:
            self._refresh_btn.setEnabled(True)
            self._refresh_btn.setText("Refresh")

    def _update_download_button(self, status: dict):
        # enable if any week has bucket=True and local=False
        has = any(v.get("bucket") and not v.get("local") for v in status.values())
        self._download_btn.setEnabled(bool(has))

    def _on_download(self):
        # Minimal download workflow placeholder: disable button and show message
        self._download_btn.setEnabled(False)
        self._download_btn.setText("Downloading...")
        # disable refresh to avoid concurrent operations
        self._refresh_btn.setEnabled(False)

        # determine weeks to download
        current_status = self._calendar._week_status
        weeks_to_download = {k for k, v in current_status.items() if v.get("bucket") and not v.get("local")}

        def _worker():
            try:
                from app.sync import download_weeks

                new_status, failures, downloaded = download_weeks(weeks_to_download)
                # emit updated status
                self.week_status_updated.emit(new_status)

                # Inform user with details and show folder location for convenience
                def _show_result():
                    msgs = []
                    if downloaded:
                        msgs.append(f"Downloaded {len(downloaded)} files.")
                        # show up to 5 file paths
                        sample = "\n".join(downloaded[:5])
                        msgs.append(f"Examples:\n{sample}")
                        # show folder of first downloaded file
                        first_folder = downloaded[0]
                    else:
                        msgs.append("No new files were downloaded (already present locally or nothing to download).")

                    if failures:
                        msgs.append(f"\nFailures: {len(failures)} files failed to download.")
                        # include examples of failures (up to 5) to help diagnose permission issues
                        sample_fail = "\n".join([f"{k}: {err}" for k, err in failures[:5]])
                        msgs.append(f"Examples of failures:\n{sample_fail}")

                    QMessageBox.information(self, "Download Result", "\n\n".join(msgs))

                QTimer.singleShot(0, _show_result)
            except Exception as exc:
                # show error in main thread
                QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Download Failed", str(exc)))
                # still emit refresh to update any partial changes
                try:
                    new_status = build_week_status(get_local_complete_weeks(), get_bucket_complete_weeks())
                    self.week_status_updated.emit(new_status)
                except Exception:
                    self.week_status_updated.emit({})

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def _open_settings(self):
        dlg = ConfigDialog()
        if dlg.exec() == QDialog.Accepted:
            # config saved; refresh and re-evaluate download availability
            try:
                ws = load_week_status()
                if ws:
                    self._calendar.set_week_status(ws)
                    self._update_download_button(ws)
            except Exception:
                pass
            # run a refresh to pick up new credentials / bucket
            self._start_refresh()
