from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QGroupBox,
    QRadioButton, QHBoxLayout, QFormLayout, QSpacerItem, QSizePolicy, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from src.core.match_engine import get_all_wrestlers, load_wrestler_by_id
from src.ui.theme import apply_styles
from src.promo.promo_engine import PromoEngine
from src.ui.promo_test_ui import PromoDisplayWidget, PromoSummaryWidget
import random


class EventPromoUI(QWidget):
    """A streamlined promo UI specifically for event promos."""
    
    def __init__(self, wrestler, on_finish=None, diplomacy_system=None):
        super().__init__()
        self.wrestler = wrestler  # Pre-selected wrestler
        self.on_finish = on_finish
        self.diplomacy_system = diplomacy_system
        self.promo_result = None
        
        # Set size constraints
        self.setMinimumHeight(500)
        self.setMaximumHeight(800)
        
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create a scroll area to contain everything
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container widget for all content
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create header section
        header = QVBoxLayout()
        
        # Event badge with title
        title_row = QHBoxLayout()
        
        # Official event badge
        event_badge = QLabel("OFFICIAL EVENT")
        event_badge.setStyleSheet("""
            background-color: #9C27B0;
            color: white;
            font-weight: bold;
            font-family: Fira Code;
            padding: 5px 10px;
            border-radius: 5px;
        """)
        event_badge.setAlignment(Qt.AlignCenter)
        title_row.addWidget(event_badge)
        
        # Title
        title = QLabel(f"Promo: {self.wrestler['name']}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #fff; margin-bottom: 10px;")
        title_row.addWidget(title, 3)  # Give title more space
        
        header.addLayout(title_row)
        
        # Wrestler info
        info_box = QGroupBox("Wrestler Info")
        info_box.setStyleSheet("""
            QGroupBox {
                font-family: Fira Code;
                font-weight: bold;
                color: #66CCFF;
                border: 1px solid #444;
                border-radius: 8px;
                margin-top: 1em;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_box)
        
        # Wrestler stats
        stats_label = QLabel(f"Name: {self.wrestler['name']}\nReputation: {self.wrestler.get('reputation', 50)}")
        stats_label.setStyleSheet("color: #fff; font-family: Fira Code;")
        info_layout.addWidget(stats_label)
        
        header.addWidget(info_box)
        scroll_layout.addLayout(header)
        
        # Promo controls
        controls_box = QGroupBox("Promo Controls")
        controls_layout = QVBoxLayout(controls_box)
        
        # Select random tone and theme
        tones = ["boast", "challenge", "insult", "callout", "humble"]
        themes = ["legacy", "dominance", "betrayal", "power", "comeback", "respect"]
        
        self.selected_tone = random.choice(tones)
        self.selected_theme = random.choice(themes)
        
        # Show selected tone and theme
        tone_theme_label = QLabel(f"Tone: {self.selected_tone}\nTheme: {self.selected_theme}")
        tone_theme_label.setStyleSheet("color: #fff; font-family: Fira Code;")
        controls_layout.addWidget(tone_theme_label)
        
        # Start button
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Promo")
        self.start_button.clicked.connect(self.start_promo)
        apply_styles(self.start_button, "button_blue")
        button_layout.addWidget(self.start_button)
        
        controls_layout.addLayout(button_layout)
        scroll_layout.addWidget(controls_box)
        
        # Promo display
        self.promo_display = PromoDisplayWidget()
        self.promo_display.finished.connect(self.handle_promo_end)
        self.promo_display.setVisible(False)
        
        # Make sure the cash-in button is always visible for event promos
        self.promo_display.w1_cashin_button.setVisible(True)
        self.promo_display.w1_cashin_button.setStyleSheet("""
            QPushButton {
                background-color: #665500;
                color: #FFDD33;
                border: 2px solid gold;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
                animation: pulse 1s infinite;
            }
            QPushButton:hover {
                background-color: #776611;
            }
            QPushButton:disabled {
                background-color: #333;
                color: #777;
                border: 1px solid #555;
                animation: none;
            }
        """)
        
        scroll_layout.addWidget(self.promo_display)
        
        # Summary screen
        self.summary_screen = PromoSummaryWidget()
        self.summary_screen.continue_clicked.connect(self.handle_continue)
        self.summary_screen.setVisible(False)
        scroll_layout.addWidget(self.summary_screen)
        
        # Set the scroll content and add to main layout
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
    def start_promo(self):
        """Start the promo with the pre-selected wrestler."""
        # Disable start button
        self.start_button.setEnabled(False)
        
        # Hide the controls and show the promo display
        for i in range(self.layout().count()):
            if isinstance(self.layout().itemAt(i).widget(), QGroupBox):
                self.layout().itemAt(i).widget().setVisible(False)
        
        self.promo_display.setVisible(True)
        
        # Run the promo engine
        engine = PromoEngine(
            self.wrestler,
            tone=self.selected_tone,
            theme=self.selected_theme,
            opponent=None
        )
        result = engine.simulate()
        self.promo_result = result
        
        # Show the promo
        self.promo_display.set_wrestlers(self.wrestler)
        self.promo_display.set_beats(result["beats"])
    
    def handle_promo_end(self):
        """Called when the promo display is complete."""
        if self.promo_result:
            self.summary_screen.show_single_summary(self.promo_result)
            self.promo_display.setVisible(False)
            self.summary_screen.setVisible(True)
    
    def handle_continue(self):
        """Called when the user clicks continue after promo end."""
        if self.on_finish and self.promo_result:
            # Add event-specific details to the result
            self.promo_result["was_event_promo"] = True
            self.promo_result["promo_wrestler"] = self.wrestler["name"]
            
            # Pass the result back to the event summary screen
            self.on_finish(self.promo_result) 