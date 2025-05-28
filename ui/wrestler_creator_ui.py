from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QGridLayout, QGroupBox, QScrollArea,
    QTabWidget, QFormLayout, QMessageBox, QSpinBox, QSizePolicy,
    QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
import sqlite3
import random
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.utils import db_path
from wrestler_creator_model import (
    generate_random_wrestler, get_attributes_list, 
    get_attribute_names, ARCHETYPES
)
from ui.theme import apply_styles

class AttributeField(QSpinBox):
    """Custom SpinBox for wrestler attributes"""
    def __init__(self, min_val=5, max_val=20, parent=None):
        super().__init__(parent)
        self.setMinimum(min_val)
        self.setMaximum(max_val)
        self.setValue(10)
        self.setFixedHeight(30)
        self.setFixedWidth(60)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Fira Code", 12))
        self.setStyleSheet("""
            QSpinBox {
                background-color: #2c2c2c;
                color: #fff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 2px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 16px;
                border-radius: 3px;
                background-color: #444;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #555;
            }
        """)

class WrestlerCreatorUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wrestler Creator")
        
        # Setup UI
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(20)
        
        # Header
        self.setup_header()
        
        # Tabs for organization
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #2c2c2c;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #333;
                color: #ccc;
                border: 1px solid #444;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background-color: #2c2c2c;
                color: #fff;
                border-bottom: none;
            }
        """)
        
        # Create tabs
        self.setup_basic_info_tab()
        self.setup_attributes_tab()
        self.setup_moves_tab()
        
        self.main_layout.addWidget(self.tabs)
        
        # Add action buttons
        self.setup_action_buttons()
        
        # Initialize signature moves list
        self.signature_moves = []
        
        # Set up attribute fields dictionary
        self.attribute_fields = {}
        self.setup_attribute_fields()
    
    def setup_header(self):
        header = QVBoxLayout()
        
        # Title
        title = QLabel("Wrestler Creator")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #fff; margin-bottom: 10px;")
        header.addWidget(title)
        
        # Quick actions
        actions = QHBoxLayout()
        actions.setSpacing(15)
        
        # Random wrestler button
        self.random_btn = QPushButton("🎲 Random Wrestler")
        apply_styles(self.random_btn, "button_blue")
        self.random_btn.clicked.connect(self.generate_random_wrestler)
        actions.addWidget(self.random_btn)
        
        # Archetype selector
        self.archetype_label = QLabel("Archetype:")
        self.archetype_label.setStyleSheet("color: #fff; font-size: 12pt;")
        actions.addWidget(self.archetype_label)
        
        self.archetype_combo = QComboBox()
        self.archetype_combo.addItems(list(ARCHETYPES.keys()))
        self.archetype_combo.setStyleSheet("""
            QComboBox {
                background-color: #333;
                color: #fff;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 4px;
                min-width: 180px;
                font-size: 12pt;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #333;
                color: #fff;
                selection-background-color: #555;
            }
        """)
        actions.addWidget(self.archetype_combo)
        
        # Apply archetype button
        self.apply_archetype_btn = QPushButton("Apply Archetype")
        apply_styles(self.apply_archetype_btn, "button_green")
        self.apply_archetype_btn.clicked.connect(self.apply_archetype)
        actions.addWidget(self.apply_archetype_btn)
        
        actions.addStretch()
        header.addLayout(actions)
        
        self.main_layout.addLayout(header)
    
    def setup_basic_info_tab(self):
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # Basic info form
        form = QFormLayout()
        form.setSpacing(15)
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignLeft)
        
        # Name field
        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Enter wrestler name")
        self.name_field.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: #fff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                font-size: 12pt;
            }
        """)
        name_label = QLabel("Name:")
        name_label.setStyleSheet("color: #fff; font-size: 12pt;")
        form.addRow(name_label, self.name_field)
        
        # Reputation
        self.reputation_field = QSpinBox()
        self.reputation_field.setRange(0, 100)
        self.reputation_field.setValue(50)
        self.reputation_field.setStyleSheet("""
            QSpinBox {
                background-color: #333;
                color: #fff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                font-size: 12pt;
            }
        """)
        reputation_label = QLabel("Reputation:")
        reputation_label.setStyleSheet("color: #fff; font-size: 12pt;")
        form.addRow(reputation_label, self.reputation_field)
        
        # Height (in inches)
        self.height_field = QSpinBox()
        self.height_field.setRange(60, 96)  # 5'0" to 8'0"
        self.height_field.setValue(72)      # 6'0" default
        self.height_field.setStyleSheet("""
            QSpinBox {
                background-color: #333;
                color: #fff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                font-size: 12pt;
            }
        """)
        self.height_field.setSuffix(" in")
        height_label = QLabel("Height:")
        height_label.setStyleSheet("color: #fff; font-size: 12pt;")
        form.addRow(height_label, self.height_field)
        
        # Weight (in pounds)
        self.weight_field = QSpinBox()
        self.weight_field.setRange(150, 400)
        self.weight_field.setValue(230)
        self.weight_field.setStyleSheet("""
            QSpinBox {
                background-color: #333;
                color: #fff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                font-size: 12pt;
            }
        """)
        self.weight_field.setSuffix(" lbs")
        weight_label = QLabel("Weight:")
        weight_label.setStyleSheet("color: #fff; font-size: 12pt;")
        form.addRow(weight_label, self.weight_field)
        
        basic_layout.addLayout(form)
        basic_layout.addStretch()
        
        self.tabs.addTab(basic_tab, "Basic Info")
    
    def setup_attributes_tab(self):
        attributes_tab = QWidget()
        
        # Create scrollable area for attributes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2c2c2c;
                width: 14px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                min-height: 20px;
                border-radius: 7px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        attributes_content = QWidget()
        attributes_layout = QVBoxLayout(attributes_content)
        attributes_layout.setSpacing(20)
        
        # Physical attributes
        self.create_attribute_group("Physical", [
            "powerlifting", "grapple_control", "grip_strength", "agility", 
            "balance", "flexibility", "recovery_rate", "conditioning"
        ], attributes_layout)
        
        # In-Ring attributes
        self.create_attribute_group("In-Ring", [
            "chain_wrestling", "mat_transitions", "submission_technique", "strike_accuracy",
            "brawling_technique", "aerial_precision", "counter_timing", "pressure_handling"
        ], attributes_layout)
        
        # Charisma attributes
        self.create_attribute_group("Charisma", [
            "promo_delivery", "fan_engagement", "entrance_presence", 
            "presence_under_fire", "confidence"
        ], attributes_layout)
        
        # Mental attributes
        self.create_attribute_group("Mental", [
            "focus", "resilience", "adaptability", "risk_assessment",
            "loyalty", "political_instinct", "determination"
        ], attributes_layout)
        
        scroll.setWidget(attributes_content)
        
        attributes_tab_layout = QVBoxLayout(attributes_tab)
        attributes_tab_layout.addWidget(scroll)
        
        self.tabs.addTab(attributes_tab, "Attributes")
    
    def create_attribute_group(self, title, attributes, parent_layout):
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14pt;
                font-weight: bold;
                color: #fff;
                border: 1px solid #555;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 8px;
            }
        """)
        
        layout = QGridLayout(group)
        layout.setSpacing(15)
        
        for i, attr in enumerate(attributes):
            # Format attribute name
            attr_display = attr.replace('_', ' ').title()
            
            # Create label
            label = QLabel(attr_display)
            label.setStyleSheet("color: #ddd; font-size: 11pt;")
            
            # Create spin box
            spin = AttributeField()
            
            # Store reference to field
            self.attribute_fields[attr] = spin
            
            # Add to layout (2 columns)
            row = i // 2
            col = (i % 2) * 2
            
            layout.addWidget(label, row, col)
            layout.addWidget(spin, row, col + 1)
        
        parent_layout.addWidget(group)
    
    def setup_moves_tab(self):
        moves_tab = QWidget()
        moves_layout = QVBoxLayout(moves_tab)
        
        # Finisher section
        finisher_group = QGroupBox("Finisher")
        finisher_group.setStyleSheet("""
            QGroupBox {
                font-size: 14pt;
                font-weight: bold;
                color: #fff;
                border: 1px solid #555;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 8px;
            }
        """)
        
        finisher_layout = QFormLayout(finisher_group)
        finisher_layout.setSpacing(15)
        finisher_layout.setLabelAlignment(Qt.AlignRight)
        
        # Finisher name
        self.finisher_name = QLineEdit()
        self.finisher_name.setPlaceholderText("Enter finisher name")
        self.finisher_name.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: #fff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                font-size: 12pt;
            }
        """)
        finisher_name_label = QLabel("Finisher Name:")
        finisher_name_label.setStyleSheet("color: #fff; font-size: 12pt;")
        finisher_layout.addRow(finisher_name_label, self.finisher_name)
        
        # Finisher style
        self.finisher_style = QComboBox()
        self.finisher_style.addItems(["slam", "strike", "submission", "aerial"])
        self.finisher_style.setStyleSheet("""
            QComboBox {
                background-color: #333;
                color: #fff;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 4px;
                min-width: 180px;
                font-size: 12pt;
            }
        """)
        finisher_style_label = QLabel("Style:")
        finisher_style_label.setStyleSheet("color: #fff; font-size: 12pt;")
        finisher_layout.addRow(finisher_style_label, self.finisher_style)
        
        # Finisher damage
        self.finisher_damage = QSpinBox()
        self.finisher_damage.setRange(8, 12)
        self.finisher_damage.setValue(10)
        self.finisher_damage.setStyleSheet("""
            QSpinBox {
                background-color: #333;
                color: #fff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                font-size: 12pt;
            }
        """)
        finisher_damage_label = QLabel("Damage:")
        finisher_damage_label.setStyleSheet("color: #fff; font-size: 12pt;")
        finisher_layout.addRow(finisher_damage_label, self.finisher_damage)
        
        moves_layout.addWidget(finisher_group)
        
        # Signature moves section
        sig_moves_group = QGroupBox("Signature Moves")
        sig_moves_group.setStyleSheet("""
            QGroupBox {
                font-size: 14pt;
                font-weight: bold;
                color: #fff;
                border: 1px solid #555;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 8px;
            }
        """)
        
        sig_moves_layout = QVBoxLayout(sig_moves_group)
        
        # Container for signature move rows
        self.sig_moves_container = QVBoxLayout()
        sig_moves_layout.addLayout(self.sig_moves_container)
        
        # Add initial signature move row
        self.add_signature_move_row()
        
        # Button to add more signature moves
        add_move_btn = QPushButton("+ Add Signature Move")
        add_move_btn.clicked.connect(self.add_signature_move_row)
        apply_styles(add_move_btn, "button_blue")
        sig_moves_layout.addWidget(add_move_btn)
        
        moves_layout.addWidget(sig_moves_group)
        moves_layout.addStretch()
        
        self.tabs.addTab(moves_tab, "Finisher & Signatures")
    
    def add_signature_move_row(self):
        # Create a frame for the row
        row_frame = QFrame()
        row_frame.setStyleSheet("background-color: #333; border-radius: 4px; margin: 2px;")
        row_layout = QHBoxLayout(row_frame)
        row_layout.setSpacing(10)
        
        # Name field
        name = QLineEdit()
        name.setPlaceholderText("Move Name")
        name.setStyleSheet("""
            QLineEdit {
                background-color: #444;
                color: #fff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        
        # Style dropdown
        style = QComboBox()
        style.addItems(["strike", "slam", "submission", "aerial"])
        style.setStyleSheet("""
            QComboBox {
                background-color: #444;
                color: #fff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        
        # Damage spinner
        damage = QSpinBox()
        damage.setRange(5, 9)
        damage.setValue(7)
        damage.setPrefix("Damage: ")
        damage.setStyleSheet("""
            QSpinBox {
                background-color: #444;
                color: #fff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        
        # Difficulty spinner
        difficulty = QSpinBox()
        difficulty.setRange(5, 9)
        difficulty.setValue(6)
        difficulty.setPrefix("Difficulty: ")
        difficulty.setStyleSheet("""
            QSpinBox {
                background-color: #444;
                color: #fff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        
        # Remove button
        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(30, 30)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #c23616;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e84118;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_signature_move(row_frame))
        
        # Add widgets to layout
        row_layout.addWidget(name, 3)
        row_layout.addWidget(style, 2)
        row_layout.addWidget(damage, 1)
        row_layout.addWidget(difficulty, 1)
        row_layout.addWidget(remove_btn, 0)
        
        self.sig_moves_container.addWidget(row_frame)
        
        # Store references
        self.signature_moves.append((name, style, damage, difficulty, row_frame))
    
    def remove_signature_move(self, frame):
        # Remove the frame from UI
        self.sig_moves_container.removeWidget(frame)
        
        # Find and remove from the signature_moves list
        for i, (name, style, damage, difficulty, f) in enumerate(self.signature_moves):
            if f == frame:
                self.signature_moves.pop(i)
                break
        
        # Delete the frame
        frame.deleteLater()
    
    def setup_action_buttons(self):
        buttons = QHBoxLayout()
        
        # Save button
        save_btn = QPushButton("💾 Save Wrestler")
        save_btn.clicked.connect(self.save_wrestler)
        apply_styles(save_btn, "button_green")
        buttons.addWidget(save_btn)
        
        # Clear button
        clear_btn = QPushButton("🧹 Clear All")
        clear_btn.clicked.connect(self.clear_form)
        apply_styles(clear_btn, "button_red")
        buttons.addWidget(clear_btn)
        
        self.main_layout.addLayout(buttons)
    
    def setup_attribute_fields(self):
        # Make sure all attribute fields are initialized
        for attr in get_attribute_names():
            if attr not in self.attribute_fields:
                self.attribute_fields[attr] = AttributeField()
    
    def generate_random_wrestler(self):
        # Generate random wrestler data
        wrestler = generate_random_wrestler()
        
        # Populate form with random data
        self.name_field.setText(f"Random {wrestler['archetype']}")
        self.reputation_field.setValue(wrestler['reputation'])
        self.height_field.setValue(wrestler['height'])
        self.weight_field.setValue(wrestler['weight'])
        
        # Set attributes
        for attr, value in wrestler['attributes'].items():
            if attr in self.attribute_fields:
                self.attribute_fields[attr].setValue(value)
        
        # Set finisher
        self.finisher_name.setText(f"{wrestler['archetype']} Finisher")
        self.finisher_style.setCurrentText(wrestler['finisher_style'])
        self.finisher_damage.setValue(wrestler['finisher_damage'])
        
        # Clear existing signature moves
        while self.signature_moves:
            self.remove_signature_move(self.signature_moves[0][4])
        
        # Add new signature moves
        for sig in wrestler['signature_moves']:
            self.add_signature_move_row()
            move_data = self.signature_moves[-1]
            move_data[0].setText(f"{wrestler['archetype']} Signature")
            move_data[1].setCurrentText(sig['type'])
            move_data[2].setValue(sig['damage'])
            move_data[3].setValue(sig['difficulty'])
    
    def apply_archetype(self):
        # Get selected archetype
        archetype = self.archetype_combo.currentText()
        
        # Generate wrestler based on archetype
        wrestler = generate_random_wrestler(archetype)
        
        # Only apply attributes, not other fields
        for attr, value in wrestler['attributes'].items():
            if attr in self.attribute_fields:
                self.attribute_fields[attr].setValue(value)
    
    def clear_form(self):
        # Clear basic info
        self.name_field.clear()
        self.reputation_field.setValue(50)
        self.height_field.setValue(72)
        self.weight_field.setValue(230)
        
        # Clear attributes
        for field in self.attribute_fields.values():
            field.setValue(10)
        
        # Clear finisher
        self.finisher_name.clear()
        self.finisher_style.setCurrentIndex(0)
        self.finisher_damage.setValue(10)
        
        # Clear signature moves
        while self.signature_moves:
            self.remove_signature_move(self.signature_moves[0][4])
        
        # Add one empty signature move row
        self.add_signature_move_row()
    
    def save_wrestler(self):
        try:
            # Validate name
            name = self.name_field.text().strip()
            if not name:
                QMessageBox.critical(self, "Error", "Wrestler name is required!")
                return
            
            # Get values from form
            reputation = self.reputation_field.value()
            height = self.height_field.value()
            weight = self.weight_field.value()
            
            # Get finisher info
            finisher_name = self.finisher_name.text().strip()
            if not finisher_name:
                # Instead of allowing empty finisher name, generate one from wrestler name
                finisher_name = f"{name}'s Finisher"
                
            finisher_style = self.finisher_style.currentText()
            finisher_damage = self.finisher_damage.value()
            
            # Get attributes
            attributes = []
            for attr_name in get_attribute_names():
                attributes.append(self.attribute_fields[attr_name].value())
            
            # Connect to DB
            conn = sqlite3.connect(db_path("wrestlers.db"))
            conn.execute(f"ATTACH DATABASE '{db_path('finishers.db')}' AS fdb")
            cursor = conn.cursor()
            
            # Check if wrestler with same name already exists
            cursor.execute("SELECT id FROM wrestlers WHERE name = ?", (name,))
            if cursor.fetchone():
                QMessageBox.critical(self, "Error", f"Wrestler with name '{name}' already exists!")
                conn.close()
                return
            
            # Insert or get finisher
            cursor.execute("SELECT id FROM finishers WHERE name = ?", (finisher_name,))
            row = cursor.fetchone()
            if row:
                finisher_id = row[0]
            else:
                cursor.execute(
                    "INSERT INTO finishers (name, style, damage, difficulty) VALUES (?, ?, ?, ?)",
                    (finisher_name, finisher_style, finisher_damage, 8)  # Default difficulty
                )
                finisher_id = cursor.lastrowid
            
            # Generate contract details
            current_date = datetime.now()
            expiry_date = current_date + timedelta(days=random.randint(730, 1460))  # 2-4 years
            contract_expiry = expiry_date.strftime('%Y-%m-%d')
            contract_value = 500000 + (reputation * 10000)
            
            # Insert wrestler
            cursor.execute("""
                INSERT INTO wrestlers (
                    name, reputation, condition, finisher_id,
                    fan_popularity, marketability, merchandise_sales,
                    contract_type, contract_expiry, contract_value,
                    contract_promises, contract_company,
                    locker_room_impact, loyalty_level, ambition, injury,
                    height, weight
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, reputation, 100, finisher_id,
                'High' if reputation > 70 else 'Moderate', 
                'High' if reputation > 70 else 'Moderate',
                'Excellent' if reputation > 70 else 'Average',
                'Full-Time', contract_expiry, contract_value,
                '', 'WWE',  # Default values
                'Positive' if random.random() > 0.5 else 'Negative',
                'Moderate', 'Moderate', '',
                height, weight
            ))
            wrestler_id = cursor.lastrowid
            
            # Insert attributes
            attr_names = get_attribute_names()
            placeholders = ",".join(["?"] * (len(attr_names) + 1))
            cursor.execute(f"""
                INSERT INTO wrestler_attributes (
                    wrestler_id, {", ".join(attr_names)}
                ) VALUES ({placeholders})
            """, (wrestler_id, *attributes))
            
            # Insert signature moves
            for name_field, type_box, dmg_field, diff_field, _ in self.signature_moves:
                move_name = name_field.text().strip()
                if not move_name:
                    continue
                
                move_type = type_box.currentText()
                move_damage = dmg_field.value()
                move_difficulty = diff_field.value()
                
                # Insert or get signature move
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
                
                # Link to wrestler
                cursor.execute("""
                    INSERT INTO wrestler_signature_moves (wrestler_id, signature_move_id)
                    VALUES (?, ?)
                """, (wrestler_id, move_id))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", f"Wrestler '{name}' added successfully!")
            
            # Clear form after successful save
            self.clear_form()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save wrestler: {str(e)}") 