from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QGridLayout, QFrame, QSizePolicy, QTabWidget  # <-- ADD QTabWidget here
)
from PyQt5.QtCore import Qt
import sqlite3
from db.utils import db_path
from ui.theme import apply_styles, BONE
from ui.stats_utils import calculate_high_level_stats_with_grades
from ui.stats_utils import GRADE_SCALE
from src.core.game_state import consume_relationships_refresh_flag
from src.ui.wrestler_merchandise_ui import WrestlerMerchandiseUI


class WrestlerProfileUI(QWidget):
    def __init__(self, wrestler_id, on_back, diplomacy_system=None):
        super().__init__()
        self.wrestler_id = wrestler_id
        self.on_back = on_back
        self.diplomacy_system = diplomacy_system
        self.wrestler_name = ""  # Will be set in load_profile

        main_layout = QVBoxLayout(self)

        # 🔥 First create tabs and pages
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.profile_tab = QWidget()
        self.relationships_tab = QWidget()
        self.merchandise_tab = QWidget()

        self.tabs.addTab(self.profile_tab, "Profile")
        self.tabs.addTab(self.relationships_tab, "Relationships")
        self.tabs.addTab(self.merchandise_tab, "Merchandise")

        # 🔥 Now build layout INSIDE profile tab
        layout = QVBoxLayout(self.profile_tab)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        self.build_relationships_tab()

        # Title
        self.title = QLabel("Wrestler Profile")
        self.title.setAlignment(Qt.AlignCenter)
        apply_styles(self.title, "label_header")
        layout.addWidget(self.title)

        # Meta Info Section
        self.meta_section = QLabel()
        layout.addWidget(self.meta_section)

        # Main content area
        self.content_row = QHBoxLayout()
        layout.addLayout(self.content_row)

        self.parent_stat_col = QVBoxLayout()
        self.parent_stat_col.setSpacing(10)
        self.content_row.addLayout(self.parent_stat_col, 1)

        self.detailed_col = QHBoxLayout()
        self.detailed_col.setSpacing(10)
        self.content_row.addLayout(self.detailed_col, 4)

        # Back button
        back_btn = QPushButton("Back to Roster")
        apply_styles(back_btn, "button_nav")
        back_btn.clicked.connect(self.on_back)
        layout.addWidget(back_btn)

        self.load_profile()

    def load_profile(self):
        conn = sqlite3.connect(db_path("wrestlers.db"))
        conn.execute(f"ATTACH DATABASE '{db_path('finishers.db')}' AS fdb")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT w.name, w.reputation, w.condition, f.name AS finisher_name, f.style, f.damage,
                   w.backstage_influence, w.company_standing, w.industry_respect,
                   w.fan_base_strength, w.media_presence
            FROM wrestlers w
            JOIN finishers f ON f.id = w.finisher_id
            WHERE w.id = ?
        """, (self.wrestler_id,))
        row = cursor.fetchone()

        if not row:
            self.meta_section.setText("Wrestler not found.")
            conn.close()
            return

        name, rep, cond, fin_name, fin_style, fin_dmg, backstage, company, industry, fan_base, media = row
        self.wrestler_name = name  # Store the wrestler's name for use in other tabs
        
        # Recalculate reputation as average of new stats
        rep = (backstage + company + industry + fan_base + media) // 5

        cursor.execute("SELECT * FROM wrestler_attributes WHERE wrestler_id = ?", (self.wrestler_id,))
        attr_row = cursor.fetchone()
        if not attr_row:
            self.meta_section.setText("No attributes found.")
            conn.close()
            return

        stat_names = [col[0] for col in cursor.description][1:]
        stat_values = attr_row[1:]
        stats = dict(zip(stat_names, stat_values))

        if consume_relationships_refresh_flag():
            self.rebuild_relationships_tab()


        conn.close()

        # Meta Info
        self.meta_section.setText(f"""\
Name:         {name}
Condition:    {cond}
Reputation:   {rep}
Finisher:     {fin_name or 'N/A'} ({fin_style or '-'}) — {fin_dmg or '-'} dmg

Reputation Stats:
• Backstage Influence: {backstage}
• Company Standing:    {company}
• Industry Respect:    {industry}
• Fan Base Strength:   {fan_base}
• Media Presence:      {media}
""")
        self.meta_section.setStyleSheet("font-family: Fira Code; font-size: 16pt; color: #e0e0e0;")

        # Parent Stats Column (Left)
        grades = calculate_high_level_stats_with_grades(stats)
        STAR_MAP = {
            "S": 5,
            "A": 5,
            "B": 4,
            "C": 3,
            "D": 2,
            "F": 1
        }

        FILLED_STAR = "⭐"
        EMPTY_STAR = "-"

        LABEL_MAP = {
            "strength": "STR",
            "dexterity": "DEX",
            "endurance": "END",
            "intelligence": "INT",
            "charisma": "CHA"
        }

        for key in ["strength", "dexterity", "endurance", "intelligence", "charisma"]:
            data = grades[key]
            stars = STAR_MAP.get(data["grade"], 1)
            label_text = f"{LABEL_MAP[key]:<3}: {FILLED_STAR * stars}{EMPTY_STAR * (5 - stars)}"

            label = QLabel(label_text)
            label.setStyleSheet(f"""
                font-family: Fira Code;
                font-size: 16pt;
                color: {data['colour']};
            """)
            self.parent_stat_col.addWidget(label)

        # Detailed Stat Columns (Right)
        self.build_stat_columns(stats)
        
        # Build merchandise tab
        self.build_merchandise_tab()

    def build_stat_columns(self, stats):
        groups = {
            "Physical": ["powerlifting", "grapple_control", "grip_strength", "agility", "balance", "flexibility", "recovery_rate", "conditioning"],
            "In-Ring": ["chain_wrestling", "mat_transitions", "submission_technique", "strike_accuracy", "brawling_technique", "aerial_precision", "counter_timing", "pressure_handling"],
            "Charisma": ["promo_delivery", "fan_engagement", "entrance_presence", "presence_under_fire", "confidence"],
            "Mental": ["focus", "resilience", "adaptability", "risk_assessment", "loyalty", "political_instinct", "determination"]
        }

        for group_name, keys in groups.items():
            frame = QFrame()
            frame.setStyleSheet("background-color: #222; border: 1px solid #444; padding: 8px;")
            layout = QVBoxLayout(frame)
            layout.setAlignment(Qt.AlignTop)
            header = QLabel(group_name)
            header.setAlignment(Qt.AlignCenter)
            header.setFixedSize(200, 40)  # Match width of all stat boxes
            header.setStyleSheet("""
                font-family: Fira Code;
                font-size: 13pt;
                font-weight: bold;
                color: #ffffff;
                background-color: #333;
                border: 1px solid #444;
                border-radius: 4px;
            """)
            layout.addWidget(header, alignment=Qt.AlignCenter)

            for key in keys:
                h = QHBoxLayout()
                h.setContentsMargins(0, 0, 0, 0)
                h.setSpacing(4)

                label = QLabel(f"{key.replace('_', ' ').title():<22}")
                label.setStyleSheet("color: #ccc; font-family: Fira Code; font-size: 10pt;")
                label.setFixedWidth(160)  # ensure all labels align

                def get_stat_colour(value):
                    for threshold, _, colour in GRADE_SCALE:
                        if value >= threshold:
                            return colour
                    return "#888888"

                stat_value = stats.get(key, "-")
                colour = get_stat_colour(stat_value) if isinstance(stat_value, int) else "#888888"

                value = QLabel(str(stat_value))
                value.setAlignment(Qt.AlignCenter)
                value.setFixedSize(40, 30)
                value.setStyleSheet(f"""
                    background-color: {colour};
                    color: black;
                    font-family: Fira Code;
                    font-size: 12pt;
                    border-radius: 3px;
                """)

                h.addWidget(label)
                h.addWidget(value)
                layout.addLayout(h)

            frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            self.detailed_col.addWidget(frame)
    
    
    def build_relationships_tab(self):
        from PyQt5.QtWidgets import QVBoxLayout, QLabel

        # Clear previous layout first if it exists
        if self.relationships_tab.layout() is not None:
            old_layout = self.relationships_tab.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            QWidget().setLayout(old_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        self.relationships_tab.setLayout(layout)

        if not self.diplomacy_system:
            notice = QLabel("Diplomacy system not available.")
            notice.setStyleSheet("font-family: Fira Code; font-size: 14pt; color: #cccccc;")
            layout.addWidget(notice)
            return

        # Find relationships
        allies = []
        rivals = []
        enemies = []

        # Get all relationships for this wrestler
        relationships = self.diplomacy_system.get_all_relationships(self.wrestler_id)
        
        for other_id, score in relationships:
            other_name = self.get_wrestler_name_by_id(other_id)
            if not other_name:
                continue  # Skip if wrestler not found
                
            if score >= 75:
                allies.append((other_name, score))
            elif score >= 25:
                allies.append((other_name, score))
            elif score >= -24:
                continue  # Neutral
            elif score >= -74:
                rivals.append((other_name, score))
            else:
                enemies.append((other_name, score))

        def add_section(title, emoji, relationships, color):
            if relationships:
                header = QLabel(f"{emoji} {title}")
                header.setStyleSheet(f"font-family: Fira Code; font-size: 18pt; font-weight: bold; color: {color}; margin-top: 20px;")
                layout.addWidget(header)

                for name, score in sorted(relationships, key=lambda x: -x[1]):
                    btn = QPushButton(f"{name} (Score: {score})")
                    btn.setStyleSheet("""
                        QPushButton {
                            font-family: Fira Code;
                            font-size: 14pt;
                            color: #cccccc;
                            background-color: transparent;
                            border: none;
                            text-align: left;
                            padding: 4px;
                        }
                        QPushButton:hover {
                            color: #66ccff;
                        }
                    """)
                    btn.clicked.connect(lambda _, n=name, s=score, t=title: self.handle_relationship_click(n, s, t))
                    layout.addWidget(btn)

        add_section("Allies", "🤝", allies, "#66ff66")
        add_section("Rivals", "⚡", rivals, "#ffcc00")
        add_section("Enemies", "💀", enemies, "#ff6666")

        if not (allies or rivals or enemies):
            empty = QLabel("No notable relationships yet.")
            empty.setStyleSheet("font-family: Fira Code; font-size: 14pt; color: #cccccc;")
            layout.addWidget(empty)


    def get_wrestler_name_by_id(self, wrestler_id):
        conn = sqlite3.connect(db_path("wrestlers.db"))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM wrestlers WHERE id = ?", (wrestler_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]
        return None


    def rebuild_relationships_tab(self):
        for i in reversed(range(self.relationships_tab.layout().count())):
            widget = self.relationships_tab.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.build_relationships_tab()

    def handle_relationship_click(self, other_wrestler_name, score, relation_type):
        print(f"[Action] You clicked {relation_type} {other_wrestler_name} (Score {score})")
        # 🚀 Later: show a popup or open an action menu

    def build_merchandise_tab(self):
        """Build the merchandise tab content"""
        # Clear existing content
        layout = QVBoxLayout(self.merchandise_tab)
        
        # Create wrestler merchandise UI widget
        self.merch_ui = WrestlerMerchandiseUI(self.wrestler_id, self.wrestler_name)
        
        # Add to layout
        layout.addWidget(self.merch_ui)
