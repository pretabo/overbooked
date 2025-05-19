from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QScrollArea, QGroupBox, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, QMimeData, QPoint
from PyQt5.QtGui import QDrag, QColor
from storyline.storyline_manager import StorylineManager
from match_engine import load_wrestler_by_id
from ui.theme import apply_styles

class StorylineItem(QFrame):
    """A draggable item representing a potential or active storyline."""
    def __init__(self, storyline_data, main_ui=None, parent=None):
        super().__init__(parent)
        self.storyline_data = storyline_data
        self.main_ui = main_ui
        self.setAcceptDrops(True)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(3)
        
        # Get wrestler names
        wrestler1 = load_wrestler_by_id(self.storyline_data['wrestler1_id'])
        wrestler2 = load_wrestler_by_id(self.storyline_data['wrestler2_id'])
        
        # Storyline value (with decay)
        storyline_manager = StorylineManager()
        value = storyline_manager.get_storyline_value(self.storyline_data['wrestler1_id'], self.storyline_data['wrestler2_id'])
        value_label = QLabel(f"Potential Value: {value:.1f}")
        value_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 11pt;")
        layout.addWidget(value_label)
        
        # Tooltip: show all interaction attributes and buffs
        interactions = storyline_manager.get_storyline_interactions(self.storyline_data['wrestler1_id'], self.storyline_data['wrestler2_id'])
        tooltip_lines = []
        for inter in interactions:
            buffs = ", ".join(f"{k}: {v}" for k, v in inter['attributes'].items() if k != 'details')
            tooltip_lines.append(f"{inter['interaction_date']} - {inter['interaction_type']} (Value: {inter['base_value']})\n  Buffs: {buffs}\n  Details: {inter['attributes'].get('details','')}")
        tooltip = "\n\n".join(tooltip_lines) if tooltip_lines else "No interactions yet."
        self.setToolTip(tooltip)
        
        # Create the main content
        if 'interaction_type' in self.storyline_data:  # Potential storyline
            title = f"{wrestler1['name']} vs {wrestler2['name']}"
            subtitle = f"Type: {self.storyline_data['interaction_type']}"
            details = self.storyline_data['interaction_details']
            date = self.storyline_data['interaction_date']
            
            # Add potential rating indicator
            rating = self.storyline_data.get('potential_rating', 0)
            rating_label = QLabel(f"Potential Rating: {rating}/100")
            rating_label.setStyleSheet(f"""
                color: {'#4CAF50' if rating >= 80 else '#FFC107' if rating >= 60 else '#F44336'};
                font-weight: bold;
            """)
            layout.addWidget(rating_label)
        else:  # Active storyline
            title = f"{wrestler1['name']} vs {wrestler2['name']}"
            subtitle = f"Type: {self.storyline_data['storyline_type']}"
            details = f"Priority: {self.storyline_data['priority']}"
            date = self.storyline_data['start_date']
        
        # Add content to layout
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: #aaa;")
        layout.addWidget(subtitle_label)
        
        details_label = QLabel(details)
        details_label.setWordWrap(True)
        layout.addWidget(details_label)
        
        date_label = QLabel(f"Date: {date}")
        date_label.setStyleSheet("color: #888; font-size: 9pt;")
        layout.addWidget(date_label)
        
        # Add delete button for potential storylines
        if 'interaction_type' in self.storyline_data:
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            if self.main_ui:
                delete_btn.clicked.connect(lambda: self.main_ui.delete_storyline(self.storyline_data['id']))
            layout.addWidget(delete_btn)
        
        # Style the frame
        self.setStyleSheet("""
            QFrame {
                background-color: #232323;
                border: 1px solid #444;
                border-radius: 5px;
                margin: 2px;
                padding: 2px;
            }
            QFrame:hover {
                background-color: #2a2a2a;
                border: 1px solid #666;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(str(self.storyline_data['id']))
            drag.setMimeData(mime_data)
            drag.exec_(Qt.MoveAction)

class StorylineContainer(QFrame):
    """A container for storyline items that accepts drops."""
    def __init__(self, title, main_ui=None, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.main_ui = main_ui
        self.initUI(title)

    def initUI(self, title):
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Scroll area for items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container for items
        self.items_container = QFrame()
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.items_container)
        
        layout.addWidget(scroll)
        
        # Style the container
        self.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #444;
                border-radius: 10px;
                padding: 10px;
            }
        """)

    def add_item(self, storyline_data):
        item = StorylineItem(storyline_data, main_ui=self.main_ui)
        self.items_layout.addWidget(item)

    def clear_items(self):
        while self.items_layout.count():
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        storyline_id = int(event.mimeData().text())
        # Use the main_ui reference to handle the drop
        if self.main_ui:
            self.main_ui.handle_storyline_drop(storyline_id, self)

class StorylineManagementUI(QWidget):
    """Main UI for managing storylines."""
    def __init__(self, on_back=None):
        super().__init__()
        self.on_back = on_back
        self.storyline_manager = StorylineManager()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        
        # Left side - Potential storylines
        left_panel = QVBoxLayout()
        
        # Potential storylines header
        potential_header = QHBoxLayout()
        potential_title = QLabel("Potential Storylines")
        potential_title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        potential_header.addWidget(potential_title)
        
        # Add refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_storylines)
        apply_styles(refresh_btn, "button_blue")
        potential_header.addWidget(refresh_btn)
        
        left_panel.addLayout(potential_header)
        
        # Potential storylines container
        self.potential_container = StorylineContainer("", main_ui=self)
        left_panel.addWidget(self.potential_container)
        
        # Right side - Active storylines
        right_panel = QVBoxLayout()
        
        # Active storylines header
        active_header = QHBoxLayout()
        active_title = QLabel("Active Storylines")
        active_title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        active_header.addWidget(active_title)
        right_panel.addLayout(active_header)
        
        # Active storylines container
        self.active_container = StorylineContainer("", main_ui=self)
        right_panel.addWidget(self.active_container)
        
        # Add panels to main layout
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        layout.addWidget(left_widget, 1)
        layout.addWidget(right_widget, 1)
        
        # Only add back button if needed
        if self.on_back:
            back_btn = QPushButton("Back")
            apply_styles(back_btn, "button_nav")
            back_btn.clicked.connect(self.on_back)
            layout.addWidget(back_btn)
        
        # Load initial data
        self.refresh_storylines()

    def refresh_storylines(self):
        """Refresh both potential and active storylines."""
        # Clear existing items
        self.potential_container.clear_items()
        self.active_container.clear_items()
        
        # Load potential storylines
        potential_storylines = self.storyline_manager.get_potential_storylines()
        for storyline in potential_storylines:
            self.potential_container.add_item(storyline)
        
        # Load active storylines
        active_storylines = self.storyline_manager.get_active_storylines()
        for storyline in active_storylines:
            self.active_container.add_item(storyline)

    def delete_storyline(self, storyline_id: int):
        """Delete a potential storyline."""
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            'Are you sure you want to delete this potential storyline?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.storyline_manager.delete_potential_storyline(storyline_id)
            self.refresh_storylines()

    def handle_storyline_drop(self, storyline_id, target_container):
        """Handle dropping a storyline into a container."""
        if target_container == self.active_container:
            # Only show confirmation for potential storylines
            storyline = self.storyline_manager.get_potential_storyline_details(storyline_id)
            if not storyline:
                return
            reply = QMessageBox.question(
                self, 'Activate Storyline',
                'Are you sure you want to activate this storyline?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    self.storyline_manager.activate_storyline(
                        storyline_id, "Feud", 1
                    )
                    self.refresh_storylines()
                except Exception as e:
                    QMessageBox.warning(
                        self, "Error",
                        f"Failed to activate storyline: {str(e)}"
                    ) 