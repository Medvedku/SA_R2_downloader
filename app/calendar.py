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

        self.day = day
        self.iso_year, self.iso_week, _ = day.isocalendar()

        self.setFixedSize(36, 28)

        label = QLabel(str(day.day))
        label.setAlignment(Qt.AlignTop | Qt.AlignRight)

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 2, 4, 2)
        layout.addWidget(label)
        self.setLayout(layout)

        # Minimal, semi-transparent dark style for better contrast in dark theme
        # Determine week status and color accordingly
        week_key = (self.iso_year, self.iso_week)
        ws = (week_status or {}).get(week_key, {"local": False, "bucket": False})

        # Color mapping (subtle translucent backgrounds)
        if ws.get("bucket") and ws.get("local"):
            # synced (green)
            bg = "rgba(72,187,120,0.18)"
            border = "rgba(72,187,120,0.25)"
            text = "rgba(255,255,255,0.95)"
        elif ws.get("bucket") and not ws.get("local"):
            # available in bucket (blue)
            bg = "rgba(100,149,237,0.16)"
            border = "rgba(100,149,237,0.22)"
            text = "rgba(255,255,255,0.95)"
        elif ws.get("local") and not ws.get("bucket"):
            # local-only (yellow)
            bg = "rgba(255,193,7,0.12)"
            border = "rgba(255,193,7,0.18)"
            text = "rgba(0,0,0,0.85)"
        else:
            # default minimal
            if day.month != current_month:
                bg = "rgba(255,255,255,0.02)"
                border = "rgba(255,255,255,0.03)"
                text = "rgba(255,255,255,0.45)"
            else:
                bg = "rgba(255,255,255,0.03)"
                border = "rgba(255,255,255,0.05)"
                text = "rgba(255,255,255,0.92)"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                color: {text};
                border: 1px solid {border};
                border-radius: 4px;
            }}
            QFrame QLabel {{ color: {text}; }}
        """)


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

        # default minimal style
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 1px solid rgba(255,255,255,0.04);
                border-radius: 4px;
                color: rgba(255,255,255,0.75);
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

        self._prev_btn = QPushButton("<")
        self._prev_btn.setFixedSize(26, 24)
        self._prev_btn.setToolTip("Previous year")
        self._prev_btn.clicked.connect(self._on_prev)

        self._next_btn = QPushButton(">")
        self._next_btn.setFixedSize(26, 24)
        self._next_btn.setToolTip("Next year")
        self._next_btn.clicked.connect(self._on_next)

        self._year_label = QLabel(str(self.year))
        self._year_label.setAlignment(Qt.AlignCenter)
        self._year_label.setStyleSheet("font-weight: bold; color: rgba(255,255,255,0.95);")

        header.addWidget(self._prev_btn)
        header.addStretch()
        header.addWidget(self._year_label)
        header.addStretch()
        header.addWidget(self._next_btn)

        self._main_layout.addLayout(header)

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
