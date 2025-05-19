from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
import sqlite3
from db.utils import db_path
from ui.stats_utils import calculate_high_level_stats_with_grades, GRADE_SCALE


class RosterUI(QWidget):
    def __init__(self, on_view_profile=None):
        super().__init__()

        self.on_view_profile = on_view_profile
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        title = QLabel("Wrestler Roster")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18pt; font-weight: bold; font-family: Fira Code; color: #fff;")
        self.layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setSortingEnabled(True)  # ✅ Enable column sorting
        self.layout.addWidget(self.table)

        self.setup_table()
        self.load_data()

        self.table.cellDoubleClicked.connect(self.handle_double_click)

    def setup_table(self):
        columns = ["ID", "Name", "STR", "DEX", "END", "INT", "CHA", "Reputation", "Condition"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setColumnHidden(0, True)  # Hide ID column
        self.table.verticalHeader().setVisible(False)


        # Header style
        header = self.table.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #333;
                color: #fff;
                font-weight: bold;
                font-size: 11pt;
                padding: 6px;
                font-family: Fira Code;
            }
        """)

        self.table.setStyleSheet("""
            QTableWidget {
                font-family: Fira Code;
                font-size: 10pt;
                color: #ddd;
                gridline-color: #555;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)

        self.table.setColumnWidth(1, 180)  # Name column width

    def load_data(self):
        conn = sqlite3.connect(db_path("wrestlers.db"))
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, reputation, condition FROM wrestlers")
        wrestler_rows = cursor.fetchall()
        self.table.setRowCount(len(wrestler_rows))

        for row_idx, (wrestler_id, name, reputation, condition) in enumerate(wrestler_rows):
            # Fetch attributes
            cursor.execute("SELECT * FROM wrestler_attributes WHERE wrestler_id = ?", (wrestler_id,))
            attr_row = cursor.fetchone()
            if not attr_row:
                continue
            attr_names = [desc[0] for desc in cursor.description][1:]
            stats_dict = dict(zip(attr_names, attr_row[1:]))

            # Calculate high-level stat averages
            grades = calculate_high_level_stats_with_grades(stats_dict)

            # Columns: ID, Name, STR, DEX, END, INT, CHA, Reputation, Condition
            values = [
                wrestler_id,
                name,
                grades["strength"]["value"],
                grades["dexterity"]["value"],
                grades["endurance"]["value"],
                grades["intelligence"]["value"],
                grades["charisma"]["value"],
                reputation,
                condition
            ]

            for col_idx, val in enumerate(values):
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, val)
                item.setTextAlignment(Qt.AlignCenter)
                item.setFont(QtGui.QFont("Fira Code", 16, QtGui.QFont.Bold))
                item.setForeground(QtGui.QColor("#000"))
                item.setBackground(QtGui.QColor("#42494a"))
                if col_idx == 0:
                    item.setData(Qt.UserRole, wrestler_id)

                # Colour stat cells by grade scale (columns 2 to 6)
                if 2 <= col_idx <= 6:
                    colour = next((c for t, _, c in GRADE_SCALE if int(val) >= t), "#888")
                    item.setBackground(QtGui.QColor(colour))

                self.table.setItem(row_idx, col_idx, item)

        conn.close()

    def handle_double_click(self, row, column):
        item = self.table.item(row, 0)  # hidden ID column
        if item and self.on_view_profile:
            wrestler_id = int(item.text())
            self.on_view_profile(wrestler_id)
