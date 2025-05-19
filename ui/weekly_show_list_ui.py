from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
from ui.theme import apply_styles
from db.utils import db_path
import sqlite3
from ui.weekly_show_settings_ui import WeeklyShowSettingsUI


class WeeklyShowListUI(QWidget):
    def __init__(self, on_back=None):
        super().__init__()
        self.on_back = on_back

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        title = QLabel("📺 All Weekly Shows")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #eee;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Show Name", "Day", "Cadence", "Start Date", "", ""])
        self.table.setStyleSheet("font-family: Fira Code; font-size: 12pt; color: #ccc;")
        layout.addWidget(self.table)

        self.load_shows()

        back_btn = QPushButton("Back")
        apply_styles(back_btn, "button_flat")
        back_btn.clicked.connect(self.on_back)
        layout.addWidget(back_btn, alignment=Qt.AlignRight)

    def load_shows(self):
        conn = sqlite3.connect(db_path("events.db"))
        cursor = conn.cursor()
        cursor.execute("SELECT name, day_of_week, cadence_weeks, start_date FROM weekly_shows ORDER BY day_of_week")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, (name, day, cadence, start_date) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(name))
            self.table.setItem(i, 1, QTableWidgetItem(day))
            self.table.setItem(i, 2, QTableWidgetItem(str(cadence)))
            self.table.setItem(i, 3, QTableWidgetItem(start_date))

            delete_btn = QPushButton("Delete")
            apply_styles(delete_btn, "button_flat")
            delete_btn.setFixedHeight(28)
            delete_btn.clicked.connect(lambda _, n=name, d=day: self.delete_show(n, d))
            self.table.setCellWidget(i, 4, delete_btn)

            edit_btn = QPushButton("Edit")
            apply_styles(edit_btn, "button_yellow")
            edit_btn.setFixedHeight(28)
            edit_btn.clicked.connect(lambda _, n=name, d=day, c=cadence, s=start_date: self.edit_show(n, d, c, s))
            self.table.setCellWidget(i, 5, edit_btn)

    def delete_show(self, name, day):
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the weekly show:\n{name} ({day})?\n\nAll future events with the same name will also be deleted.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        conn = sqlite3.connect(db_path("events.db"))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM weekly_shows WHERE name = ? AND day_of_week = ?", (name, day))

        # Delete future scheduled events with this name
        cursor.execute("DELETE FROM events WHERE name = ? AND date >= date('now')", (name,))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Deleted", f"{name} ({day}) was removed.")
        self.load_shows()

    def edit_show(self, name, day, cadence, start_date):
        parent = self.window()
        screen = WeeklyShowSettingsUI(
            on_back=self.on_back,
            initial_data={
                "name": name,
                "day": day,
                "cadence": cadence,
                "start_date": start_date
            }
        )
        parent.clear_right_panel()
        parent.right_panel.addWidget(screen)
        parent.right_panel.setCurrentWidget(screen)
