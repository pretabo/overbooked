from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout,
    QPushButton, QComboBox, QFormLayout, QGroupBox, QScrollArea,
    QMessageBox
)
import sqlite3
from db.utils import db_path
from match_engine import get_all_wrestlers


class WrestlerDatabaseUI(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.signature_moves = []

        title = QLabel("🧠 Wrestler Creator")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        self.layout.addWidget(title)

        self.form = QFormLayout()

        # Wrestler core attributes
        self.fields = {}
        for label in ["Name", "Strength", "Dexterity", "Endurance", "Intelligence",
                      "Charisma", "Reputation", "Condition"]:
            input_field = QLineEdit()
            self.fields[label.lower()] = input_field
            self.form.addRow(label + ":", input_field)

        # Finisher
        self.finisher_name = QLineEdit()
        self.finisher_style = QComboBox()
        self.finisher_style.addItems(["strike", "slam", "aerial", "submission"])
        self.finisher_damage = QLineEdit()

        self.form.addRow("Finisher Name:", self.finisher_name)
        self.form.addRow("Finisher Style:", self.finisher_style)
        self.form.addRow("Finisher Damage:", self.finisher_damage)

        self.layout.addLayout(self.form)

        # Signature Moves Area
        self.move_container = QVBoxLayout()
        self.move_box = QWidget()
        self.move_box.setLayout(self.move_container)

        move_group = QGroupBox("Signature Moves")
        move_layout = QVBoxLayout()
        move_layout.addWidget(self.move_box)

        self.add_signature_move_row()  # Add first row
        add_btn = QPushButton("➕ Add Another Signature Move")
        add_btn.clicked.connect(self.add_signature_move_row)
        move_layout.addWidget(add_btn)

        move_group.setLayout(move_layout)
        self.layout.addWidget(move_group)

        # Save button
        save_btn = QPushButton("💾 Save Wrestler")
        save_btn.clicked.connect(self.save_wrestler)
        self.layout.addWidget(save_btn)

    def add_signature_move_row(self):
        row_layout = QHBoxLayout()
        name = QLineEdit()
        move_type = QComboBox()
        move_type.addItems(["strike", "slam", "aerial", "submission"])
        damage = QLineEdit()
        difficulty = QLineEdit()

        row_layout.addWidget(name)
        row_layout.addWidget(move_type)
        row_layout.addWidget(damage)
        row_layout.addWidget(difficulty)

        self.move_container.addLayout(row_layout)
        self.signature_moves.append((name, move_type, damage, difficulty))

    def save_wrestler(self):
        try:
            data = {k: int(self.fields[k].text()) if k != "name" else self.fields[k].text().strip()
                    for k in self.fields}
            finisher_name = self.finisher_name.text().strip()
            finisher_style = self.finisher_style.currentText()
            finisher_damage = int(self.finisher_damage.text())

            # Connect to DB
            conn = sqlite3.connect(db_path("wrestlers.db"))
            conn.execute(f"ATTACH DATABASE '{db_path('finishers.db')}' AS fdb")
            cursor = conn.cursor()

            # Insert or get finisher
            cursor.execute("SELECT id FROM fdb.finishers WHERE name = ?", (finisher_name,))
            row = cursor.fetchone()
            if row:
                finisher_id = row[0]
            else:
                cursor.execute("INSERT INTO fdb.finishers (name, style, damage) VALUES (?, ?, ?)",
                               (finisher_name, finisher_style, finisher_damage))
                finisher_id = cursor.lastrowid

            # Insert wrestler
            cursor.execute("""
                INSERT INTO wrestlers (
                    name, strength, dexterity, endurance, intelligence,
                    charisma, reputation, condition, finisher_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["name"], data["strength"], data["dexterity"], data["endurance"],
                data["intelligence"], data["charisma"], data["reputation"], data["condition"],
                finisher_id
            ))
            wrestler_id = cursor.lastrowid

            # Signature moves
            for name_field, type_box, dmg_field, diff_field in self.signature_moves:
                move_name = name_field.text().strip()
                move_type = type_box.currentText()
                move_damage = int(dmg_field.text())
                move_difficulty = int(diff_field.text())

                cursor.execute("""
                    SELECT id FROM signature_moves WHERE name = ? AND type = ? AND damage = ? AND difficulty = ?
                """, (move_name, move_type, move_damage, move_difficulty))
                row = cursor.fetchone()
                if row:
                    move_id = row[0]
                else:
                    cursor.execute("""
                        INSERT INTO signature_moves (name, type, damage, difficulty)
                        VALUES (?, ?, ?, ?)
                    """, (move_name, move_type, move_damage, move_difficulty))
                    move_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO wrestler_signature_moves (wrestler_id, signature_move_id)
                    VALUES (?, ?)
                """, (wrestler_id, move_id))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", f"✅ Wrestler '{data['name']}' added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ {str(e)}")
