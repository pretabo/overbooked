from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QGridLayout, QFrame, QCalendarWidget, QScrollArea, QComboBox
)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QPalette, QColor
from datetime import datetime, timedelta
from calendar import monthrange
from src.core.game_state import get_game_date, advance_day
from src.ui.event_manager_helper import get_all_events, get_event_by_id, generate_weekly_events_for_year
from src.ui.theme import apply_styles

class CalendarDayCell(QFrame):
    def __init__(self, date, events, on_click, is_today=False):
        super().__init__()
        self.date = date
        self.events = events
        self.on_click = on_click

        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(1)
        self.setFixedSize(130, 100)

        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 6px;
            }
            QFrame:hover {
                background-color: #3a3a3a;
            }
        """ if not is_today else """
            QFrame {
                background-color: #334477;
                border: 2px solid #66ccff;
                border-radius: 6px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(2)
        self.setLayout(layout)

        day_label = QLabel(str(date.day))
        day_label.setAlignment(Qt.AlignRight)
        day_label.setStyleSheet("font-weight: bold; color: #fff; font-size: 14px;")
        layout.addWidget(day_label)

        for _, name in events:
            event_label = QLabel(f"• {name}")
            event_label.setStyleSheet("font-size: 11px; color: #ccc; font-weight: bold;")
            event_label.setWordWrap(True)
            layout.addWidget(event_label)

        layout.addStretch()
        self.mouseReleaseEvent = self.handle_click

    def handle_click(self, event):
        self.on_click(self.date, self.events)

class CalendarViewUI(QWidget):
    def __init__(self, on_back, news_callback=None):
        super().__init__()
        self.on_back = on_back
        self.news_callback = news_callback

        game_date = datetime.strptime(get_game_date(), "%A, %d %B %Y")
        self.current_year = game_date.year
        self.current_month = game_date.month

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        # Month navigation
        nav_layout = QHBoxLayout()
        prev_btn = QPushButton("◀ Prev")
        next_btn = QPushButton("Next ▶")
        prev_btn.clicked.connect(self.prev_month)
        next_btn.clicked.connect(self.next_month)
        nav_layout.addWidget(prev_btn)
        nav_layout.addWidget(next_btn)
        self.main_layout.addLayout(nav_layout)

        # Calendar grid
        self.grid_layout = QGridLayout()
        self.main_layout.addLayout(self.grid_layout)

        # Bottom control buttons
        control_layout = QHBoxLayout()
        list_btn = QPushButton("List All Events")
        list_btn.clicked.connect(self.load_event_list)
        control_layout.addWidget(list_btn)
        self.main_layout.addLayout(control_layout)

        self.render_calendar()

    def render_calendar(self):
        from PyQt5.QtWidgets import QSizePolicy

        # Clear previous grid
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # Month header
        month_name = datetime(self.current_year, self.current_month, 1).strftime("%B %Y")
        self.title_label.setText(f"🗓️ {month_name}")

        # Weekday headers
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days_of_week):
            header = QLabel(day)
            header.setAlignment(Qt.AlignCenter)
            header.setStyleSheet("font-weight: bold; font-size: 14px; color: #ccc;")
            self.grid_layout.addWidget(header, 0, i)

        generate_weekly_events_for_year(self.current_year, self.current_month)

        # Load event data
        events_by_date = {}
        for ev in get_all_events():
            date_str = ev[5]
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                if date_obj not in events_by_date:
                    events_by_date[date_obj] = []
                events_by_date[date_obj].append((ev[0], ev[1]))
            except:
                continue

        # Fill the 7x6 grid
        first_day = datetime(self.current_year, self.current_month, 1)
        _, num_days = monthrange(self.current_year, self.current_month)
        start_day = (first_day.weekday())  # 0 = Monday

        day = 1
        for row in range(1, 7):  # start at row 1 (row 0 is headers)
            for col in range(7):
                if row == 1 and col < start_day:
                    spacer = QLabel("")
                    spacer.setFixedSize(130, 100)
                    self.grid_layout.addWidget(spacer, row, col)
                elif day <= num_days:
                    cell_date = datetime(self.current_year, self.current_month, day).date()
                    events = events_by_date.get(cell_date, [])
                    is_today = cell_date.strftime("%Y-%m-%d") == datetime.strptime(get_game_date(), "%A, %d %B %Y").strftime("%Y-%m-%d")
                    cell = CalendarDayCell(cell_date, events, self.handle_day_click, is_today=is_today)
                    cell.setFixedSize(130, 100)
                    self.grid_layout.addWidget(cell, row, col)
                    day += 1

        # Fix column/row spacing to make calendar layout stable
        for i in range(7):
            self.grid_layout.setColumnStretch(i, 1)
        for j in range(7):  # 6 rows + 1 for headers
            self.grid_layout.setRowStretch(j, 1)

        self.grid_layout.setSpacing(4)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        
    def handle_day_click(self, date, events):
        from src.ui.manage_event_ui_pyqt import ManageEventUI
        from src.ui.event_summary_pyqt import EventSummaryUI

        parent = self.window()  # Top-level window (your MainApp)

        if not events:
            print("🆕 Creating new event")
            editor = ManageEventUI(fixed_date=date.strftime("%Y-%m-%d"), on_back=parent.load_calendar_ui)
            parent.clear_right_panel()
            parent.right_panel.addWidget(editor)
            parent.right_panel.setCurrentWidget(editor)
            return

        event_id, _ = events[0]
        event_data = get_event_by_id(event_id)


        if not event_data:
            print("❌ Failed to load event.")
            return

        if event_data["card"] and len(event_data["results"]) == len(event_data["card"]):
            summary = EventSummaryUI(event_data, on_back=parent.load_calendar_ui)
            parent.clear_right_panel()
            parent.right_panel.addWidget(summary)
            parent.right_panel.setCurrentWidget(summary)
        else:
            editor = ManageEventUI(event_data=event_data, on_back=parent.load_calendar_ui)
            parent.clear_right_panel()
            parent.right_panel.addWidget(editor)
            parent.right_panel.setCurrentWidget(editor)
        print("📝 Results:", len(event_data["results"]), "Card:", len(event_data["card"]))

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.render_calendar()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.render_calendar()

    def load_event_list(self):
        from src.ui.event_list_pyqt import EventsUI
        parent = self.window()  # your MainApp

        screen = EventsUI(on_back=self.on_back, load_screen=parent.set_screen)
        parent.clear_right_panel()
        parent.right_panel.addWidget(screen)
        parent.right_panel.setCurrentWidget(screen)
