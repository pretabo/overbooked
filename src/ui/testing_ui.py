from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import logging

class TestingUI(QWidget):
    def __init__(self, parent=None, load_screen_callback=None):
        super().__init__(parent)
        self.load_screen_callback = load_screen_callback
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Testing & Development Tools")
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel(
            "This section contains tools for testing and developing the game. "
            "These tools are not intended for normal gameplay."
        )
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # Testing tools section
        tools_layout = QHBoxLayout()
        
        # Create groups of tools
        tools_layout.addWidget(self.create_game_tools_group())
        tools_layout.addWidget(self.create_debug_tools_group())
        
        layout.addLayout(tools_layout)
        
        # Return button
        back_btn = QPushButton("Return to Game")
        back_btn.setMinimumHeight(40)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        back_btn.clicked.connect(self.return_to_game)
        layout.addWidget(back_btn)
        
        self.setLayout(layout)
    
    def create_game_tools_group(self):
        """Create the game tools group"""
        group = QGroupBox("Game Testing Tools")
        layout = QVBoxLayout()
        
        # Add Wrestler button
        add_wrestler_btn = QPushButton("Add Wrestler")
        add_wrestler_btn.clicked.connect(lambda: self.load_screen("add_wrestler"))
        layout.addWidget(add_wrestler_btn)
        
        # Simulate Match button
        match_btn = QPushButton("Simulate Match")
        match_btn.clicked.connect(lambda: self.load_screen("simulate_match"))
        layout.addWidget(match_btn)
        
        # Test Promos button
        promo_btn = QPushButton("Test Promos")
        promo_btn.clicked.connect(lambda: self.load_screen("test_promos"))
        layout.addWidget(promo_btn)
        
        # Test Event Promos button
        event_promo_btn = QPushButton("Test Event Promos")
        event_promo_btn.clicked.connect(lambda: self.load_screen("test_event_promos"))
        layout.addWidget(event_promo_btn)
        
        group.setLayout(layout)
        return group
    
    def create_debug_tools_group(self):
        """Create the debug tools group"""
        group = QGroupBox("Development Tools")
        layout = QVBoxLayout()
        
        # Diplomacy Manager button
        diplomacy_btn = QPushButton("Diplomacy Manager")
        diplomacy_btn.clicked.connect(lambda: self.load_screen("diplomacy_manager"))
        layout.addWidget(diplomacy_btn)
        
        # Debug Menu button
        debug_btn = QPushButton("Debug Menu")
        debug_btn.clicked.connect(lambda: self.load_screen("debug_menu"))
        layout.addWidget(debug_btn)
        
        group.setLayout(layout)
        return group
    
    def load_screen(self, screen_name):
        """Load a specific screen"""
        if self.load_screen_callback:
            self.load_screen_callback(screen_name)
    
    def return_to_game(self):
        """Return to the main game"""
        if self.load_screen_callback:
            self.load_screen_callback("news_feed") 