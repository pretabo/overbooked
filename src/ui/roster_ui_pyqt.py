from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
import sqlite3
from db.utils import db_path
from ui.stats_utils import calculate_high_level_stats_with_grades, GRADE_SCALE
import logging
from PyQt5.QtGui import QColor


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
        columns = ["ID", "Name", "STR", "DEX", "END", "INT", "CHA", "Rep", "Cond"]
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
        """Load wrestler data into the table"""
        self.table.setRowCount(0)  # Clear table
        
        try:
            # Connect to the database
            conn = sqlite3.connect(db_path("wrestlers.db"))
            cursor = conn.cursor()
            
            # Get all wrestlers
            cursor.execute("""
                SELECT id, name, reputation, condition
                FROM wrestlers
                ORDER BY name
            """)
            
            rows = cursor.fetchall()
            
            # If no rows, use dummy data for development
            if not rows:
                rows = [
                    (1, "The Rock", 95, "Healthy"),
                    (2, "Stone Cold", 90, "Healthy"),
                    (3, "Undertaker", 85, "Minor Injury"),
                    (4, "John Cena", 88, "Healthy"),
                    (5, "Bret Hart", 92, "Healthy"),
                    (6, "Shawn Michaels", 91, "Healthy"),
                    (7, "Triple H", 87, "Healthy"),
                    (8, "Randy Savage", 86, "Minor Injury"),
                    (9, "Ric Flair", 89, "Healthy"),
                    (10, "Hulk Hogan", 84, "Healthy")
                ]
            
            self.table.setRowCount(len(rows))
            
            # Process each wrestler
            for i, row in enumerate(rows):
                wrestler_id, name, reputation, condition = row
                
                # For development, use dummy attributes if database query fails
                try:
                    cursor.execute("""
                        SELECT strength, dexterity, endurance, intelligence, charisma
                        FROM wrestler_attributes
                        WHERE wrestler_id = ?
                    """, (wrestler_id,))
                    
                    attr_row = cursor.fetchone()
                    if not attr_row:
                        # Use dummy data if no attributes found
                        attr_row = (80, 75, 85, 70, 90)  # Dummy values
                except:
                    # Use dummy data if query fails
                    attr_row = (80, 75, 85, 70, 90)  # Dummy values
                    
                attributes = {
                    "strength": attr_row[0],
                    "dexterity": attr_row[1],
                    "endurance": attr_row[2],
                    "intelligence": attr_row[3],
                    "charisma": attr_row[4]
                }
                
                # Scale attributes to 0-20 range
                for attr in attributes:
                    attributes[attr] = int(attributes[attr] / 5)  # Scale from 0-100 to 0-20
                
                # Scale reputation to 0-20 range
                reputation = int(reputation / 5)  # Scale from 0-100 to 0-20
                
                # Calculate grades for each attribute
                grades = calculate_high_level_stats_with_grades(attributes)
                
                # Add wrestler to table
                self.table.setItem(i, 0, QTableWidgetItem(str(wrestler_id)))
                self.table.setItem(i, 1, QTableWidgetItem(name))
                
                # Add attributes with color coding
                self.table.setItem(i, 2, self.create_stat_item(grades["strength"]))
                self.table.setItem(i, 3, self.create_stat_item(grades["dexterity"]))
                self.table.setItem(i, 4, self.create_stat_item(grades["endurance"]))
                self.table.setItem(i, 5, self.create_stat_item(grades["intelligence"]))
                self.table.setItem(i, 6, self.create_stat_item(grades["charisma"]))
                
                # Add reputation and condition
                reputation_item = QTableWidgetItem(str(reputation))
                reputation_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 7, reputation_item)
                
                condition_item = QTableWidgetItem(condition)
                condition_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 8, condition_item)
            
            conn.close()
            
            # Resize columns to fit content
            self.table.resizeColumnsToContents()
            
        except Exception as e:
            logging.error(f"Error loading wrestlers: {e}")
            print(f"Error loading wrestlers: {e}")  # DEBUG
            
            # Use dummy data for development
            dummy_data = [
                (1, "The Rock", 19, "Healthy"),
                (2, "Stone Cold", 18, "Healthy"),
                (3, "Undertaker", 17, "Minor Injury"),
                (4, "John Cena", 18, "Healthy"),
                (5, "Bret Hart", 18, "Healthy"),
                (6, "Shawn Michaels", 18, "Healthy"),
                (7, "Triple H", 17, "Healthy"),
                (8, "Randy Savage", 17, "Minor Injury"),
                (9, "Ric Flair", 18, "Healthy"),
                (10, "Hulk Hogan", 17, "Healthy")
            ]
            
            self.table.setRowCount(len(dummy_data))
            
            for i, (wrestler_id, name, reputation, condition) in enumerate(dummy_data):
                # Create dummy attributes with random values between 13-20
                import random
                attributes = {
                    "strength": {"value": random.randint(13, 20), "grade": "A", "colour": "#26A55B"},
                    "dexterity": {"value": random.randint(13, 20), "grade": "A", "colour": "#26A55B"},
                    "endurance": {"value": random.randint(13, 20), "grade": "A", "colour": "#26A55B"},
                    "intelligence": {"value": random.randint(13, 20), "grade": "A", "colour": "#26A55B"},
                    "charisma": {"value": random.randint(13, 20), "grade": "A", "colour": "#26A55B"},
                }
                
                # Add wrestler to table
                self.table.setItem(i, 0, QTableWidgetItem(str(wrestler_id)))
                self.table.setItem(i, 1, QTableWidgetItem(name))
                
                # Add attributes with color coding
                self.table.setItem(i, 2, self.create_stat_item(attributes["strength"]))
                self.table.setItem(i, 3, self.create_stat_item(attributes["dexterity"]))
                self.table.setItem(i, 4, self.create_stat_item(attributes["endurance"]))
                self.table.setItem(i, 5, self.create_stat_item(attributes["intelligence"]))
                self.table.setItem(i, 6, self.create_stat_item(attributes["charisma"]))
                
                # Add reputation and condition
                reputation_item = QTableWidgetItem(str(reputation))
                reputation_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 7, reputation_item)
                
                condition_item = QTableWidgetItem(condition)
                condition_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 8, condition_item)
            
            # Resize columns to fit content
            self.table.resizeColumnsToContents()

    def handle_double_click(self, row, column):
        item = self.table.item(row, 0)  # hidden ID column
        if item and self.on_view_profile:
            wrestler_id = int(item.text())
            self.on_view_profile(wrestler_id)

    def create_stat_item(self, stat_grade):
        """Create a table item for a stat with proper formatting"""
        item = QTableWidgetItem(str(stat_grade["value"]))
        item.setTextAlignment(Qt.AlignCenter)
        
        # Set color based on grade
        color = next((c for t, _, c in GRADE_SCALE if stat_grade["value"] >= t), "#888")
        item.setBackground(QColor(color))
        
        return item
