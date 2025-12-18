from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QGridLayout, QFrame,
    QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt
from datetime import date
import calendar


class DayCell(QFrame):
    def __init__(self, day: date, current_month: int, week_status: dict | None = None):
        super().__init__()

        self.setObjectName("dayCell")
        self.day = day
        self.iso_year, self.iso_week, _ = day.isocalendar()

        self.setFixedSize(36, 24)

        label = QLabel(str(day.day))
        label.setAlignment(Qt.AlignTop | Qt.AlignRight)

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 2, 4, 2)
        layout.addWidget(label)
        self.setLayout(layout)

        # Initial style will be set by update_style which is called by the parent
        self._week_status = week_status or {}
        self._current_month = current_month
        self.update_style()

    def update_style(self):
        week_key = (self.iso_year, self.iso_week)
        ws = self._week_status.get(week_key, {"local": False, "bucket": False})
        
        # Color palette
        purple = "#531a46"
        yellow = "#eea83a"
        crimson = "#d82b2c"

        # Determine colors based on status
        if ws.get("bucket") and ws.get("local"):
            # synced
            bg = "rgba(83, 26, 70, 0.3)"
            border = purple
            text = "#FFFFFF"
        elif ws.get("bucket") and not ws.get("local"):
            # available in bucket
            bg = "rgba(216, 43, 44, 0.3)"
            border = crimson
            text = "#FFFFFF"
        else:
            # default
            if self.day.month != self._current_month:
                bg = "rgba(128, 128, 128, 0.05)"
                border = "rgba(128, 128, 128, 0.1)"
                text = "rgba(128, 128, 128, 0.5)"
            else:
                bg = "rgba(128, 128, 128, 0.1)"
                border = "rgba(128, 128, 128, 0.2)"
                text = "#FFFFFF"

        base_style = f"""
            QFrame#dayCell {{
                background-color: {bg};
                color: {text};
                border: 1px solid {border};
                border-radius: 2px;
            }}
            QFrame#dayCell QLabel {{ color: {text}; background: transparent; border: none; }}
        """

        from datetime import date as _date
        if self.day == _date.today():
            today_style = f"""
                QFrame#dayCell {{
                    background-color: transparent;
                    color: {text};
                    border: 2px solid {yellow};
                    border-radius: 2px;
                }}
                QFrame#dayCell QLabel {{ color: {text}; font-weight: bold; background: transparent; border: none; }}
            """
            self.setStyleSheet(today_style)
        else:
            self.setStyleSheet(base_style)


class WeekCell(QFrame):
    def __init__(self, year: int, week: int):
        super().__init__()

        self.year = year
        self.week = week

        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedSize(38, 26)

        label = QLabel(f"W{week:02d}")
        label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(label)

        self.setLayout(layout)

        # default minimal style for week label
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 1px solid rgba(255,255,255,0.04);
                border-radius: 4px;
            }
            QFrame QLabel { color: rgba(255,255,255,0.75); font-size: 11px; }
        """)


class MonthWidget(QWidget):
    def __init__(self, year: int, month: int, week_status: dict | None = None):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(4)

        title = QLabel(calendar.month_name[month])
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; color: rgba(255,255,255,0.95);")

        grid = QGridLayout()
        grid.setSpacing(2)

        # Weekday header
        for col, name in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 10px; color: rgba(255,255,255,0.65);")
            grid.addWidget(lbl, 0, col)

        cal = calendar.Calendar(firstweekday=calendar.MONDAY)
        days = list(cal.itermonthdates(year, month))

        row = 1
        col = 0
        for d in days:
            cell = DayCell(d, month, week_status=week_status)
            grid.addWidget(cell, row, col)

            col += 1
            if col == 7:
                col = 0
                row += 1

        layout.addWidget(title)
        layout.addLayout(grid)
        self.setLayout(layout)
        
        self.title_label = title
        self.grid = grid


class YearCalendarWidget(QWidget):
    def __init__(self, year: int):
        super().__init__()

        from datetime import datetime

        # Limits: project started in 2024, allow some future years
        self._min_year = 2024
        self._max_year = datetime.now().year + 10
        # ensure initial year is in allowed range
        self.year = max(year, self._min_year)

        self._main_layout = QVBoxLayout()
        self._main_layout.setSpacing(8)

        # Header with prev / year / next
        header = QHBoxLayout()
        header.setSpacing(6)

        self._prev_btn = QPushButton("←")
        self._prev_btn.setObjectName("yearNavBtn")
        self._prev_btn.setFixedSize(30, 30)
        self._prev_btn.setToolTip("Previous year (Left Arrow)")
        self._prev_btn.clicked.connect(self._on_prev)

        self._next_btn = QPushButton("→")
        self._next_btn.setObjectName("yearNavBtn")
        self._next_btn.setFixedSize(30, 30)
        self._next_btn.setToolTip("Next year (Right Arrow)")
        self._next_btn.clicked.connect(self._on_next)

        self._year_label = QLabel(str(self.year))
        self._year_label.setObjectName("yearLabel")
        self._year_label.setAlignment(Qt.AlignCenter)
        self._year_label.setStyleSheet("font-weight: bold; color: rgba(255,255,255,0.95);")

        header.addWidget(self._prev_btn)
        header.addStretch()
        header.addWidget(self._year_label)
        header.addStretch()
        header.addWidget(self._next_btn)

        self._main_layout.addLayout(header)
        
        # Ensure focus for key events
        self.setFocusPolicy(Qt.StrongFocus)

        self._grid = QGridLayout()
        self._grid.setSpacing(12)
        self._main_layout.addLayout(self._grid)

        # current week status (tuple keys -> dict)
        self._week_status: dict[tuple, dict] = {}

        self.setLayout(self._main_layout)

        self._build_months()

    def _clear_grid(self):
        # remove widgets from grid
        for i in reversed(range(self._grid.count())):
            item = self._grid.itemAt(i)
            w = item.widget()
            if w is not None:
                w.setParent(None)

    def _build_months(self):
        self._clear_grid()

        month = 1
        for row in range(3):
            for col in range(4):
                self._grid.addWidget(MonthWidget(self.year, month, week_status=self._week_status), row, col)
                month += 1

    def set_week_status(self, week_status: dict):
        """Update internal week status and refresh rendering."""
        self._week_status = week_status or {}
        # rebuild months to apply new styles
        self._build_months()

    def _on_prev(self):
        if self.year > self._min_year:
            self.year -= 1
            self._year_label.setText(str(self.year))
            self._build_months()

    def _on_next(self):
        if self.year < self._max_year:
            self.year += 1
            self._year_label.setText(str(self.year))
            self._build_months()

    def wheelEvent(self, event):
        """Scroll wheel navigation: scroll down = next year, scroll up = previous year."""
        delta = event.angleDelta().y()
        if delta < 0:
            # wheel scrolled down -> next year
            self._on_next()
            event.accept()
        elif delta > 0:
            # wheel scrolled up -> previous year
            self._on_prev()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        """Arrow key navigation for years."""
        if event.key() == Qt.Key_Left:
            self._on_prev()
            event.accept()
        elif event.key() == Qt.Key_Right:
            self._on_next()
            event.accept()
        else:
            super().keyPressEvent(event)

    def _on_next(self):
        if self.year < self._max_year:
            self.year += 1
            self._year_label.setText(str(self.year))
            self._build_months()
