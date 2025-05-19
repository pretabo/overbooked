from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QComboBox, QDateEdit, QSpinBox, QMessageBox
)
from PyQt5.QtCore import Qt, QDate, QTimer
from ui.theme import apply_styles
from db.utils import db_path
import sqlite3
from game_state import get_game_date
from datetime import datetime


class WeeklyShowSettingsUI(QWidget):
    def __init__(self, on_back=None, initial_data=None):
        super().__init__()
        self.on_back = on_back

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(25)

        title = QLabel("Manage Weekly Show")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #eee;")
        layout.addWidget(title)

        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Enter show name")
        self.name_field.setFixedWidth(300)

        self.day_dropdown = QComboBox()
        self.day_dropdown.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        self.day_dropdown.setFixedWidth(300)

        self.cadence_input = QSpinBox()
        self.cadence_input.setRange(1, 6)
        self.cadence_input.setValue(1)
        self.cadence_input.setFixedWidth(300)

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.fromString(get_game_date(), "dddd, dd MMMM yyyy"))
        self.start_date.setCalendarPopup(True)
        self.start_date.setFixedWidth(300)
        
        self.name_field.textChanged.connect(self.update_preview)
        self.day_dropdown.currentIndexChanged.connect(self.update_preview)
        self.cadence_input.valueChanged.connect(self.update_preview)
        self.start_date.dateChanged.connect(self.update_preview)

        if initial_data:
            self.name_field.setText(initial_data.get("name", ""))
            day_index = self.day_dropdown.findText(initial_data.get("day", "Monday"))
            self.day_dropdown.setCurrentIndex(day_index)
            self.cadence_input.setValue(initial_data.get("cadence", 1))
            start = QDate.fromString(initial_data.get("start_date", get_game_date()), "yyyy-MM-dd")
            self.start_date.setDate(start)


        # Field layout
        layout.addWidget(QLabel("Show Name:"))
        layout.addWidget(self.name_field)

        layout.addWidget(QLabel("Air Day:"))
        layout.addWidget(self.day_dropdown)

        layout.addWidget(QLabel("Cadence (weeks):"))
        layout.addWidget(self.cadence_input)

        layout.addWidget(QLabel("Start Date:"))
        layout.addWidget(self.start_date)

        self.preview_label = QLabel("")
        self.preview_label.setStyleSheet("font-family: Fira Code; font-size: 10pt; color: #aaa;")
        layout.addWidget(self.preview_label)

        self.update_preview()  # Show initial preview
        
        # Buttons
        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save Show")
        back_btn = QPushButton("Back")
        apply_styles(save_btn, "button_blue")
        apply_styles(back_btn, "button_flat")
        save_btn.setFixedSize(150, 36)
        back_btn.setFixedSize(150, 36)

        auto_add_btn = QPushButton("Generate Events")
        apply_styles(auto_add_btn, "button_yellow")
        auto_add_btn.setFixedSize(150, 36)
        
        list_btn = QPushButton("View All Weekly Shows")
        apply_styles(list_btn, "button_flat")



        auto_add_btn.clicked.connect(self.generate_weekly_show_events)
        save_btn.clicked.connect(self.save_show)
        back_btn.clicked.connect(self.on_back)
        list_btn.clicked.connect(self.load_weekly_show_list)

        btn_row.addWidget(save_btn)
        btn_row.addWidget(back_btn)
        btn_row.addWidget(auto_add_btn)
        btn_row.addWidget(list_btn)
        layout.addLayout(btn_row)

    def save_show(self):
        name = self.name_field.text().strip()
        day = self.day_dropdown.currentText()
        cadence = self.cadence_input.value()
        start = self.start_date.date().toString("yyyy-MM-dd")

        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a show name.")
            return

        conn = sqlite3.connect(db_path("events.db"))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO weekly_shows (name, day_of_week, cadence_weeks, start_date)
            VALUES (?, ?, ?, ?)
        """, (name, day, cadence, start))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Saved", f"✅ {name} has been added as a weekly show.")

        if self.on_back:
            QTimer.singleShot(0, self.on_back)

    def generate_weekly_show_events(self):
        from ui.event_manager_helper import generate_weekly_events_for_year
        from datetime import datetime

        name = self.name_field.text().strip()
        day = self.day_dropdown.currentText()
        cadence = self.cadence_input.value()
        start = self.start_date.date().toString("yyyy-MM-dd")

        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a show name first.")
            return

        # Save to the weekly_shows table if not already present
        conn = sqlite3.connect(db_path("events.db"))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM weekly_shows
            WHERE name = ? AND day_of_week = ?
        """, (name, day))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO weekly_shows (name, day_of_week, cadence_weeks, start_date)
                VALUES (?, ?, ?, ?)
            """, (name, day, cadence, start))
            conn.commit()
            QMessageBox.information(self, "Show Added", f"✅ {name} was added as a weekly show.")

        conn.close()

        from game_state import get_game_date
        current = datetime.strptime(get_game_date(), "%A, %d %B %Y")
        generate_weekly_events_for_year(current.year, current.month)

        QMessageBox.information(self, "Events Generated", f"✅ Events for {name} were generated for {current.strftime('%B %Y')}.")

        if self.on_back:
            QTimer.singleShot(0, self.on_back)

    def update_preview(self):
        from datetime import datetime, timedelta

        name = self.name_field.text().strip() or "[Show Name]"
        day = self.day_dropdown.currentText()
        cadence = self.cadence_input.value()
        start = self.start_date.date().toPyDate()

        day_lookup = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
            "Friday": 4, "Saturday": 5, "Sunday": 6
        }

        # Find the first occurrence of the selected day on or after start date
        start_day = day_lookup[day]
        current = start
        while current.weekday() != start_day:
            current += timedelta(days=1)

        dates = []
        for _ in range(3):
            dates.append(current.strftime("%d %b %Y"))
            current += timedelta(weeks=cadence)

        self.preview_label.setText(f"Next episodes of {name}:\n" + "\n".join(dates))

    def load_weekly_show_list(self):
        from ui.weekly_show_list_ui import WeeklyShowListUI
        parent = self.window()
        screen = WeeklyShowListUI(on_back=self.on_back)
        parent.clear_right_panel()
        parent.right_panel.addWidget(screen)
        parent.right_panel.setCurrentWidget(screen)
