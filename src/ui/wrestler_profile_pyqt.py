from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QGridLayout, QFrame, QSizePolicy, QTabWidget  # <-- ADD QTabWidget here
)
from PyQt5.QtCore import Qt
import sqlite3
from src.db.utils import db_path
from src.ui.theme import apply_styles, BONE
from src.ui.stats_utils import calculate_high_level_stats_with_grades
from src.ui.stats_utils import GRADE_SCALE
from src.core.game_state import get_relationships_refresh_flag, set_relationships_refresh_flag
from src.ui.wrestler_merchandise_ui import WrestlerMerchandiseUI


class WrestlerProfileUI(QWidget):
    def __init__(self, wrestler_id, on_back, diplomacy_system=None):
        super().__init__()
        self.wrestler_id = wrestler_id
        self.on_back = on_back
        self.diplomacy_system = diplomacy_system
        self.wrestler_name = ""  # Will be set in load_profile

        # First, load the wrestler name immediately
        conn = sqlite3.connect(db_path("wrestlers.db"))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM wrestlers WHERE id = ?", (self.wrestler_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            self.wrestler_name = row[0]
        else:
            self.wrestler_name = f"Wrestler {self.wrestler_id}"

        main_layout = QVBoxLayout(self)

        # 🔥 First create tabs and pages
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.profile_tab = QWidget()
        self.relationships_tab = QWidget()
        self.merchandise_tab = QWidget()
        self.buffs_tab = QWidget()

        self.tabs.addTab(self.profile_tab, "Profile")
        self.tabs.addTab(self.relationships_tab, "Relationships")
        self.tabs.addTab(self.merchandise_tab, "Merchandise")
        self.tabs.addTab(self.buffs_tab, "Buffs")

        # 🔥 Now build layout INSIDE profile tab
        layout = QVBoxLayout(self.profile_tab)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        self.build_relationships_tab()
        self.build_buffs_tab()

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
            LEFT JOIN finishers f ON f.id = w.finisher_id
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
            # If attributes don't exist, check if we should create them
            try:
                # Use a basic average value (could be improved to use various calculation methods)
                avg_value = 10  # Default to average
                
                # Create default attributes
                default_attr_query = """
                    INSERT INTO wrestler_attributes (
                        wrestler_id, powerlifting, grapple_control, grip_strength,
                        agility, balance, flexibility, recovery_rate, conditioning,
                        chain_wrestling, mat_transitions, submission_technique, strike_accuracy,
                        brawling_technique, aerial_precision, counter_timing, pressure_handling,
                        promo_delivery, fan_engagement, entrance_presence, presence_under_fire,
                        confidence, focus, resilience, adaptability, risk_assessment,
                        loyalty, political_instinct, determination
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                # Default values based on reputation
                physical_attr = max(8, min(18, rep // 10 + 8))
                technical_attr = max(8, min(18, rep // 10 + 7))
                charisma_attr = max(8, min(18, rep // 10 + 9))
                mental_attr = max(8, min(18, rep // 10 + 8))
                
                cursor.execute(default_attr_query, (
                    self.wrestler_id,
                    physical_attr, physical_attr, physical_attr,  # Physical 1
                    physical_attr, physical_attr, physical_attr, physical_attr, physical_attr,  # Physical 2
                    technical_attr, technical_attr, technical_attr, technical_attr,  # Technical 1
                    technical_attr, technical_attr, technical_attr, technical_attr,  # Technical 2
                    charisma_attr, charisma_attr, charisma_attr, charisma_attr, charisma_attr,  # Charisma
                    mental_attr, mental_attr, mental_attr, mental_attr,  # Mental 1
                    mental_attr, mental_attr, mental_attr  # Mental 2
                ))
                conn.commit()
                
                # Fetch the newly created attributes
                cursor.execute("SELECT * FROM wrestler_attributes WHERE wrestler_id = ?", (self.wrestler_id,))
                attr_row = cursor.fetchone()
                
                if not attr_row:
                    self.meta_section.setText(f"Wrestler found: {name}, but could not create attributes.")
                    conn.close()
                    return
            except Exception as e:
                # Just display basic info if we can't create attributes
                finisher_display = f"{fin_name or 'N/A'}"
                if fin_style or fin_dmg:
                    finisher_display += f" ({fin_style or '-'}) — {fin_dmg or '-'} dmg"
                    
                self.meta_section.setText(f"""\
Name:         {name}
Condition:    {cond}
Reputation:   {rep}
Finisher:     {finisher_display}

Reputation Stats:
• Backstage Influence: {backstage}
• Company Standing:    {company}
• Industry Respect:    {industry}
• Fan Base Strength:   {fan_base}
• Media Presence:      {media}

Error loading attributes: {str(e)}
""")
                conn.close()
                return

        stat_names = [col[0] for col in cursor.description][1:]
        stat_values = attr_row[1:]
        stats = dict(zip(stat_names, stat_values))

        if get_relationships_refresh_flag():
            self.rebuild_relationships_tab()


        conn.close()

        # Meta Info
        finisher_display = f"{fin_name or 'N/A'}"
        if fin_style or fin_dmg:
            finisher_display += f" ({fin_style or '-'}) — {fin_dmg or '-'} dmg"
            
        self.meta_section.setText(f"""\
Name:         {name}
Condition:    {cond}
Reputation:   {rep}
Finisher:     {finisher_display}

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
        from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout, 
                                    QScrollArea, QWidget, QLineEdit, QComboBox)
        from PyQt5.QtCore import Qt
        import logging
        import os

        # Clear previous layout first if it exists
        if self.relationships_tab.layout() is not None:
            old_layout = self.relationships_tab.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            QWidget().setLayout(old_layout)

        # Main layout for the tab
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        self.relationships_tab.setLayout(main_layout)

        # Add title
        title = QLabel("Wrestler Relationships")
        title.setStyleSheet("font-family: Fira Code; font-size: 18pt; font-weight: bold; color: #e0e0e0;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Control panel for search and sorting
        control_panel = QFrame()
        control_panel.setStyleSheet("""
            background-color: #2a2a2a;
            border-radius: 6px;
            padding: 8px;
        """)
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(10, 5, 10, 5)
        
        # Search box
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-family: Fira Code; font-size: 12pt; color: #cccccc;")
        control_layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setStyleSheet("""
            font-family: Fira Code;
            font-size: 12pt;
            padding: 5px;
            border: 1px solid #444;
            border-radius: 4px;
            background-color: #333;
            color: #ffffff;
        """)
        self.search_box.setPlaceholderText("Search wrestlers...")
        self.search_box.textChanged.connect(self.filter_relationships)
        control_layout.addWidget(self.search_box, 2)
        
        # Sort options
        sort_label = QLabel("Sort by:")
        sort_label.setStyleSheet("font-family: Fira Code; font-size: 12pt; color: #cccccc; margin-left: 10px;")
        control_layout.addWidget(sort_label)
        
        self.sort_combo = QComboBox()
        self.sort_combo.setStyleSheet("""
            font-family: Fira Code;
            font-size: 12pt;
            padding: 5px;
            border: 1px solid #444;
            border-radius: 4px;
            background-color: #333;
            color: #ffffff;
            min-width: 150px;
        """)
        self.sort_combo.addItems(["Value (Highest)", "Value (Lowest)", "Name (A-Z)", "Name (Z-A)"])
        self.sort_combo.currentIndexChanged.connect(self.sort_relationships)
        control_layout.addWidget(self.sort_combo, 1)
        
        main_layout.addWidget(control_panel)

        # Create a scroll area for the relationship content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #3a3a3a;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #666;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Container widget for scrollable content
        self.relationship_container = QWidget()
        self.relationship_layout = QVBoxLayout(self.relationship_container)
        self.relationship_layout.setAlignment(Qt.AlignTop)
        self.relationship_layout.setContentsMargins(5, 5, 5, 5)
        self.relationship_layout.setSpacing(15)
        
        # Set the scroll area widget
        scroll_area.setWidget(self.relationship_container)
        main_layout.addWidget(scroll_area)

        # Store relationship data
        self.allies = []
        self.rivals = []
        self.enemies = []
        
        # Load relationships from database
        self.load_relationships()
        
        # Create UI for relationships
        self.update_relationship_ui()
        
        # Add explanation at bottom
        explanation = QLabel("Relationships affect wrestler interactions both in and out of the ring.")
        explanation.setStyleSheet("font-family: Fira Code; font-size: 11pt; color: #999999; margin-top: 10px;")
        explanation.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(explanation)

    def load_relationships(self):
        """Load relationships from the database"""
        import logging
        import os
        import sqlite3
        
        print(f"\n=== Loading relationships for wrestler {self.wrestler_id} ({self.wrestler_name}) ===")
        
        try:
            # Get the absolute path to the database
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            relationships_db_path = os.path.join(project_root, "data", "db", "relationships.db")
            
            print(f"Relationships DB path: {relationships_db_path}")
            print(f"DB exists: {os.path.exists(relationships_db_path)}")
            
            logging.info(f"Using relationships database at: {relationships_db_path}")
            
            # Connect to the relationships database
            conn = sqlite3.connect(relationships_db_path)
            cursor = conn.cursor()
            
            # Print table structure for debugging
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Tables in relationships DB: {[t[0] for t in tables]}")
            
            # Query all relationships for this wrestler
            query = f"SELECT wrestler1_id, wrestler2_id, relationship_value FROM relationships WHERE wrestler1_id = {self.wrestler_id} OR wrestler2_id = {self.wrestler_id}"
            print(f"Running query: {query}")
            
            cursor.execute(query)
            relationships = cursor.fetchall()
            print(f"Found {len(relationships)} relationships")
            
            conn.close()
            
            # Reset relationship lists
            self.allies = []
            self.rivals = []
            self.enemies = []
            
            # Track wrestlers we've already processed to avoid duplicates
            processed_wrestlers = set()
            
            # Process relationships
            for w1, w2, value in relationships:
                other_id = w2 if w1 == self.wrestler_id else w1
                
                # Skip if we've already processed this wrestler
                if other_id in processed_wrestlers:
                    logging.info(f"Skipping duplicate relationship with wrestler ID {other_id}")
                    continue
                    
                processed_wrestlers.add(other_id)
                
                other_name = self.get_wrestler_name_by_id(other_id)
                
                if not other_name:
                    logging.warning(f"Could not find name for wrestler ID {other_id}")
                    continue
                    
                # Categorize based on relationship value
                if value > 0:
                    self.allies.append((other_name, value))
                elif value < -25:
                    self.enemies.append((other_name, value))
                elif value < 0:
                    self.rivals.append((other_name, value))
                
            logging.info(f"Direct DB Query: Found {len(relationships)} relationships for {self.wrestler_name} (ID: {self.wrestler_id})")
            logging.info(f"After deduplication: {len(processed_wrestlers)} unique relationships")
            logging.info(f"Categorized: {len(self.allies)} allies, {len(self.rivals)} rivals, {len(self.enemies)} enemies")
            
        except Exception as e:
            print(f"ERROR in load_relationships: {str(e)}")
            logging.error(f"Error querying relationships database: {e}")
            
            # Try falling back to the diplomacy system
            if self.diplomacy_system:
                logging.info("Falling back to diplomacy system")
                relationships = self.diplomacy_system.get_all_relationships(self.wrestler_id)
                
                # Track wrestlers we've already processed to avoid duplicates
                processed_wrestlers = set()
                
                for other_id, score in relationships:
                    # Skip if we've already processed this wrestler
                    if other_id in processed_wrestlers:
                        continue
                        
                    processed_wrestlers.add(other_id)
                    
                    other_name = self.get_wrestler_name_by_id(other_id)
                    if not other_name:
                        logging.warning(f"Could not find name for wrestler ID {other_id}")
                        continue
                    
                    # Categorize based on relationship value
                    if score > 0:
                        self.allies.append((other_name, score))
                    elif score < -25:
                        self.enemies.append((other_name, score))
                    elif score < 0:
                        self.rivals.append((other_name, score))

    def filter_relationships(self):
        """Filter relationships based on search text"""
        self.update_relationship_ui()

    def sort_relationships(self):
        """Sort relationships based on selected sort option"""
        self.update_relationship_ui()

    def update_relationship_ui(self):
        """Update the relationship UI based on current filter and sort settings"""
        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QFrame, QHBoxLayout
        from PyQt5.QtCore import Qt
        
        # Clear existing widgets from layout
        while self.relationship_layout.count():
            item = self.relationship_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Get search text (lowercase for case-insensitive search)
        search_text = self.search_box.text().lower() if hasattr(self, 'search_box') else ""
        
        # Apply sorting based on combo box selection
        sort_option = self.sort_combo.currentIndex() if hasattr(self, 'sort_combo') else 0
        
        # Sort allies
        allies = self.allies.copy()
        rivals = self.rivals.copy()
        enemies = self.enemies.copy()
        
        if sort_option == 0:  # Value (Highest)
            allies.sort(key=lambda x: -x[1])
            rivals.sort(key=lambda x: -abs(x[1]))
            enemies.sort(key=lambda x: -abs(x[1]))
        elif sort_option == 1:  # Value (Lowest)
            allies.sort(key=lambda x: x[1])
            rivals.sort(key=lambda x: abs(x[1]))
            enemies.sort(key=lambda x: abs(x[1]))
        elif sort_option == 2:  # Name (A-Z)
            allies.sort(key=lambda x: x[0])
            rivals.sort(key=lambda x: x[0])
            enemies.sort(key=lambda x: x[0])
        elif sort_option == 3:  # Name (Z-A)
            allies.sort(key=lambda x: x[0], reverse=True)
            rivals.sort(key=lambda x: x[0], reverse=True)
            enemies.sort(key=lambda x: x[0], reverse=True)
        
        # Filter by search text if provided
        if search_text:
            allies = [(name, score) for name, score in allies if search_text in name.lower()]
            rivals = [(name, score) for name, score in rivals if search_text in name.lower()]
            enemies = [(name, score) for name, score in enemies if search_text in name.lower()]
        
        # Add info about wrestler
        total_count = len(allies) + len(rivals) + len(enemies)
        if total_count > 0:
            filtered_text = " (filtered)" if search_text else ""
            info = QLabel(f"{self.wrestler_name} has {total_count} relationships{filtered_text}")
            info.setStyleSheet("font-family: Fira Code; font-size: 12pt; color: #cccccc; margin-bottom: 10px;")
            info.setAlignment(Qt.AlignCenter)
            self.relationship_layout.addWidget(info)
        
        # Create relationship sections
        has_friends = self.add_section("Friends", "🤝", allies, "#66ff66")
        has_rivals = self.add_section("Rivals", "⚡", rivals, "#ffcc00") 
        has_enemies = self.add_section("Enemies", "💀", enemies, "#ff6666")
        
        if not (has_friends or has_rivals or has_enemies):
            if search_text:
                empty = QLabel(f"No relationships found matching '{search_text}'")
            else:
                empty = QLabel("No notable relationships yet.")
            empty.setStyleSheet("font-family: Fira Code; font-size: 14pt; color: #cccccc; margin: 20px;")
            empty.setAlignment(Qt.AlignCenter)
            self.relationship_layout.addWidget(empty)

    def add_section(self, title, emoji, relationships, color):
        """Add a section for a relationship category"""
        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QFrame, QHBoxLayout
        from PyQt5.QtCore import Qt
        
        if not relationships:
            return False
        
        # Create section container
        section = QFrame()
        section.setStyleSheet(f"""
            background-color: #333333;
            border-left: 4px solid {color};
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 15px;
        """)
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(10, 10, 10, 10)
        section_layout.setSpacing(8)
        
        # Add header
        header = QLabel(f"{emoji} {title} ({len(relationships)})")
        header.setStyleSheet(f"""
            font-family: Fira Code; 
            font-size: 16pt; 
            font-weight: bold; 
            color: {color};
        """)
        section_layout.addWidget(header)
        
        # Add wrestler relationships
        for name, score in relationships:
            item = self.create_relationship_item(name, score)
            section_layout.addWidget(item)
        
        self.relationship_layout.addWidget(section)
        return True

    def create_relationship_item(self, name, score):
        """Create a relationship item widget"""
        from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel
        
        item = QFrame()
        item.setStyleSheet("""
            background-color: #3a3a3a;
            border-radius: 4px;
            padding: 5px;
            margin: 2px 0;
        """)
        
        item_layout = QHBoxLayout(item)
        item_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create a QLabel for the wrestler name
        name_label = QLabel(name)
        name_label.setStyleSheet("""
            font-family: Fira Code;
            font-size: 14pt;
            color: #cccccc;
        """)
        
        # Create a QLabel for the score with appropriate color
        score_label = QLabel(f"{score}")
        score_color = "#66ff66" if score > 0 else "#ff6666"  # Green for positive, red for negative
        score_label.setStyleSheet(f"""
            font-family: Fira Code;
            font-size: 14pt;
            font-weight: bold;
            color: {score_color};
            min-width: 40px;
            text-align: right;
        """)
        
        item_layout.addWidget(name_label, 5)  # Give name more space
        item_layout.addWidget(score_label, 1)  # Score takes less space
        
        return item

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

    def build_buffs_tab(self):
        """Build the buffs tab to display current buffs affecting the wrestler"""
        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QScrollArea, QWidget, QGridLayout, QHBoxLayout, QFrame
        from PyQt5.QtCore import Qt
        import logging
        import os
        import sys
        
        print(f"\n=== Building buffs tab for wrestler {self.wrestler_id} ({self.wrestler_name}) ===")
        
        # Clear previous layout first if it exists
        if self.buffs_tab.layout() is not None:
            old_layout = self.buffs_tab.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            QWidget().setLayout(old_layout)
        
        # Main layout for the tab
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        self.buffs_tab.setLayout(main_layout)
        
        try:
            # Add the current directory to the path so imports work correctly
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            print(f"Project root: {project_root}")
            
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            # Check if buffs database exists
            buffs_db_path = os.path.join(project_root, "data", "db", "buffs.db")
            print(f"Buffs DB path: {buffs_db_path}")
            print(f"DB exists: {os.path.exists(buffs_db_path)}")
            
            if not os.path.exists(buffs_db_path):
                print(f"ERROR: Buffs database not found at {buffs_db_path}")
                raise ImportError(f"Buffs database not found at {buffs_db_path}")
            
            # Debug: check DB tables and contents
            try:
                import sqlite3
                conn = sqlite3.connect(buffs_db_path)
                cursor = conn.cursor()
                
                # Check tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print(f"Tables in buffs DB: {[t[0] for t in tables]}")
                
                # Check if wrestler has buffs
                cursor.execute(f"SELECT COUNT(*) FROM wrestler_buffs WHERE wrestler_id = {self.wrestler_id}")
                buff_count = cursor.fetchone()[0]
                print(f"Wrestler {self.wrestler_id} has {buff_count} buffs in database")
                
                conn.close()
            except Exception as e:
                print(f"Error checking buffs database content: {str(e)}")
            
            # Try to import BuffDisplay
            print("Attempting to import BuffDisplay...")
            from src.ui.BuffDisplay import BuffDisplay
            print("Successfully imported BuffDisplay")
            
            # Create and add the BuffDisplay widget
            print(f"Creating BuffDisplay for wrestler {self.wrestler_id}")
            self.buff_display = BuffDisplay(wrestler_id=self.wrestler_id)
            main_layout.addWidget(self.buff_display)
            
            # Connect signal for buff removal if needed
            self.buff_display.buff_removed.connect(self.on_buff_removed)
            
            logging.info(f"Successfully initialized BuffDisplay for wrestler {self.wrestler_id}")
            
        except Exception as e:
            # Log detailed error information
            print(f"ERROR in build_buffs_tab: {str(e)}")
            logging.error(f"Error initializing BuffDisplay: {str(e)}")
            
            # Show error to user
            error_label = QLabel(f"Buff display system encountered an error: {str(e)}")
            error_label.setStyleSheet("font-family: Fira Code; font-size: 14pt; color: #ff6666;")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setWordWrap(True)
            main_layout.addWidget(error_label)
            
            # Fall back to the old implementation
            print("Falling back to legacy buff display implementation")
            self._legacy_build_buffs_tab()

    def load_wrestler_buffs(self):
        """Load wrestler's active buffs from the database"""
        import sqlite3
        import os
        import logging
        from datetime import datetime
        
        buffs = []
        
        try:
            # Get database path
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            buffs_db_path = os.path.join(project_root, "data", "db", "buffs.db")
            
            # Check if database exists
            if not os.path.exists(buffs_db_path):
                logging.warning(f"Buffs database not found at {buffs_db_path}")
                
                # Return sample buffs for now (these will be shown until the database is populated)
                return [
                    {"name": "Crowd Favorite", "description": "Increased fan support during matches", "icon": "👑", "color": "#66ff66", "duration": "Permanent"},
                    {"name": "Recovering from Injury", "description": "-15% to physical performance", "icon": "🤕", "color": "#ff6666", "duration": "2 weeks"},
                    {"name": "Momentum Surge", "description": "+10% to win probability", "icon": "🔥", "color": "#ffcc00", "duration": "3 matches"},
                    {"name": "Merchandise Boost", "description": "+20% merchandise sales", "icon": "💰", "color": "#66ccff", "duration": "1 month"}
                ]
            
            # Connect to database
            conn = sqlite3.connect(buffs_db_path)
            cursor = conn.cursor()
            
            # First check if the expected tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wrestler_buffs'")
            if not cursor.fetchone():
                logging.warning("wrestler_buffs table not found in the buffs database")
                conn.close()
                return []
                
            # Check for buff_types table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='buff_types'")
            if not cursor.fetchone():
                logging.warning("buff_types table not found in the buffs database")
                conn.close()
                return []
            
            # Check table structure to determine correct column names
            cursor.execute("PRAGMA table_info(wrestler_buffs)")
            columns = {col[1]: True for col in cursor.fetchall()}
            
            # Build query based on available columns
            select_columns = ["bt.name", "bt.description", "bt.icon", "bt.color"]
            
            # Check for additional columns
            if "duration" in columns:
                select_columns.append("wb.duration")
            else:
                select_columns.append("NULL as duration")
                
            if "expiry_date" in columns:
                select_columns.append("wb.expiry_date")
            else:
                select_columns.append("NULL as expiry_date")
                
            if "value" in columns:
                select_columns.append("wb.value")
            else:
                select_columns.append("1.0 as value")
            
            # Query active buffs for this wrestler
            query = f"""
                SELECT {', '.join(select_columns)}
                FROM wrestler_buffs wb
                JOIN buff_types bt ON wb.buff_type_id = bt.id
                WHERE wb.wrestler_id = ?
                ORDER BY bt.effect_type DESC, wb.applied_at DESC
            """
            
            cursor.execute(query, (self.wrestler_id,))
            rows = cursor.fetchall()
            
            # Process each buff
            for row in rows:
                name, description, icon, color, duration, expiry_date, value = row
                
                # Format the description with the buff value if available
                if value:
                    if "%" in description:
                        formatted_desc = description.replace("%", f"{value}%")
                    else:
                        formatted_desc = f"{description} ({value})"
                else:
                    formatted_desc = description
                
                buffs.append({
                    "name": name,
                    "description": formatted_desc,
                    "icon": icon or "⚡",
                    "color": color or "#ffffff",
                    "duration": duration or "Permanent", 
                    "value": value or 1.0
                })
            
            conn.close()
            
            logging.info(f"Loaded {len(buffs)} buffs for wrestler {self.wrestler_name} (ID: {self.wrestler_id})")
            
        except Exception as e:
            logging.error(f"Error loading buffs: {e}")
            
            # Return sample buffs in case of error
            return [
                {"name": "Crowd Favorite", "description": "Increased fan support during matches", "icon": "👑", "color": "#66ff66", "duration": "Permanent"},
                {"name": "Recovering from Injury", "description": "-15% to physical performance", "icon": "🤕", "color": "#ff6666", "duration": "2 weeks"}
            ]
        
        return buffs

    def create_buff_card(self, buff):
        """Create a card widget for a buff"""
        from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
        
        card = QFrame()
        card.setStyleSheet(f"""
            background-color: #333333;
            border: 2px solid {buff['color']};
            border-radius: 8px;
            padding: 8px;
            margin: 5px;
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(5)
        
        # Buff header with icon
        header = QLabel(f"{buff['icon']} {buff['name']}")
        header.setStyleSheet(f"""
            font-family: Fira Code;
            font-size: 14pt;
            font-weight: bold;
            color: {buff['color']};
        """)
        card_layout.addWidget(header)
        
        # Buff description
        desc = QLabel(buff['description'])
        desc.setStyleSheet("font-family: Fira Code; font-size: 12pt; color: #cccccc;")
        desc.setWordWrap(True)
        card_layout.addWidget(desc)
        
        # Duration
        duration = QLabel(f"Duration: {buff['duration']}")
        duration.setStyleSheet("font-family: Fira Code; font-size: 10pt; color: #999999;")
        card_layout.addWidget(duration)
        
        return card

    def on_buff_removed(self, wrestler_id, buff_name):
        """Handle when a buff is removed from the wrestler"""
        import logging
        logging.info(f"Buff '{buff_name}' removed from wrestler {wrestler_id}")
        
        # You can add additional logic here if needed when buffs are removed
        # For example, update other parts of the UI that might depend on buffs

    def _legacy_build_buffs_tab(self):
        """Legacy implementation of the buffs tab (used as fallback)"""
        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QScrollArea, QWidget, QGridLayout, QHBoxLayout, QFrame
        import logging
        
        # Main layout already created in build_buffs_tab
        main_layout = self.buffs_tab.layout()
        
        # Create a scroll area for the buffs content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #3a3a3a;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #666;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Container widget for scrollable content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignTop)
        content_layout.setSpacing(15)
        
        # Add a title
        title = QLabel("Active Buffs & Debuffs")
        title.setStyleSheet("font-family: Fira Code; font-size: 20pt; font-weight: bold; color: #e0e0e0; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title)
        
        # Load active buffs from database
        buffs = self.load_wrestler_buffs()
        
        # Display a message if no buffs are active
        if not buffs:
            no_buffs = QLabel("No active buffs or debuffs")
            no_buffs.setStyleSheet("font-family: Fira Code; font-size: 14pt; color: #cccccc; margin: 20px;")
            no_buffs.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(no_buffs)
        else:
            # Create a grid layout for the buff cards
            grid = QGridLayout()
            grid.setSpacing(15)
            
            # Add each buff to the grid
            for i, buff in enumerate(buffs):
                # Create buff card
                card = self.create_buff_card(buff)
                
                # Add to grid
                row, col = divmod(i, 2)
                grid.addWidget(card, row, col)
            
            content_layout.addLayout(grid)
        
        # Add a note about buffs
        note = QLabel("Buffs are temporary or permanent effects that modify wrestler performance")
        note.setStyleSheet("font-family: Fira Code; font-size: 12pt; color: #999999; margin-top: 20px;")
        note.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(note)
        
        # Set the content widget to the scroll area
        scroll_area.setWidget(content)
        
        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)
