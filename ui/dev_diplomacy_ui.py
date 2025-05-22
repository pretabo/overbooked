from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QTextEdit, QHBoxLayout
from PyQt5.QtCore import Qt
from ui.theme import apply_styles
from match_engine import get_all_wrestlers
from storyline.storyline_manager import StorylineManager
import random
import sqlite3

class DevDiplomacyUI(QWidget):
    def __init__(self, diplomacy_system, on_back):
        super().__init__()
        self.diplomacy_system = diplomacy_system
        self.on_back = on_back
        self.storyline_manager = StorylineManager()
        self.recent_events = []

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        title = QLabel("Developer: Diplomacy Manager")
        title.setAlignment(Qt.AlignCenter)
        apply_styles(title, "label_header")
        layout.addWidget(title)

        # Wrestler dropdowns
        wrestlers = get_all_wrestlers()
        self.wrestler_names = [w[1] for w in wrestlers]
        self.wrestler_ids = {w[1]: w[0] for w in wrestlers}

        row = QHBoxLayout()
        self.wrestler_a_dropdown = QComboBox()
        self.wrestler_a_dropdown.addItems(["(None)"] + self.wrestler_names)
        row.addWidget(QLabel("Wrestler A:"))
        row.addWidget(self.wrestler_a_dropdown)
        self.wrestler_b_dropdown = QComboBox()
        self.wrestler_b_dropdown.addItems(["(None)"] + self.wrestler_names)
        row.addWidget(QLabel("Wrestler B:"))
        row.addWidget(self.wrestler_b_dropdown)
        layout.addLayout(row)

        # Event type dropdown
        self.event_type_dropdown = QComboBox()
        self.event_type_dropdown.addItems([
            "Betrayal",
            "Alliance",
            "Backstage Fight",
            "Mentorship",
            "Romantic Angle",
            "Public Callout",
            "Injury/Return",
            "Championship Challenge",
            "Simulate Match",
            "Random Off-Screen Event"
        ])
        layout.addWidget(QLabel("Event Type:"))
        layout.addWidget(self.event_type_dropdown)

        # Trigger event button
        trigger_btn = QPushButton("Trigger Event")
        apply_styles(trigger_btn, "button_blue")
        trigger_btn.clicked.connect(self.trigger_event)
        layout.addWidget(trigger_btn)

        # Relationship boost/hurt/decay
        boost_btn = QPushButton("Boost Relationship (+20)")
        apply_styles(boost_btn, "button_blue")
        boost_btn.clicked.connect(self.boost_relationship)
        layout.addWidget(boost_btn)

        hurt_btn = QPushButton("Hurt Relationship (-20)")
        apply_styles(hurt_btn, "button_red")
        hurt_btn.clicked.connect(self.hurt_relationship)
        layout.addWidget(hurt_btn)

        decay_btn = QPushButton("Decay All Relationships")
        apply_styles(decay_btn, "button_nav")
        decay_btn.clicked.connect(self.decay_relationships)
        layout.addWidget(decay_btn)

        # Remove all storylines button
        remove_all_btn = QPushButton("Remove All Storylines")
        apply_styles(remove_all_btn, "button_red")
        remove_all_btn.clicked.connect(self.remove_all_storylines)
        layout.addWidget(remove_all_btn)

        # Recent events log
        layout.addWidget(QLabel("Recent Events:"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(120)
        layout.addWidget(self.log_box)

        # Back Button
        back_btn = QPushButton("Back to Main Menu")
        apply_styles(back_btn, "button_nav")
        back_btn.clicked.connect(self.on_back)
        layout.addWidget(back_btn)

    def log_event(self, text):
        self.recent_events.append(text)
        if len(self.recent_events) > 10:
            self.recent_events = self.recent_events[-10:]
        self.log_box.setPlainText("\n".join(self.recent_events[::-1]))

    def trigger_event(self):
        a_name = self.wrestler_a_dropdown.currentText()
        b_name = self.wrestler_b_dropdown.currentText()
        a_id = self.wrestler_ids.get(a_name)
        b_id = self.wrestler_ids.get(b_name)
        event_type = self.event_type_dropdown.currentText()
        details = f"Triggered via Diplomacy Manager."
        storyline_id = None

        if event_type == "Simulate Match":
            if a_id and b_id:
                # Simulate a match result (random winner, random rating)
                winner_id = random.choice([a_id, b_id])
                match_result = {
                    "winner_id": winner_id,
                    "match_rating": random.randint(60, 100)
                }
                storyline_ids = self.storyline_manager.generate_potential_storylines_from_match(a_id, b_id, match_result)
                self.log_event(f"Simulated match: {a_name} vs {b_name} (Winner: {a_name if winner_id == a_id else b_name})")
                if storyline_ids:
                    self.log_event(f"Potential storyline(s) generated from match.")
            else:
                self.log_event("Select two wrestlers for a match.")
            return
        elif event_type == "Random Off-Screen Event":
            # Pick a random wrestler or pair
            if random.random() < 0.5 and len(self.wrestler_names) >= 2:
                a_name, b_name = random.sample(self.wrestler_names, 2)
                a_id, b_id = self.wrestler_ids[a_name], self.wrestler_ids[b_name]
            else:
                a_name = random.choice(self.wrestler_names)
                a_id = self.wrestler_ids[a_name]
                b_name = None
                b_id = None
            event_types = [
                "Scandal", "Praise", "Suspension", "Media Appearance", "Charity Work", "Backstage Prank"
            ]
            chosen_type = random.choice(event_types)
            storyline_id = self.storyline_manager.add_potential_storyline(
                a_id, b_id or a_id, chosen_type, f"Random off-screen event: {chosen_type}")
            self.log_event(f"Random off-screen event: {a_name}{' & ' + b_name if b_name else ''} - {chosen_type}")
        else:
            # Relationship/angle event
            if a_id and b_id:
                storyline_id = self.storyline_manager.add_potential_storyline(
                    a_id, b_id, event_type, details)
                self.log_event(f"{event_type} between {a_name} and {b_name}.")
            else:
                self.log_event("Select two wrestlers for this event.")

    def boost_relationship(self):
        a_name = self.wrestler_a_dropdown.currentText()
        b_name = self.wrestler_b_dropdown.currentText()
        if a_name in self.wrestler_ids and b_name in self.wrestler_ids:
            a_id = self.wrestler_ids[a_name]
            b_id = self.wrestler_ids[b_name]
            self.diplomacy_system.adjust_relationship(a_id, b_id, "Dev Boost", +20)
            self.log_event(f"Boosted relationship: {a_name} ↔ {b_name}")

    def hurt_relationship(self):
        a_name = self.wrestler_a_dropdown.currentText()
        b_name = self.wrestler_b_dropdown.currentText()
        if a_name in self.wrestler_ids and b_name in self.wrestler_ids:
            a_id = self.wrestler_ids[a_name]
            b_id = self.wrestler_ids[b_name]
            self.diplomacy_system.adjust_relationship(a_id, b_id, "Dev Hurt", -20)
            self.log_event(f"Hurt relationship: {a_name} ↔ {b_name}")

    def decay_relationships(self):
        self.diplomacy_system.tick_relationships()
        self.log_event("All relationships decayed.")

    def remove_all_storylines(self):
        # Remove all potential and active storylines
        with sqlite3.connect(self.storyline_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM potential_storylines")
            cursor.execute("DELETE FROM active_storylines")
            cursor.execute("DELETE FROM storyline_interactions")
            conn.commit()
        self.log_event("All storylines removed.")
