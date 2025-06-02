from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QSizePolicy, QComboBox, QTextEdit,
    QProgressBar, QScrollArea, QFrame, QToolTip, QDialog, QTabWidget, QFormLayout,
    QGroupBox, QHeaderView, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject, QEvent, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont, QPalette, QPixmap, QIcon
from src.ui.theme import apply_styles
from src.ui.theme import ShadowTextLabel
from src.core.match_engine import simulate_match
from PyQt5.QtWidgets import QApplication
from src.storyline.storyline_manager import StorylineManager
from src.core.match_integrator import MatchIntegrator
import random
from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt
from src.db.commentary_utils import get_commentary_line
from PyQt5.QtWidgets import QLabel, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal
from src.core.diplomacy_hooks import handle_match_relationship_effects
from src.core.wrestler_stats import (
    get_wrestler_attr, calculate_strength, calculate_dexterity, 
    calculate_endurance, calculate_intelligence, calculate_charisma,
    calculate_overall_rating, get_grade_and_colour, get_star_rating
)
import time


SPEED_MAP = {
    "Slower": 3000,  # 3 seconds
    "Slow": 2000,    # 2 seconds
    "Normal": 1000,  # 1 second
    "Fast": 500,     # 0.5 seconds
    "Faster": 100,   # 0.1 seconds - was too fast at 10ms
}


W1_COLOUR = "#2c3e50"
W2_COLOUR = "#7f1d1d"


class MatchWorker(QObject):
    finished = pyqtSignal(dict)
    log = pyqtSignal(str, str)
    update = pyqtSignal(dict, dict)
    colour_commentary = pyqtSignal(str)
    stats_signal = pyqtSignal(dict)
    beat_complete = pyqtSignal()  # New signal to indicate a beat is ready for display

    def __init__(self, w1, w2, get_delay, stats_callback=None):
        super().__init__()
        self.w1 = w1
        self.w2 = w2
        self.get_delay = get_delay
        self.stats_callback = stats_callback
        self.latest_result = {}
        self.fast_mode = False
        self.paused = False
        self.beat_in_progress = False
        self.match_integrator = MatchIntegrator()
        
        # Track wrestler stats during the match
        self.w1_current = {'name': get_wrestler_attr(w1, 'name', 'Wrestler 1')}
        self.w2_current = {'name': get_wrestler_attr(w2, 'name', 'Wrestler 2')}
        
        print(f"DEBUG: MatchWorker initialized with wrestlers:")
        print(f"  W1: {get_wrestler_attr(w1, 'name', 'Unknown')}")
        print(f"  W2: {get_wrestler_attr(w2, 'name', 'Unknown')}")
    
    def get_wrestler_attr(self, wrestler, attr, default=None):
        """Safely get wrestler attribute regardless of if it's a class or dict"""
        if hasattr(wrestler, attr):
            return getattr(wrestler, attr)
        elif isinstance(wrestler, dict) and attr in wrestler:
            return wrestler[attr]
        
        # Special case for intelligence - use standard calculation function
        if attr == "intelligence":
            # Use the standard intelligence calculation function
            intelligence = calculate_intelligence(wrestler)
            print(f"DEBUG: Calculated intelligence={intelligence} using standard function")
            return intelligence
        
        return default

    def run(self):
        def log_callback(msg, attacker=None):
            # Just send the message and don't wait if in fast mode
            if self.fast_mode:
                self.log.emit(msg, attacker)
                return
                
            # For normal mode, emit message and wait for UI to process it
            self.log.emit(msg, attacker)
            
            # Wait for a maximum of 1 second to prevent deadlock
            start_time = time.time()
            self.beat_in_progress = True
            
            # More efficient wait loop with timeout
            while self.beat_in_progress and not self.paused and (time.time() - start_time) < 1.0:
                QThread.msleep(10)  # Short sleep for responsiveness
            
            # Add a small consistent delay between beats for readability
            current_delay = self.get_delay() // 4  # Use 1/4 of the main delay
            if current_delay > 0 and not self.paused:
                QThread.msleep(current_delay)
                
        def update_callback(w1_update, w2_update):
            # Track the most recent updates
            self.w1_current.update(w1_update)
            self.w2_current.update(w2_update)
            
            # Debug output
            print(f"DEBUG: Match engine sent wrestler updates:")
            print(f"  W1 update: stamina={w1_update.get('stamina', 'N/A')}, health={w1_update.get('health', 'N/A')}, damage={w1_update.get('damage_taken', 'N/A')}")
            print(f"  W2 update: stamina={w2_update.get('stamina', 'N/A')}, health={w2_update.get('health', 'N/A')}, damage={w2_update.get('damage_taken', 'N/A')}")
            
            # Make sure we're sending full copies with all the data
            w1_complete = self.w1_current.copy()
            w2_complete = self.w2_current.copy()
            
            # Send the update signal
            self.update.emit(w1_complete, w2_complete)

        def stats_callback(stats):
            # Debug the stats we're receiving
            print(f"DEBUG: Match engine sent stats update: {list(stats.keys())}")
            
            # Add w1/w2 current values to stats
            stats['w1_current'] = self.w1_current
            stats['w2_current'] = self.w2_current
            
            # Forward to UI
            self.stats_signal.emit(stats)

        # Use our integrator to simulate the match with statistics tracking
        print("DEBUG: Starting match simulation")
        result = self.match_integrator.simulate_match_with_tracking(
            self.w1,
            self.w2,
            log_function=log_callback,
            update_callback=update_callback,
            colour_callback=lambda line: self.colour_commentary.emit(line),
            stats_callback=stats_callback,
            fast_mode=self.fast_mode
        )
        self.latest_result = result
        print("DEBUG: Match simulation complete, emitting result")
        self.finished.emit(result)


class WrestlingMatchUI(QWidget):
    def __init__(self, wrestler1, wrestler2, on_next_match=None, fast_mode=False, diplomacy_system=None):
        super().__init__()
        self.w1 = wrestler1
        self.w2 = wrestler2
        self.on_next_match = on_next_match
        self.fast_mode = fast_mode
        self.diplomacy_system = diplomacy_system
        
        # Initialize latest wrestler data storage
        self.w1_latest = {}
        self.w2_latest = {}
        
        # Commentary setup
        self.current_commentary = []
        self.commentary_queue = []
        self.current_attacker = None
        self.current_beat = 1  # Track current beat number
        self.paused = False
        
        # Display timer setup
        self.display_timer = QTimer()
        self.display_timer.setSingleShot(True)
        self.display_timer.timeout.connect(self.process_next_beat)
        
        # Initialize these attributes early to prevent eventFilter issues
        self.left_name = None
        self.right_name = None
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        self.setContentsMargins(15, 10, 15, 10)  # Reduced margins
        self.layout.setSpacing(5)  # Reduced spacing

        # Build UI components
        self.build_top_row()
        self.build_info_bar()
        self.build_center()
        self.build_controls()

        QTimer.singleShot(100, self.run_match_threaded)
    
    def get_wrestler_attr(self, wrestler, attr, default=None):
        """Safely get wrestler attribute regardless of if it's a class or dict"""
        if hasattr(wrestler, attr):
            return getattr(wrestler, attr)
        elif isinstance(wrestler, dict) and attr in wrestler:
            return wrestler[attr]
        
        # Special case for intelligence - use standard calculation function
        if attr == "intelligence":
            # Use the standard intelligence calculation function
            intelligence = calculate_intelligence(wrestler)
            print(f"DEBUG: Calculated intelligence={intelligence} using standard function")
            return intelligence
        
        return default

    def build_top_row(self):
        top = QHBoxLayout()
        top.setSpacing(20)  # Add consistent spacing

        # Left wrestler block
        left_box = QVBoxLayout()
        left_box.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        left_box.setContentsMargins(0, 0, 0, 0)  # Remove margins
        left_box.setSpacing(0)  # Reduce spacing between elements
        
        # Create attribute block with key stats prominently displayed above the name
        self.left_stats = QLabel(self.format_wrestler_stats(self.w1))
        self.left_stats.setStyleSheet("font-family: Fira Code; font-size: 14pt; color: #d4af37;")
        self.left_stats.setFixedWidth(300)
        self.left_stats.setFixedHeight(60)  # Shorter height for the horizontal layout
        self.left_stats.setAlignment(Qt.AlignCenter)
        
        # Create name label with hover capabilities
        self.left_name = ShadowTextLabel(self.w1.name if hasattr(self.w1, 'name') else self.w1["name"])
        
        # Set up proper text handling for ellipsis
        self.left_name.setWordWrap(False)
        self.left_name.setFixedWidth(300)
        self.left_name.setFixedHeight(70)  # Shorter height
        self.left_name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Install event filter for hover functionality
        self.left_name.installEventFilter(self)
        
        # Use large font for names
        font = self.left_name.font()
        font.setPointSize(36)
        font.setBold(True)
        self.left_name.setFont(font)
        
        # Set ellipsis mode to truncate text properly
        self.left_name.setTextFormat(Qt.PlainText)
        
        self.left_name.setStyleSheet("""
            font-family: Georgia, serif;
            font-weight: bold;
            color: #2c3e50;
            padding: 12px;
            border-radius: 8px;
            text-align: left;
        """)

        # Add widgets to layout - stats first, then name
        left_box.addWidget(self.left_stats)
        left_box.addWidget(self.left_name)
        left_box.addStretch(1)

        # Right wrestler block
        right_box = QVBoxLayout()
        right_box.setAlignment(Qt.AlignRight | Qt.AlignTop)
        right_box.setContentsMargins(0, 0, 0, 0)  # Remove margins
        right_box.setSpacing(0)  # Reduce spacing between elements
        
        # Create attribute block with key stats prominently displayed above the name
        self.right_stats = QLabel(self.format_wrestler_stats(self.w2))
        self.right_stats.setStyleSheet("font-family: Fira Code; font-size: 14pt; color: #d4af37;")
        self.right_stats.setFixedWidth(300)
        self.right_stats.setFixedHeight(60)  # Shorter height for the horizontal layout
        self.right_stats.setAlignment(Qt.AlignCenter)
        
        # Create name label with hover capabilities
        self.right_name = ShadowTextLabel(self.w2.name if hasattr(self.w2, 'name') else self.w2["name"])
        
        # Set up proper text handling for ellipsis
        self.right_name.setWordWrap(False)
        self.right_name.setFixedWidth(300)
        self.right_name.setFixedHeight(70)  # Shorter height
        self.right_name.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Install event filter for hover functionality
        self.right_name.installEventFilter(self)
        
        # Use same font settings
        self.right_name.setFont(font)
        
        # Set ellipsis mode to truncate text properly
        self.right_name.setTextFormat(Qt.PlainText)
        
        self.right_name.setStyleSheet("""
            font-family: Georgia, serif;
            font-weight: bold;
            color: #7f1d1d;
            padding: 12px;
            border-radius: 8px;
            text-align: right;
        """)

        # Add widgets to layout - stats first, then name
        right_box.addWidget(self.right_stats)
        right_box.addWidget(self.right_name)
        right_box.addStretch(1)

        # Set stretch factors for the layout
        top.addLayout(left_box, 1)
        top.addStretch(1)  # Center spacer instead of momentum arrow
        top.addLayout(right_box, 1)

        self.layout.addLayout(top)

    def eventFilter(self, obj, event):
        """Handle hover events for wrestler names to show full stats"""
        # Only handle events if the UI widgets are fully initialized
        if hasattr(self, 'left_name') and hasattr(self, 'right_name') and self.left_name is not None and self.right_name is not None:
            if obj in [self.left_name, self.right_name]:
                if event.type() == QEvent.Enter:
                    # On hover, show detailed stats in a rich tooltip
                    wrestler = self.w1 if obj == self.left_name else self.w2
                    tooltip_text = self.format_full_stats(wrestler)
                    QApplication.setOverrideCursor(Qt.ArrowCursor)  # Ensure normal cursor during tooltip
                    QToolTip.showText(event.globalPos(), tooltip_text, obj)  # Show tooltip
                    # Set a longer timeout for tooltips globally
                    QApplication.instance().setStyleSheet("QToolTip { opacity: 255; }")
                    return True
                elif event.type() == QEvent.Leave:
                    QApplication.restoreOverrideCursor()
                    return True
        return super().eventFilter(obj, event)

    def format_full_stats(self, wrestler):
        """Format wrestler's full stats for tooltip display"""
        # Get core stats
        name = self.get_wrestler_attr(wrestler, "name", "Unknown Wrestler")
        charisma = self.get_wrestler_attr(wrestler, "charisma", 0)
        strength = self.get_wrestler_attr(wrestler, "strength", 0)
        dexterity = self.get_wrestler_attr(wrestler, "dexterity", 0)
        stamina = self.get_wrestler_attr(wrestler, "stamina", 0)
        rep = self.get_wrestler_attr(wrestler, "rep", 0)
        
        # Check if we should use the latest match data for health/stamina
        if hasattr(self, 'w1_latest') and hasattr(self, 'w2_latest'):
            w1_name = self.get_wrestler_attr(self.w1, 'name', 'Unknown')
            if name == w1_name and self.w1_latest:
                # Use the updated values
                stamina = self.get_wrestler_attr(self.w1_latest, 'stamina', stamina)
                health = self.get_wrestler_attr(self.w1_latest, 'health', 100)
                damage = self.get_wrestler_attr(self.w1_latest, 'damage_taken', 0)
            else:
                w2_name = self.get_wrestler_attr(self.w2, 'name', 'Unknown')
                if name == w2_name and self.w2_latest:
                    # Use the updated values
                    stamina = self.get_wrestler_attr(self.w2_latest, 'stamina', stamina)
                    health = self.get_wrestler_attr(self.w2_latest, 'health', 100)
                    damage = self.get_wrestler_attr(self.w2_latest, 'damage_taken', 0)
                else:
                    health = 100
                    damage = 0
        else:
            health = 100
            damage = 0
        
        # Get extended attributes if available
        attributes = {}
        if hasattr(wrestler, "attributes"):
            attributes = wrestler.attributes
        elif isinstance(wrestler, dict) and "attributes" in wrestler:
            attributes = wrestler["attributes"]
        
        # Format HTML for tooltip with improved styling
        html = f"""
        <div style='background-color:#222; padding:15px; border-radius:8px; min-width:350px; box-shadow: 0 4px 8px rgba(0,0,0,0.5);'>
            <h2 style='color:#eee; margin:0 0 15px 0; border-bottom:1px solid #444; padding-bottom:8px;'>{name}</h2>
            
            <div style='margin-bottom:15px;'>
                <div style='color:#ffd700; font-size:14pt; margin-bottom:10px;'>Reputation: {rep}</div>
                
                <div style='display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:15px;'>
                    <div style='background:#2c3e50; padding:8px; border-radius:4px;'>
                        <span style='color:#e67e22; font-weight:bold; font-size:12pt;'>CHR:</span> 
                        <span style='color:#eee; font-size:12pt;'>{charisma}</span>
                    </div>
                    <div style='background:#7f1d1d; padding:8px; border-radius:4px;'>
                        <span style='color:#c0392b; font-weight:bold; font-size:12pt;'>STR:</span> 
                        <span style='color:#eee; font-size:12pt;'>{strength}</span>
                    </div>
                    <div style='background:#1a365d; padding:8px; border-radius:4px;'>
                        <span style='color:#3498db; font-weight:bold; font-size:12pt;'>DEX:</span> 
                        <span style='color:#eee; font-size:12pt;'>{dexterity}</span>
                    </div>
                    <div style='background:#1e3a29; padding:8px; border-radius:4px;'>
                        <span style='color:#2ecc71; font-weight:bold; font-size:12pt;'>STA:</span> 
                        <span style='color:#eee; font-size:12pt;'>{stamina:.1f}</span>
                    </div>
                </div>
                
                <div style='display:grid; grid-template-columns:1fr 1fr; gap:10px;'>
                    <div style='background:#133337; padding:8px; border-radius:4px;'>
                        <span style='color:#9be7ff; font-weight:bold; font-size:12pt;'>Current Stamina:</span> 
                        <span style='color:#eee; font-size:12pt;'>{stamina:.1f}</span>
                    </div>
                    <div style='background:#331313; padding:8px; border-radius:4px;'>
                        <span style='color:#ff6347; font-weight:bold; font-size:12pt;'>Damage Taken:</span> 
                        <span style='color:#eee; font-size:12pt;'>{damage:.1f}</span>
                    </div>
                </div>
            </div>
        """
        
        # Add extended attributes if available
        if attributes:
            html += "<h3 style='color:#ffd700; margin:15px 0 10px 0; border-bottom:1px solid #444; padding-bottom:5px;'>Extended Attributes</h3>"
            html += "<div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px;'>"
            
            # Add attributes in a grid
            for name, value in attributes.items():
                html += f"""
                <div style='background:#333; padding:6px; border-radius:4px;'>
                    <span style='color:#bbb; font-weight:bold;'>{name.upper()[:3]}:</span> 
                    <span style='color:#eee;'>{value}</span>
                </div>
                """
            
            html += "</div>"
        
        html += "</div>"
        return html

    def build_center(self):
        mid = QHBoxLayout()

        # Commentary box using QTextEdit with improved styling
        self.commentary_box = QTextEdit()
        self.commentary_box.setReadOnly(True)
        self.commentary_box.setFixedSize(800, 400)
        self.commentary_box.setStyleSheet("""
            QTextEdit {
                font-family: Fira Code;
                font-size: 16pt;
                color: #eeeeee;
                background-color: #1a1a1a;
                border: 1px solid #333;
                padding: 16px;
                line-height: 1.5;
            }
            QTextEdit QScrollBar:vertical {
                background: #1a1a1a;
                width: 12px;
                margin: 0;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: #444;
                border-radius: 6px;
                min-height: 20px;
            }
            QTextEdit QScrollBar::add-line:vertical,
            QTextEdit QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        mid.addWidget(self.commentary_box)

        # Stats panel
        self.stats_panel = QVBoxLayout()
        self.stats_panel.setSpacing(6)
        stats_frame = QWidget()
        stats_frame.setLayout(self.stats_panel)
        stats_frame.setStyleSheet("""
            background-color: #222;
            border: 1px solid #444;
            padding: 10px;
        """)
        mid.addWidget(stats_frame, 1)
        self.layout.addLayout(mid)

        # Init stat labels
        self.stat_labels = {}
        # Get wrestler names safely
        w1_name = self.get_wrestler_attr(self.w1, "name", "Wrestler 1")
        w2_name = self.get_wrestler_attr(self.w2, "name", "Wrestler 2")
        
        keys = [
            "Match Quality", "Fan Reaction",
            f"{w1_name} Hits", f"{w2_name} Hits",
            f"{w1_name} Reversals", f"{w2_name} Reversals",
            f"{w1_name} Misses", f"{w2_name} Misses",
            "Flow Streak", "Drama Score", "False Finishes",
            "Signatures Landed", "Turns"
        ]
        for key in keys:
            label = QLabel(f"{key}: 0")
            label.setStyleSheet("font-family: Fira Code; font-size: 12pt; color: #ccc;")
            self.stat_labels[key] = label
            self.stats_panel.addWidget(label)



    def build_controls(self):
        control_row = QHBoxLayout()

        # Speed Slider
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(4)
        self.speed_slider.setValue(2)  # Default: "Normal"
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(1)
        self.speed_slider.setFixedWidth(200)

        self.speed_labels = ["Slower", "Slow", "Normal", "Fast", "Faster"]

        self.speed_label_display = QLabel(self.speed_labels[self.speed_slider.value()])
        self.speed_label_display.setStyleSheet("font-family: Fira Code; color: #ccc;")
        self.speed_slider.valueChanged.connect(
            lambda value: self.speed_label_display.setText(self.speed_labels[value])
        )

        control_row.addWidget(QLabel("Speed:"))
        control_row.addWidget(self.speed_slider)
        control_row.addWidget(self.speed_label_display)

        # Play/Pause toggle
        self.pause_button = QPushButton("Pause")
        apply_styles(self.pause_button, "button_flat")
        self.pause_button.setCheckable(True)
        self.pause_button.clicked.connect(self.toggle_pause)
        control_row.addWidget(self.pause_button)

        # Finish Match button
        self.finish_button = QPushButton("Finish Match")
        apply_styles(self.finish_button, "button_red")
        self.finish_button.clicked.connect(self.finish_match_quick)
        control_row.addWidget(self.finish_button)

        # Continue button
        self.continue_button = QPushButton("Continue")
        apply_styles(self.continue_button, "button_blue")
        self.continue_button.setVisible(False)
        self.continue_button.clicked.connect(self.handle_continue)
        control_row.addStretch()
        control_row.addWidget(self.continue_button)

        self.layout.addLayout(control_row)

    def update_stats(self, updated1, updated2):
        # Store the updated values for later use
        # Maps the data by name since the order might not match
        w1_name = self.get_wrestler_attr(self.w1, 'name', 'Wrestler 1')
        w2_name = self.get_wrestler_attr(self.w2, 'name', 'Wrestler 2')
        
        # DEBUG: Print what we're receiving
        print(f"DEBUG: update_stats received data for wrestlers:")
        print(f"  Data1: name={self.get_wrestler_attr(updated1, 'name', 'Unknown')}, stamina={self.get_wrestler_attr(updated1, 'stamina', 'N/A')}, health={self.get_wrestler_attr(updated1, 'health', 'N/A')}, damage={self.get_wrestler_attr(updated1, 'damage_taken', 'N/A')}")
        print(f"  Data2: name={self.get_wrestler_attr(updated2, 'name', 'Unknown')}, stamina={self.get_wrestler_attr(updated2, 'stamina', 'N/A')}, health={self.get_wrestler_attr(updated2, 'health', 'N/A')}, damage={self.get_wrestler_attr(updated2, 'damage_taken', 'N/A')}")
        
        # Store the updated data for use in other methods
        if self.get_wrestler_attr(updated1, 'name', '') == w1_name:
            self.w1_latest = updated1
            self.w2_latest = updated2
            
            # Add mental attributes for intelligence calculation
            if hasattr(self, 'w1_mental') and self.w1_mental:
                if isinstance(self.w1_latest, dict):
                    self.w1_latest.update(self.w1_mental)
            if hasattr(self, 'w2_mental') and self.w2_mental:
                if isinstance(self.w2_latest, dict):
                    self.w2_latest.update(self.w2_mental)
        else:
            self.w1_latest = updated2
            self.w2_latest = updated1
            
            # Add mental attributes for intelligence calculation
            if hasattr(self, 'w1_mental') and self.w1_mental:
                if isinstance(self.w1_latest, dict):
                    self.w1_latest.update(self.w1_mental)
            if hasattr(self, 'w2_mental') and self.w2_mental:
                if isinstance(self.w2_latest, dict):
                    self.w2_latest.update(self.w2_mental)
        
        # Update name labels
        self.left_name.setText(w1_name)
        self.right_name.setText(w2_name)
        
        # Get updated stamina and health values
        w1_stamina = self.get_wrestler_attr(self.w1_latest, 'stamina', 100) 
        w2_stamina = self.get_wrestler_attr(self.w2_latest, 'stamina', 100)
        w1_health = self.get_wrestler_attr(self.w1_latest, 'health', 100)
        w2_health = self.get_wrestler_attr(self.w2_latest, 'health', 100)
        w1_damage = self.get_wrestler_attr(self.w1_latest, 'damage_taken', 0)
        w2_damage = self.get_wrestler_attr(self.w2_latest, 'damage_taken', 0)
        
        # DEBUG: Print what we've extracted
        print(f"DEBUG: Extracted stats for UI update:")
        print(f"  {w1_name}: stamina={w1_stamina}, health={w1_health}, damage={w1_damage}")
        print(f"  {w2_name}: stamina={w2_stamina}, health={w2_health}, damage={w2_damage}")
        
        # Alternative way to get values if not found directly
        if w1_stamina == 100 and isinstance(self.w1_latest, dict):
            # Try to get stamina_drained if stamina is not available
            w1_stamina_drained = self.get_wrestler_attr(self.w1_latest, 'stamina_drained', 0)
            if w1_stamina_drained > 0:
                w1_stamina = max(0, 100 - w1_stamina_drained)
                print(f"DEBUG: Used stamina_drained for {w1_name}: {w1_stamina}")
                
        if w2_stamina == 100 and isinstance(self.w2_latest, dict):
            # Try to get stamina_drained if stamina is not available
            w2_stamina_drained = self.get_wrestler_attr(self.w2_latest, 'stamina_drained', 0)
            if w2_stamina_drained > 0:
                w2_stamina = max(0, 100 - w2_stamina_drained)
                print(f"DEBUG: Used stamina_drained for {w2_name}: {w2_stamina}")
            
        # Calculate damage as 100 - health or directly from damage_taken
        if w1_damage == 0 and w1_health < 100:
            w1_damage = 100 - w1_health
            print(f"DEBUG: Calculated damage from health for {w1_name}: {w1_damage}")
        
        if w2_damage == 0 and w2_health < 100:
            w2_damage = 100 - w2_health
            print(f"DEBUG: Calculated damage from health for {w2_name}: {w2_damage}")
        
        # If we have damage_taken but not health, calculate health
        if w1_health == 100 and w1_damage > 0:
            w1_health = max(0, 100 - w1_damage)
            print(f"DEBUG: Calculated health from damage for {w1_name}: {w1_health}")
            
        if w2_health == 100 and w2_damage > 0:
            w2_health = max(0, 100 - w2_damage)
            print(f"DEBUG: Calculated health from damage for {w2_name}: {w2_health}")
        
        # Make sure we're using floats for display
        w1_stamina = float(w1_stamina)
        w2_stamina = float(w2_stamina)
        w1_damage = float(w1_damage)
        w2_damage = float(w2_damage)
        
        # Update the UI with new values - directly update stat labels
        self.update_stamina_label(self.left_stamina, w1_stamina)
        self.update_stamina_label(self.right_stamina, w2_stamina)
        self.update_damage_label(self.left_damage, w1_damage)
        self.update_damage_label(self.right_damage, w2_damage)
        
        # DEBUG: Print what we're updating in the UI
        print(f"DEBUG: Updating UI with:")
        print(f"  {w1_name}: stamina={w1_stamina}, damage={w1_damage}")
        print(f"  {w2_name}: stamina={w2_stamina}, damage={w2_damage}")
        
        # Also update the wrestler stat displays at the top
        self.left_stats.setText(self.format_wrestler_stats(self.w1_latest))
        self.right_stats.setText(self.format_wrestler_stats(self.w2_latest))
        
        # We've removed the momentum arrow, so we don't need to update it anymore

    def update_live_stats(self, stats):
        if not stats or not isinstance(stats, dict):
            return

        # DEBUG: Print the incoming stats
        print(f"DEBUG: update_live_stats received: {stats.keys()}")
        
        if 'stamina_drain' in stats:
            print(f"DEBUG: stamina_drain = {stats['stamina_drain']}")
        if 'health_remaining' in stats:
            print(f"DEBUG: health_remaining = {stats['health_remaining']}")
        if 'damage' in stats:
            print(f"DEBUG: damage = {stats['damage']}")

        # Extract wrestler names
        w1_name = self.get_wrestler_attr(self.w1, 'name', 'Wrestler 1')
        w2_name = self.get_wrestler_attr(self.w2, 'name', 'Wrestler 2')
        
        # Update stat labels with match information
        self.stat_labels["Match Quality"].setText(f"Match Quality: {stats.get('quality', 0)}")
        self.stat_labels["Fan Reaction"].setText(f"Fan Reaction: {stats.get('reaction', '...')}")
        
        # Update hit/reversal/miss counters
        hits = stats.get("hits", {})
        revs = stats.get("reversals", {})
        misses = stats.get("misses", {})
        
        # Ensure dictionaries are properly formatted
        if isinstance(hits, int):
            hits = {w1_name: hits // 2, w2_name: hits // 2}
        if isinstance(revs, int):
            revs = {w1_name: revs // 2, w2_name: revs // 2}
        if isinstance(misses, int):
            misses = {w1_name: misses // 2, w2_name: misses // 2}
            
        # Update individual wrestler stats
        for who in [w1_name, w2_name]:
            self.stat_labels[f"{who} Hits"].setText(f"{who} Hits: {hits.get(who, 0)}")
            self.stat_labels[f"{who} Reversals"].setText(f"{who} Reversals: {revs.get(who, 0)}")
            self.stat_labels[f"{who} Misses"].setText(f"{who} Misses: {misses.get(who, 0)}")
            
        # Update other match stats
        self.stat_labels["Flow Streak"].setText(f"Flow Streak: {stats.get('flow_streak', 0)}")
        self.stat_labels["Drama Score"].setText(f"Drama Score: {stats.get('drama_score', 0)}")
        self.stat_labels["False Finishes"].setText(f"False Finishes: {stats.get('false_finishes', 0)}")
        self.stat_labels["Signatures Landed"].setText(f"Signatures Landed: {stats.get('sig_moves_landed', 0)}")
        self.stat_labels["Turns"].setText(f"Match Length: {stats.get('turns', 0)} turns")
        
        # Convert quality to star rating
        quality = stats.get("quality", 0)
        
        # Set star rating based on quality
        if quality >= 91:
            stars = "★★★★★"
        elif quality >= 81:
            stars = "★★★★☆"
        elif quality >= 61:
            stars = "★★★☆☆"
        elif quality >= 41:
            stars = "★★☆☆☆"
        elif quality >= 21:
            stars = "★☆☆☆☆"
        else:
            stars = "☆☆☆☆☆"
        
        self.match_quality_stars.setText(stars)
        
        # Create a copy of current wrestler data if we don't have it yet
        if not hasattr(self, 'w1_latest') or not self.w1_latest:
            self.w1_latest = {'name': w1_name, 'stamina': 100, 'health': 100, 'damage_taken': 0}
        if not hasattr(self, 'w2_latest') or not self.w2_latest:
            self.w2_latest = {'name': w2_name, 'stamina': 100, 'health': 100, 'damage_taken': 0}
        
        # Update stamina and damage values from the stats
        w1_stamina = self.get_wrestler_attr(self.w1_latest, 'stamina', 100)
        w2_stamina = self.get_wrestler_attr(self.w2_latest, 'stamina', 100)
        w1_damage = self.get_wrestler_attr(self.w1_latest, 'damage_taken', 0)
        w2_damage = self.get_wrestler_attr(self.w2_latest, 'damage_taken', 0)
        
        # Get stamina values from stats
        stamina_drain = stats.get("stamina_drain", {})
        if isinstance(stamina_drain, dict):
            if w1_name in stamina_drain:
                w1_stamina = max(0, 100 - stamina_drain.get(w1_name, 0))
                # Update our latest data
                if isinstance(self.w1_latest, dict):
                    self.w1_latest['stamina'] = w1_stamina
                print(f"DEBUG: Updated {w1_name} stamina from stats: {w1_stamina}")
                
            if w2_name in stamina_drain:
                w2_stamina = max(0, 100 - stamina_drain.get(w2_name, 0))
                # Update our latest data
                if isinstance(self.w2_latest, dict):
                    self.w2_latest['stamina'] = w2_stamina
                print(f"DEBUG: Updated {w2_name} stamina from stats: {w2_stamina}")
        
        # Get health/damage values from stats
        health_remaining = stats.get("health_remaining", {})
        if isinstance(health_remaining, dict):
            if w1_name in health_remaining:
                w1_health = health_remaining.get(w1_name, 100)
                w1_damage = 100 - w1_health
                # Update our latest data
                if isinstance(self.w1_latest, dict):
                    self.w1_latest['health'] = w1_health
                    self.w1_latest['damage_taken'] = w1_damage
                print(f"DEBUG: Updated {w1_name} health/damage from stats: health={w1_health}, damage={w1_damage}")
                
            if w2_name in health_remaining:
                w2_health = health_remaining.get(w2_name, 100)
                w2_damage = 100 - w2_health
                # Update our latest data
                if isinstance(self.w2_latest, dict):
                    self.w2_latest['health'] = w2_health
                    self.w2_latest['damage_taken'] = w2_damage
                print(f"DEBUG: Updated {w2_name} health/damage from stats: health={w2_health}, damage={w2_damage}")
        else:
            # If health_remaining isn't available, try to get damage directly
            damage = stats.get("damage", {})
            if isinstance(damage, dict):
                if w1_name in damage:
                    w1_damage = damage.get(w1_name, 0)
                    # Update our latest data
                    if isinstance(self.w1_latest, dict):
                        self.w1_latest['damage_taken'] = w1_damage
                        self.w1_latest['health'] = max(0, 100 - w1_damage)
                    print(f"DEBUG: Updated {w1_name} damage from stats: {w1_damage}")
                    
                if w2_name in damage:
                    w2_damage = damage.get(w2_name, 0)
                    # Update our latest data
                    if isinstance(self.w2_latest, dict):
                        self.w2_latest['damage_taken'] = w2_damage
                        self.w2_latest['health'] = max(0, 100 - w2_damage)
                    print(f"DEBUG: Updated {w2_name} damage from stats: {w2_damage}")
        
        # Make sure values are capped appropriately and converted to float
        w1_stamina = float(max(0, min(100, w1_stamina)))
        w2_stamina = float(max(0, min(100, w2_stamina)))
        w1_damage = float(max(0, min(100, w1_damage)))
        w2_damage = float(max(0, min(100, w2_damage)))
        
        # Update the UI with the latest values
        self.update_stamina_label(self.left_stamina, w1_stamina)
        self.update_stamina_label(self.right_stamina, w2_stamina)
        self.update_damage_label(self.left_damage, w1_damage)
        self.update_damage_label(self.right_damage, w2_damage)
        
        # DEBUG: Print what we've updated in the UI
        print(f"DEBUG: Live stats UI update:")
        print(f"  {w1_name}: stamina={w1_stamina}, damage={w1_damage}")
        print(f"  {w2_name}: stamina={w2_stamina}, damage={w2_damage}")

    def get_speed_delay(self):
        """Get the current delay based on speed setting."""
        return list(SPEED_MAP.values())[self.speed_slider.value()]


    def run_match_threaded(self):
        def get_delay():
            return list(SPEED_MAP.values())[self.speed_slider.value()]

        self.worker = MatchWorker(self.w1, self.w2, get_delay)
        self.worker.stats_signal.connect(self.update_live_stats)
        
        self.worker.fast_mode = self.fast_mode
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        self.worker.log.connect(self.queue_beat)
        self.worker.colour_commentary.connect(self.update_colour_commentary)
        self.worker.update.connect(self.update_stats)
        self.worker.finished.connect(self.on_match_complete)
        self.worker.beat_complete.connect(self.on_beat_completed)

        # Store mental attributes for intelligence calculation
        self.w1_mental = {}
        self.w2_mental = {}
        
        # Extract mental attributes for intelligence calculation - use more robust method
        try:
            # For wrestler 1
            if hasattr(self.w1, "get_attribute"):
                try:
                    self.w1_mental = {
                        "focus": self.w1.get_attribute("focus"),
                        "risk_assessment": self.w1.get_attribute("risk_assessment"),
                        "adaptability": self.w1.get_attribute("adaptability")
                    }
                    print(f"DEBUG: Extracted w1 mental stats via get_attribute: {self.w1_mental}")
                except Exception as e:
                    print(f"DEBUG: Error with w1.get_attribute: {e}")
            
            if not self.w1_mental and hasattr(self.w1, "attributes"):
                self.w1_mental = {
                    "focus": self.w1.attributes.get("focus", 10),
                    "risk_assessment": self.w1.attributes.get("risk_assessment", 10),
                    "adaptability": self.w1.attributes.get("adaptability", 10)
                }
                print(f"DEBUG: Extracted w1 mental stats via attributes: {self.w1_mental}")
                
            # For wrestler 2
            if hasattr(self.w2, "get_attribute"):
                try:
                    self.w2_mental = {
                        "focus": self.w2.get_attribute("focus"),
                        "risk_assessment": self.w2.get_attribute("risk_assessment"),
                        "adaptability": self.w2.get_attribute("adaptability")
                    }
                    print(f"DEBUG: Extracted w2 mental stats via get_attribute: {self.w2_mental}")
                except Exception as e:
                    print(f"DEBUG: Error with w2.get_attribute: {e}")
            
            if not self.w2_mental and hasattr(self.w2, "attributes"):
                self.w2_mental = {
                    "focus": self.w2.attributes.get("focus", 10),
                    "risk_assessment": self.w2.attributes.get("risk_assessment", 10),
                    "adaptability": self.w2.attributes.get("adaptability", 10)
                }
                print(f"DEBUG: Extracted w2 mental stats via attributes: {self.w2_mental}")
            
            # Store the original wrestlers for later use
            self.original_w1 = self.w1
            self.original_w2 = self.w2
            
            print(f"DEBUG: Mental attributes for intelligence calculation:")
            print(f"  W1 mental: {self.w1_mental}")
            print(f"  W2 mental: {self.w2_mental}")
        except Exception as e:
            print(f"DEBUG: Error extracting mental attributes: {e}")

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def queue_beat(self, message, attacker):
        """Queue a beat for display without blocking the simulation thread."""
        if not message.strip():
            return
            
        # Fix attacker identification if it's not correctly set by the match engine
        w1_name = self.get_wrestler_attr(self.w1, "name", "")
        w2_name = self.get_wrestler_attr(self.w2, "name", "")
        
        if attacker is None or attacker == "":
            # Try to determine attacker from message content
            if w1_name in message and (message.startswith(w1_name) or message.startswith(f"{w1_name} ")):
                attacker = "w1"
                print(f"DEBUG: Auto-detected attacker as w1 from message: {message[:40]}...")
            elif w2_name in message and (message.startswith(w2_name) or message.startswith(f"{w2_name} ")):
                attacker = "w2"
                print(f"DEBUG: Auto-detected attacker as w2 from message: {message[:40]}...")
        
        # Always print debugging information about the attacker
        print(f"DEBUG: Queue_beat with message: '{message[:40]}...' and attacker: {attacker}")
            
        # Add to the queue
        self.commentary_queue.append((message, attacker))
        
        # Start processing if not already in progress
        if not self.display_timer.isActive() and len(self.commentary_queue) == 1:
            self.process_next_beat()

    def process_next_beat(self):
        """Process the next beat in the queue."""
        if not self.commentary_queue or self.paused:
            return
            
        # Get the next beat
        message, attacker = self.commentary_queue.pop(0)
        
        # Debug what attacker we're receiving
        print(f"DEBUG: process_next_beat received message with attacker={attacker}")
        
        # Clear the commentary box first
        self.commentary_box.clear()

        # Format the line based on the attacker
        if attacker == "w1":
            color = W1_COLOUR  # Blue color for Wrestler 1
            bg_color = "#1a2a3a"  # Dark blue background
            print(f"DEBUG: Using W1 colors: {color}, bg={bg_color}")
        elif attacker == "w2":
            color = W2_COLOUR  # Red color for Wrestler 2
            bg_color = "#3a1a1a"  # Dark red background
            print(f"DEBUG: Using W2 colors: {color}, bg={bg_color}")
        else:
            color = "#1c1c1c"  # Dark color for neutral commentary
            bg_color = "#1a1a1a"  # Neutral dark background
            print(f"DEBUG: Using neutral colors: {color}, bg={bg_color}")

        # Parse momentum and confidence changes
        momentum_info = ""
        if "🌟" in message:
            parts = message.split("(")
            if len(parts) > 1:
                momentum_info = parts[1].strip(")")
                message = parts[0].strip()

        # Get wrestler names for clear identification
        w1_name = self.get_wrestler_attr(self.w1, 'name', 'Wrestler 1')
        w2_name = self.get_wrestler_attr(self.w2, 'name', 'Wrestler 2')
        
        print(f"DEBUG: Wrestler names: W1={w1_name}, W2={w2_name}")

        # Create beat HTML with wrestler-specific styling
        beat_html = f"""
            <div style='
                background-color: {bg_color};
                margin: 12px 0;
                padding: 16px;
                border-radius: 8px;
                border-left: 4px solid {color};
                font-family: Fira Code;
            '>
                <div style='
                    font-size: 16pt;
                    color: #eeeeee;
                    margin-bottom: 8px;
                    padding: 8px;
                    background-color: {color};
                    border-radius: 4px;
                '>Beat {self.current_beat}: {message}</div>
        """

        # Add momentum information if present
        if momentum_info:
            beat_html += f"""
                <div style='
                    font-size: 14pt;
                    color: #ffd700;
                    margin: 8px 0;
                    padding: 4px 8px;
                    background-color: #2a2a2a;
                    border-radius: 4px;
                    display: inline-block;
                '>⚡ {momentum_info}</div>
            """

        # Add any queued commentary for this beat with wrestler-specific colors
        for commentary in self.current_commentary:
            # Determine which wrestler is speaking based on name presence
            commentary_color = "#444444"  # Default gray
            commentary_bg = "#2a2a2a"     # Default background
            
            if w1_name in commentary:
                commentary_color = W1_COLOUR  # Blue for wrestler 1
                commentary_bg = "#1a2a3a"     # Blue-tinted background
            elif w2_name in commentary:
                commentary_color = W2_COLOUR  # Red for wrestler 2
                commentary_bg = "#3a1a1a"     # Red-tinted background
                
            beat_html += f"""
                <div style='
                    margin: 8px 16px;
                    padding: 8px 12px;
                    background-color: {commentary_bg};
                    border-radius: 4px;
                    font-family: Fira Code;
                    font-size: 14pt;
                    font-style: italic;
                    color: #aaaaaa;
                    border-left: 3px solid {commentary_color};
                '>{commentary}</div>
            """

        beat_html += "</div>"

        # Insert the beat immediately
        cursor = self.commentary_box.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertHtml(beat_html)
        
        # Ensure the new content is visible
        self.commentary_box.setTextCursor(cursor)
        self.commentary_box.ensureCursorVisible()

        # Clear current commentary for next beat
        self.current_commentary = []
        self.current_beat += 1

        # Don't call update_stats here - it's triggering an additional update
        # that resets the wrestler values

        # Signal the worker that we've processed this beat
        if hasattr(self, 'worker') and self.worker.beat_in_progress:
            self.worker.beat_in_progress = False
            
        # Schedule processing of next beat after delay
        if self.commentary_queue:
            # Use a much shorter delay in fast mode
            if hasattr(self, 'fast_mode') and self.fast_mode:
                delay = 10  # Very short delay in fast mode
            else:
                delay = self.get_speed_delay()
                
            # Make sure delay is not zero to avoid UI freezing
            delay = max(10, delay)
            self.display_timer.start(delay)
        elif hasattr(self, 'worker'):
            # Ensure we're not stuck waiting
            self.worker.beat_in_progress = False
            
        # Force UI update to ensure smooth display
        QApplication.processEvents()

    def on_beat_completed(self):
        """Handle signal that a beat is complete."""
        if hasattr(self, 'worker'):
            self.worker.beat_in_progress = False

    def update_colour_commentary(self, line):
        """Add commentary to the current beat."""
        if not line.strip():
            return
        self.current_commentary.append(line)

    def on_match_complete(self, result):
        """Handle post-match processing."""
        # Print debug info about the match result
        print(f"DEBUG: Match result received with keys: {list(result.keys())}")
        if 'winner' in result:
            print(f"DEBUG: Winner: {result['winner']}")
        if 'loser' in result:
            print(f"DEBUG: Loser: {result['loser']}")
        if 'match_quality' in result:
            print(f"DEBUG: Match quality: {result['match_quality']}")
        if 'highlights' in result:
            print(f"DEBUG: Number of highlights: {len(result['highlights'])}")
        if 'move_history' in result:
            print(f"DEBUG: Move history entries: {len(result['move_history'])}")
            
        self.match_result = result
        
        # Show the match summary after a short delay
        QTimer.singleShot(1000, lambda: self.show_post_match_summary(result))
        
        # Process match end effects
        self.handle_match_end(result)
        
        # If we're in fast mode, auto-continue
        if self.fast_mode and self.on_next_match:
            QTimer.singleShot(3000, self.handle_continue)
            
    def show_post_match_summary(self, result):
        """
        Show the post-match summary dialog with enhanced match data.
        """
        # Create dialog and layout
        dialog = QDialog(self)
        dialog.setWindowTitle("Match Summary")
        dialog.setMinimumWidth(600)
        dialog.setStyleSheet("""
            background-color: #1a1a1a;
            color: #e0e0e0;
            font-family: Fira Code;
        """)
        
        # Create a tab widget for different sections
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid #444;
                background-color: #222;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #333;
                color: #ccc;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0066cc;
                color: white;
                font-weight: bold;
            }
        """)
        
        # Create the tabs
        result_tab = QWidget()
        stats_tab = QWidget()
        psychology_tab = QWidget()  # Tab for psychology insights
        moves_tab = QWidget()  # Tab for move history
        
        # Set up layouts for each tab
        result_layout = QVBoxLayout(result_tab)
        stats_layout = QVBoxLayout(stats_tab)
        psychology_layout = QVBoxLayout(psychology_tab)
        moves_layout = QVBoxLayout(moves_tab)
        
        # Ensure we have winner and loser data
        winner_name = "Unknown"
        loser_name = "Unknown"
        
        if 'winner' in result and isinstance(result['winner'], str):
            winner_name = result['winner']
        elif 'winner_object' in result:
            winner_name = self.get_wrestler_attr(result['winner_object'], 'name', 'Unknown')
        
        if 'loser' in result and isinstance(result['loser'], str):
            loser_name = result['loser']
        elif 'loser_object' in result:
            loser_name = self.get_wrestler_attr(result['loser_object'], 'name', 'Unknown')
            
        print(f"DEBUG: Using winner_name={winner_name}, loser_name={loser_name} for match summary")
        
        # Add main result to the result tab
        winner_label = QLabel(f"<h1>{winner_name} defeated {loser_name}</h1>")
        winner_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        winner_label.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(winner_label)
        
        # Match quality with star rating - using same system as in the UI
        match_quality = result.get("match_quality", 0)
        if match_quality == 0:
            match_quality = result.get("quality", 0)
            
        print(f"DEBUG: Match quality for display: {match_quality}")
        
        # Convert quality to star rating using the same logic as update_live_stats
        if match_quality >= 91:
            stars = "★★★★★"
        elif match_quality >= 81:
            stars = "★★★★☆"
        elif match_quality >= 61:
            stars = "★★★☆☆"
        elif match_quality >= 41:
            stars = "★★☆☆☆"
        elif match_quality >= 21:
            stars = "★☆☆☆☆"
        else:
            stars = "☆☆☆☆☆"
        
        quality_label = QLabel(f"<h2>Match Rating: {match_quality:.1f}/100</h2>")
        quality_label.setStyleSheet("color: #FFD700;")
        quality_label.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(quality_label)
        
        star_label = QLabel(f"<h1>{stars}</h1>")
        star_label.setStyleSheet("color: #FFD700; font-size: 24pt;")
        star_label.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(star_label)
        
        # Calculate win probability based on overall stats
        w1 = self.w1
        w2 = self.w2
        
        w1_name = get_wrestler_attr(w1, "name", "Wrestler 1")
        w2_name = get_wrestler_attr(w2, "name", "Wrestler 2")
        
        # Get main attributes for calculating win probability
        w1_str = calculate_strength(w1)
        w1_dex = calculate_dexterity(w1)
        w1_end = calculate_endurance(w1)
        w1_cha = calculate_charisma(w1)
        w1_rep = get_wrestler_attr(w1, "rep", 0)
        
        w2_str = calculate_strength(w2)
        w2_dex = calculate_dexterity(w2)
        w2_end = calculate_endurance(w2)
        w2_cha = calculate_charisma(w2)
        w2_rep = get_wrestler_attr(w2, "rep", 0)
        
        # Calculate overall rating factoring in reputation
        w1_overall = (w1_str + w1_dex + w1_end + w1_cha) / 4 + (w1_rep / 20)
        w2_overall = (w2_str + w2_dex + w2_end + w2_cha) / 4 + (w2_rep / 20)
        
        # Calculate win probability
        total_rating = w1_overall + w2_overall
        if total_rating > 0:
            w1_win_prob = (w1_overall / total_rating) * 100
        else:
            w1_win_prob = 50.0
            
        # If win probability was provided in the result, use that instead
        if "w1_win_probability" in result:
            w1_win_prob = result.get("w1_win_probability", 0.5) * 100
        
        prob_label = QLabel(f"Pre-match Win Probability: {w1_name}: {w1_win_prob:.1f}% / {w2_name}: {(100-w1_win_prob):.1f}%")
        prob_label.setStyleSheet("color: #2196F3;")
        prob_label.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(prob_label)
        
        # Add wrestler stats to stats tab
        stats_layout.addWidget(QLabel("<h2>Wrestler Ratings</h2>"))
        
        # Add wrestler names as headers
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Spacer for label column
        spacer = QLabel("")
        spacer.setMinimumWidth(100)
        header_layout.addWidget(spacer)
        
        # W1 name
        w1_header = QLabel(w1_name)
        w1_header.setAlignment(Qt.AlignCenter)
        w1_header.setStyleSheet("font-weight: bold; color: #4CAF50;")
        header_layout.addWidget(w1_header)
        
        # W2 name
        w2_header = QLabel(w2_name)
        w2_header.setAlignment(Qt.AlignCenter)
        w2_header.setStyleSheet("font-weight: bold; color: #4CAF50;")
        header_layout.addWidget(w2_header)
        
        stats_layout.addWidget(header)
        
        # Create horizontal layouts for each stat with star ratings
        def create_stat_row(label_text, w1_val, w2_val, max_val=20):
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # Label
            label = QLabel(label_text)
            label.setMinimumWidth(100)
            layout.addWidget(label)
            
            # Get star ratings using our standard function with appropriate max value
            w1_stars = get_star_rating(w1_val, max_val)
            w2_stars = get_star_rating(w2_val, max_val)
            
            # W1 value with stars
            w1_label = QLabel(f"{w1_val} {w1_stars}")
            w1_label.setAlignment(Qt.AlignCenter)
            w1_label.setStyleSheet(f"color: {self.get_rating_color(w1_val)};")
            layout.addWidget(w1_label)
            
            # W2 value with stars
            w2_label = QLabel(f"{w2_val} {w2_stars}")
            w2_label.setAlignment(Qt.AlignCenter)
            w2_label.setStyleSheet(f"color: {self.get_rating_color(w2_val)};")
            layout.addWidget(w2_label)
            
            return container
            
        # Add main wrestler stats rows
        stats_layout.addWidget(create_stat_row("Strength:", w1_str, w2_str))
        stats_layout.addWidget(create_stat_row("Dexterity:", w1_dex, w2_dex))
        stats_layout.addWidget(create_stat_row("Endurance:", w1_end, w2_end))
        
        # Get Intelligence (mental stat)
        w1_int = calculate_intelligence(w1)
        w2_int = calculate_intelligence(w2)
        stats_layout.addWidget(create_stat_row("Intelligence:", w1_int, w2_int))
        
        # Charisma
        stats_layout.addWidget(create_stat_row("Charisma:", w1_cha, w2_cha))
        
        # Reputation (use higher max value)
        stats_layout.addWidget(create_stat_row("Reputation:", w1_rep, w2_rep, 100))
        
        # Calculate overall rating
        w1_overall_display = (w1_str + w1_dex + w1_end + w1_int + w1_cha) / 5
        w2_overall_display = (w2_str + w2_dex + w2_end + w2_int + w2_cha) / 5
        
        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #555;")
        stats_layout.addWidget(separator)
        
        # Add overall rating
        stats_layout.addWidget(create_stat_row("Overall:", w1_overall_display, w2_overall_display))
        
        # Add final match stats
        stats_layout.addWidget(QLabel("<h2>Match Statistics</h2>"))
        
        # Extract additional match stats
        stamina_drain = result.get("stamina_drain", {})
        health_remaining = result.get("health_remaining", {})
        damage = result.get("damage", {})
        hits = result.get("hits", {})
        misses = result.get("misses", {})
        reversals = result.get("reversals", {})
        
        # Create a grid layout for match stats
        match_stats_widget = QWidget()
        match_stats_layout = QGridLayout(match_stats_widget)
        match_stats_layout.setHorizontalSpacing(15)
        match_stats_layout.setVerticalSpacing(8)
        
        # Add headers
        match_stats_layout.addWidget(QLabel("Stat"), 0, 0)
        match_stats_layout.addWidget(QLabel(w1_name), 0, 1)
        match_stats_layout.addWidget(QLabel(w2_name), 0, 2)
        
        # Add stats rows
        row = 1
        
        # Final stamina
        match_stats_layout.addWidget(QLabel("Final Stamina:"), row, 0)
        match_stats_layout.addWidget(QLabel(f"{100 - stamina_drain.get(w1_name, 0):.1f}"), row, 1)
        match_stats_layout.addWidget(QLabel(f"{100 - stamina_drain.get(w2_name, 0):.1f}"), row, 2)
        row += 1
        
        # Damage taken
        match_stats_layout.addWidget(QLabel("Damage Taken:"), row, 0)
        match_stats_layout.addWidget(QLabel(f"{damage.get(w1_name, 0):.1f}"), row, 1)
        match_stats_layout.addWidget(QLabel(f"{damage.get(w2_name, 0):.1f}"), row, 2)
        row += 1
        
        # Health remaining
        match_stats_layout.addWidget(QLabel("Health Remaining:"), row, 0)
        match_stats_layout.addWidget(QLabel(f"{health_remaining.get(w1_name, 0):.1f}"), row, 1)
        match_stats_layout.addWidget(QLabel(f"{health_remaining.get(w2_name, 0):.1f}"), row, 2)
        row += 1
        
        # Hits
        match_stats_layout.addWidget(QLabel("Hits:"), row, 0)
        match_stats_layout.addWidget(QLabel(f"{hits.get(w1_name, 0)}"), row, 1)
        match_stats_layout.addWidget(QLabel(f"{hits.get(w2_name, 0)}"), row, 2)
        row += 1
        
        # Misses
        match_stats_layout.addWidget(QLabel("Misses:"), row, 0)
        match_stats_layout.addWidget(QLabel(f"{misses.get(w1_name, 0)}"), row, 1)
        match_stats_layout.addWidget(QLabel(f"{misses.get(w2_name, 0)}"), row, 2)
        row += 1
        
        # Reversals
        match_stats_layout.addWidget(QLabel("Reversals:"), row, 0)
        match_stats_layout.addWidget(QLabel(f"{reversals.get(w1_name, 0)}"), row, 1)
        match_stats_layout.addWidget(QLabel(f"{reversals.get(w2_name, 0)}"), row, 2)
        row += 1
        
        # Add all match stats to layout
        stats_layout.addWidget(match_stats_widget)
        
        # Add spacer at the bottom
        stats_layout.addStretch()
        
        # Psychology tab - simplified with focus on comparison and impact
        psychology_layout.addWidget(QLabel("<h2>Psychology Effects</h2>"))
        
        # Get psychology impact from result
        psychology_impact = result.get("psychology_impact", 0)
        
        # Psychology impact on match quality
        psych_quality = QLabel(f"Psychology Boost to Match Quality: +{psychology_impact*100:.1f}%")
        psych_quality.setStyleSheet("font-size: 14pt; color: #64B5F6; margin: 10px 0;")
        psychology_layout.addWidget(psych_quality)
        
        # Add wrestler psychology comparison
        psych_comparison = QWidget()
        psych_comp_layout = QVBoxLayout(psych_comparison)
        
        comp_title = QLabel("<h3>Wrestler Psychology Comparison</h3>")
        psych_comp_layout.addWidget(comp_title)
        
        # Add psychology attributes breakdown
        def create_psych_attr_row(attr_name, w1_val, w2_val):
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # Label
            label = QLabel(attr_name)
            label.setMinimumWidth(120)
            layout.addWidget(label)
            
            # W1 and W2 values
            w1_label = QLabel(f"{w1_val:.1f}")
            w1_label.setAlignment(Qt.AlignCenter)
            w1_label.setStyleSheet(f"color: {self.get_rating_color(w1_val)};")
            
            w2_label = QLabel(f"{w2_val:.1f}")
            w2_label.setAlignment(Qt.AlignCenter)
            w2_label.setStyleSheet(f"color: {self.get_rating_color(w2_val)};")
            
            layout.addWidget(w1_label)
            layout.addWidget(w2_label)
            
            return container
        
        # Add psych attribute headers
        psych_header = QWidget()
        psych_header_layout = QHBoxLayout(psych_header)
        psych_header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Spacer for label column
        psych_spacer = QLabel("")
        psych_spacer.setMinimumWidth(120)
        psych_header_layout.addWidget(psych_spacer)
        
        # W1 and W2 names
        psych_w1_header = QLabel(w1_name)
        psych_w1_header.setAlignment(Qt.AlignCenter)
        psych_w1_header.setStyleSheet("font-weight: bold;")
        psych_header_layout.addWidget(psych_w1_header)
        
        psych_w2_header = QLabel(w2_name)
        psych_w2_header.setAlignment(Qt.AlignCenter)
        psych_w2_header.setStyleSheet("font-weight: bold;")
        psych_header_layout.addWidget(psych_w2_header)
        
        psych_comp_layout.addWidget(psych_header)
        
        # Helper function to safely get wrestler attributes
        def get_psych_attr(wrestler, attr, default=10):
            """Safely get psychology attribute from wrestler"""
            try:
                if hasattr(wrestler, 'get_attribute'):
                    return wrestler.get_attribute(attr)
                elif hasattr(wrestler, 'attributes') and attr in wrestler.attributes:
                    return wrestler.attributes[attr]
                elif isinstance(wrestler, dict):
                    if 'attributes' in wrestler and attr in wrestler['attributes']:
                        return wrestler['attributes'][attr]
                    elif attr in wrestler:
                        return wrestler[attr]
                return default
            except Exception as e:
                print(f"DEBUG: Error getting {attr} from wrestler: {e}")
                return default
        
        # Get psychology attributes using the safe method
        w1_focus = get_psych_attr(w1, "focus")
        w1_resilience = get_psych_attr(w1, "resilience")
        w1_adaptability = get_psych_attr(w1, "adaptability")
        w1_risk_assessment = get_psych_attr(w1, "risk_assessment")
        w1_determination = get_psych_attr(w1, "determination")
        
        w2_focus = get_psych_attr(w2, "focus")
        w2_resilience = get_psych_attr(w2, "resilience")
        w2_adaptability = get_psych_attr(w2, "adaptability")
        w2_risk_assessment = get_psych_attr(w2, "risk_assessment")
        w2_determination = get_psych_attr(w2, "determination")
        
        # Add psychology attribute rows
        psych_comp_layout.addWidget(create_psych_attr_row("Focus:", w1_focus, w2_focus))
        psych_comp_layout.addWidget(create_psych_attr_row("Resilience:", w1_resilience, w2_resilience))
        psych_comp_layout.addWidget(create_psych_attr_row("Adaptability:", w1_adaptability, w2_adaptability))
        psych_comp_layout.addWidget(create_psych_attr_row("Risk Assessment:", w1_risk_assessment, w2_risk_assessment))
        psych_comp_layout.addWidget(create_psych_attr_row("Determination:", w1_determination, w2_determination))
        
        psychology_layout.addWidget(psych_comparison)
        
        # Add key psychology moments from the match
        psych_moments = QLabel("<h3>Key Psychology Moments</h3>")
        psychology_layout.addWidget(psych_moments)
        
        # Extract psychology highlights from result
        psych_highlights = result.get("psychology_highlights", [])
        
        if not psych_highlights:
            # Generate some generic psychology moments based on attributes comparison
            psych_highlights = []
            
            # Focus comparison
            if abs(w1_focus - w2_focus) >= 3:
                better_focus = w1_name if w1_focus > w2_focus else w2_name
                worse_focus = w2_name if w1_focus > w2_focus else w1_name
                psych_highlights.append(f"{better_focus}'s superior focus allowed for better match pacing compared to {worse_focus}")
            
            # Resilience comparison
            if abs(w1_resilience - w2_resilience) >= 3:
                more_resilient = w1_name if w1_resilience > w2_resilience else w2_name
                less_resilient = w2_name if w1_resilience > w2_resilience else w1_name
                psych_highlights.append(f"{more_resilient} showed greater resilience, recovering quickly from major moves that would have slowed {less_resilient}")
            
            # Adaptability comparison
            if abs(w1_adaptability - w2_adaptability) >= 3:
                more_adaptable = w1_name if w1_adaptability > w2_adaptability else w2_name
                less_adaptable = w2_name if w1_adaptability > w2_adaptability else w1_name
                psych_highlights.append(f"{more_adaptable} adapted better to the match flow, while {less_adaptable} struggled to change strategy when needed")
        
        # Add psychology highlights
        for highlight in psych_highlights:
            highlight_label = QLabel(f"• {highlight}")
            highlight_label.setWordWrap(True)
            highlight_label.setStyleSheet("margin: 4px 0; color: #e0e0e0;")
            psychology_layout.addWidget(highlight_label)
        
        # Add spacer at the bottom
        psychology_layout.addStretch()
        
        # Moves tab - show detailed move history with color coding
        moves_layout.addWidget(QLabel("<h2>Move History</h2>"))
        
        # Create a table for moves
        moves_table = QTableWidget()
        moves_table.setColumnCount(6)
        moves_table.setHorizontalHeaderLabels(["Turn", "Wrestler", "Move", "Type", "Damage", "Result"])
        
        # Get move history
        move_history = result.get("move_history", [])
        moves_table.setRowCount(len(move_history))
        
        # Debug move history
        print(f"DEBUG: Move history has {len(move_history)} entries")
        if move_history and len(move_history) > 0:
            print(f"DEBUG: First move sample: {move_history[0]}")
        
        # Define wrestler background colors
        w1_bg_color = QColor(44, 62, 80, 100)  # Dark blue with transparency
        w2_bg_color = QColor(127, 29, 29, 100)  # Dark red with transparency
        
        # Define move type styles
        signature_bg = QColor(148, 0, 211, 130)  # Purple for signature moves
        finisher_bg = QColor(255, 215, 0, 150)  # Gold for finishers
        
        # Populate table
        for i, move in enumerate(move_history):
            # Turn number
            turn_item = QTableWidgetItem(str(i + 1))
            moves_table.setItem(i, 0, turn_item)
            
            # Wrestler name
            wrestler_name = move.get("wrestler", "Unknown")
            wrestler_item = QTableWidgetItem(wrestler_name)
            moves_table.setItem(i, 1, wrestler_item)
            
            # Move name
            move_name = move.get("move", "Unknown Move")
            move_item = QTableWidgetItem(move_name)
            moves_table.setItem(i, 2, move_item)
            
            # Move type
            move_type = move.get("type", "Basic")
            type_item = QTableWidgetItem(move_type)
            moves_table.setItem(i, 3, type_item)
            
            # Check more thoroughly for signature/finisher moves
            is_signature = False
            is_finisher = False
            
            # Check move type
            if isinstance(move_type, str):
                is_signature = "signature" in move_type.lower()
                is_finisher = "finisher" in move_type.lower()
                
            # Check additional flags
            if not is_signature and move.get("is_signature", False):
                is_signature = True
                
            if not is_finisher and move.get("is_finisher", False):
                is_finisher = True
                
            # Check move name - many signature/finisher moves have special names
            if not is_signature and not is_finisher and isinstance(move_name, str):
                # Check against known signature/finisher move names
                w1_sig_move = self.get_wrestler_attr(self.w1, "signature_move", "")
                w1_fin_move = self.get_wrestler_attr(self.w1, "finisher", "")
                w2_sig_move = self.get_wrestler_attr(self.w2, "signature_move", "")
                w2_fin_move = self.get_wrestler_attr(self.w2, "finisher", "")
                
                # Check against known signature/finisher move names
                if move_name == w1_sig_move or move_name == w2_sig_move:
                    is_signature = True
                    type_item.setText("SIGNATURE")
                
                if move_name == w1_fin_move or move_name == w2_fin_move:
                    is_finisher = True
                    type_item.setText("FINISHER")
                
                # Check for common signature/finisher move keywords
                signature_keywords = ["signature", "patented", "special", "trademark"]
                finisher_keywords = ["finisher", "finishing", "finsh", "final"]
                
                # Check for any signature keywords in the move name or type
                for keyword in signature_keywords:
                    if keyword.lower() in move_name.lower() or (isinstance(move_type, str) and keyword.lower() in move_type.lower()):
                        is_signature = True
                        type_item.setText("SIGNATURE")
                        break
                
                # Check for any finisher keywords in the move name or type
                if not is_finisher:  # Only check if not already identified as a finisher
                    for keyword in finisher_keywords:
                        if keyword.lower() in move_name.lower() or (isinstance(move_type, str) and keyword.lower() in move_type.lower()):
                            is_finisher = True
                            type_item.setText("FINISHER")
                            break
                
                # Check for specific iconic finisher move names
                iconic_finishers = [
                    "piledriver", "tombstone", "stunner", "rock bottom", "rko", "ddt", "sharpshooter", 
                    "ankle lock", "f5", "sweet chin music", "chokeslam", "walls of jericho",
                    "figure four", "spear", "superkick", "gts", "last ride", "people's elbow"
                ]
                
                if not is_finisher and not is_signature:
                    move_name_lower = move_name.lower()
                    for iconic in iconic_finishers:
                        if iconic in move_name_lower and move.get("damage", 0) > 15:  # Higher damage suggests it's a finisher
                            is_finisher = True
                            type_item.setText("FINISHER")
                            break
            
            print(f"DEBUG: Move {i}: {move_name}, type={move_type}, sig={is_signature}, fin={is_finisher}")
            
            # Damage
            damage_item = QTableWidgetItem(f"{move.get('damage', 0)}")
            moves_table.setItem(i, 4, damage_item)
            
            # Result (hit, miss, reversal)
            result_item = QTableWidgetItem(move.get("result", "Unknown"))
            
            # Color based on result
            if move.get("result", "") == "hit":
                result_item.setBackground(QColor(50, 150, 50))  # Green for hit
            elif move.get("result", "") == "miss":
                result_item.setBackground(QColor(150, 50, 50))  # Red for miss
            elif move.get("result", "") == "reversal":
                result_item.setBackground(QColor(50, 50, 150))  # Blue for reversal
                
            moves_table.setItem(i, 5, result_item)
            
            # Set base row color based on wrestler
            row_color = w1_bg_color if wrestler_name == self.get_wrestler_attr(self.w1, 'name', '') else w2_bg_color
            
            # Apply special coloring for signature and finisher moves
            if is_finisher:
                for col in range(6):
                    item = moves_table.item(i, col)
                    if item:
                        item.setBackground(finisher_bg)
                type_item.setText("FINISHER")
                type_item.setForeground(QColor(255, 255, 0))  # Yellow text
            elif is_signature:
                for col in range(6):
                    item = moves_table.item(i, col)
                    if item:
                        item.setBackground(signature_bg)
                type_item.setText("SIGNATURE")
                type_item.setForeground(QColor(200, 200, 255))  # Light blue text
            else:
                # Apply row color if not already colored as signature or finisher
                for col in range(6):
                    item = moves_table.item(i, col)
                    if item:
                        # Set the background but keep any existing background on the result column
                        if col != 5 or move.get("result", "") not in ["hit", "miss", "reversal"]:
                            item.setBackground(row_color)
        
        # Auto resize columns to content
        moves_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # Add table to layout
        moves_layout.addWidget(moves_table)
        
        # Add tabs to tab widget
        tabs.addTab(result_tab, "Result")
        tabs.addTab(stats_tab, "Stats")
        tabs.addTab(psychology_tab, "Psychology")
        tabs.addTab(moves_tab, "Moves")
        
        # Set up dialog layout
        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.addWidget(tabs)
        
        # Add Continue button
        continue_button = QPushButton("Continue")
        continue_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14pt;
                    font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        continue_button.clicked.connect(dialog.accept)
        dialog_layout.addWidget(continue_button)
        
        # Store dialog for later reference
        self.summary_dialog = dialog
        
        # Show dialog
        dialog.exec_()
        
        # After dialog is closed, call the continue handler
        self.handle_continue()

    def get_rating_color(self, rating):
        """Get color based on rating value"""
        _, color = get_grade_and_colour(rating)
        return color

    def handle_continue(self):
        if self.on_next_match and self.match_result:
            # Ensure match quality is included in the result
            if 'quality' in self.match_result and 'match_rating' not in self.match_result:
                self.match_result["match_rating"] = self.match_result["quality"]
            elif 'match_rating' not in self.match_result and hasattr(self, 'stat_labels'):
                quality_text = self.stat_labels.get("Match Quality", "").text()
                if quality_text:
                    try:
                        quality = int(quality_text.split(": ")[1])
                        self.match_result["match_rating"] = quality
                    except (IndexError, ValueError):
                        pass
            
            self.on_next_match(self.match_result)

    def format_wrestler_stats(self, wrestler):
        """Format wrestler stats with key stats displayed in a horizontal row with stars underneath"""
        # Get stats from either object or dict using our centralized function
        strength = calculate_strength(wrestler)
        dexterity = calculate_dexterity(wrestler)
        endurance = calculate_endurance(wrestler)
        intelligence = calculate_intelligence(wrestler)
        charisma = calculate_charisma(wrestler)
        
        # Get star ratings for each stat
        strength_stars = get_star_rating(strength)
        dexterity_stars = get_star_rating(dexterity)
        endurance_stars = get_star_rating(endurance)
        intelligence_stars = get_star_rating(intelligence)
        charisma_stars = get_star_rating(charisma)
        
        # Trace the stats we've retrieved
        wrestler_name = get_wrestler_attr(wrestler, "name", "Unknown")
        print(f"DEBUG: format_wrestler_stats for {wrestler_name}: STR={strength}, DEX={dexterity}, END={endurance}, INT={intelligence}, CHR={charisma}")
        
        # Format them in a horizontal layout with stars underneath
        return f"""
            <table style='font-family: Fira Code; font-size: 0.9em; border-spacing: 4px; width: 100%;'>
                <tr>
                    <td align='center'><span style='color:#c0392b; font-weight: bold;'>STR</span></td>
                    <td align='center'><span style='color:#3498db; font-weight: bold;'>DEX</span></td>
                    <td align='center'><span style='color:#2ecc71; font-weight: bold;'>END</span></td>
                    <td align='center'><span style='color:#9b59b6; font-weight: bold;'>INT</span></td>
                    <td align='center'><span style='color:#e67e22; font-weight: bold;'>CHR</span></td>
                </tr>
                <tr>
                    <td align='center'><span style='color:#c0392b; font-size: 1.1em;'>{strength_stars}</span></td>
                    <td align='center'><span style='color:#3498db; font-size: 1.1em;'>{dexterity_stars}</span></td>
                    <td align='center'><span style='color:#2ecc71; font-size: 1.1em;'>{endurance_stars}</span></td>
                    <td align='center'><span style='color:#9b59b6; font-size: 1.1em;'>{intelligence_stars}</span></td>
                    <td align='center'><span style='color:#e67e22; font-size: 1.1em;'>{charisma_stars}</span></td>
                </tr>
            </table>
        """

    def build_info_bar(self):
        info_bar = QHBoxLayout()
        info_bar.setAlignment(Qt.AlignCenter)

        # Get initial values
        w1_name = self.get_wrestler_attr(self.w1, 'name', 'Wrestler 1')
        w2_name = self.get_wrestler_attr(self.w2, 'name', 'Wrestler 2')
        w1_stamina = self.get_wrestler_attr(self.w1, 'stamina', 100)
        w2_stamina = self.get_wrestler_attr(self.w2, 'stamina', 100)

        # Left wrestler stats - larger and more visible
        self.left_stamina = QLabel(f"Stamina: {w1_stamina}")
        self.left_stamina.setFixedWidth(180)
        self.left_stamina.setStyleSheet("font-size: 18pt; font-weight: bold; color: #9be7ff; font-family: Fira Code;")

        self.left_damage = QLabel("Damage: 0.0")
        self.left_damage.setFixedWidth(180)
        self.left_damage.setStyleSheet("font-size: 18pt; font-weight: bold; color: #ffaaaa; font-family: Fira Code;")

        # Center match quality stars
        self.match_quality_stars = QLabel("★☆☆☆☆")
        self.match_quality_stars.setFixedWidth(120)
        self.match_quality_stars.setAlignment(Qt.AlignCenter)
        self.match_quality_stars.setStyleSheet("""
            font-size: 20pt;
            font-weight: bold;
            font-family: Fira Code;
            color: gold;
        """)

        # Right wrestler stats - larger and more visible
        self.right_stamina = QLabel(f"Stamina: {w2_stamina}")
        self.right_stamina.setFixedWidth(180)
        self.right_stamina.setStyleSheet("font-size: 18pt; font-weight: bold; color: #9be7ff; font-family: Fira Code;")

        self.right_damage = QLabel("Damage: 0.0")
        self.right_damage.setFixedWidth(180)
        self.right_damage.setStyleSheet("font-size: 18pt; font-weight: bold; color: #ffaaaa; font-family: Fira Code;")

        # Add widgets in the proper order
        info_bar.addWidget(self.left_stamina)
        info_bar.addWidget(self.left_damage)
        info_bar.addSpacing(40)
        info_bar.addWidget(self.match_quality_stars)
        info_bar.addSpacing(40)
        info_bar.addWidget(self.right_stamina)
        info_bar.addWidget(self.right_damage)

        self.layout.addLayout(info_bar)

    def toggle_pause(self):
        self.paused = not self.paused
        if hasattr(self, 'worker'):
            self.worker.paused = self.paused
            
        if self.paused:
            self.pause_button.setText("Resume")
            self.display_timer.stop()
        else:
            self.pause_button.setText("Pause")
            if self.commentary_queue:
                self.process_next_beat()

    def handle_match_end(self, result):
        """Process match end, including storylines and statistics."""
        # Show end animation
        QTimer.singleShot(500, self.show_end)
        
        # Process diplomacy effects if available
        if self.diplomacy_system:
            handle_match_relationship_effects(
                self.w1,
                self.w2,
                result,
                self.diplomacy_system
            )
        
        # We don't need to manually create storylines since the integrator does it
        # Just use what's already in the result
        storylines = result.get("storylines", [])
        
        # Show winner
        def show_winner():
            winner_name = result["winner"]
            w1_name = self.get_wrestler_attr(self.w1, 'name', 'Wrestler 1')
            
            if winner_name == w1_name:
                winner_color = "#2c3e50"
            else:
                winner_color = "#7f1d1d"
            
            self.log_html(f"<br><p style='text-align:center;font-size:24pt;color:{winner_color};'>WINNER: {winner_name}</p>")
            
            # Display match quality
            quality = result.get("quality", 0)
            quality_text = f"<p style='text-align:center;font-size:18pt;'>Match Rating: {quality}/100</p>"
            self.log_html(quality_text)
            
            # Display any key statistics
            if "statistics" in result:
                winner_stats = result["statistics"].get("wrestler1") if winner_name == w1_name else result["statistics"].get("wrestler2")
                if winner_stats:
                    wins = winner_stats.get("wins", 0)
                    losses = winner_stats.get("losses", 0)
                    avg_quality = winner_stats.get("avg_quality", 0)
                    stats_text = f"<p style='text-align:center;font-size:14pt;'>{winner_name}: {wins}W-{losses}L, Avg Rating: {avg_quality:.1f}</p>"
                    self.log_html(stats_text)
            
            # Display storyline implications
            if storylines:
                self.log_html("<p style='text-align:center;font-size:16pt;color:gold;'>Storyline Implications:</p>")
                for storyline_id in storylines[:2]:  # Show top 2 storylines
                    # We need to get the storyline details
                    # This is just a placeholder - you'd need to retrieve the actual storyline
                    self.log_html(f"<p style='text-align:center;font-size:14pt;'>New storyline potential (ID: {storyline_id})</p>")
        
        QTimer.singleShot(1500, show_winner)

    def finish_match_quick(self):
        """Quickly finish the match by enabling fast mode and clearing the queue."""
        if hasattr(self, 'worker'):
            # Enable fast mode to skip delays
            self.worker.fast_mode = True
            
            # Clear existing commentary queue to prevent backlog
            self.commentary_queue = []
            
            # Stop any active timers
            self.display_timer.stop()
            
            # Disable UI updates until the end
            if hasattr(self, 'worker'):
                self.worker.beat_in_progress = False
            
            # Hide the finish button after clicking
            self.finish_button.setVisible(False)
            
            # Add a "finishing match" message
            self.commentary_box.clear()
            self.commentary_box.append("<div style='text-align:center; font-size:16pt; color:#ffc107;'>⏩ Finishing match quickly...</div>")
            
            # Process events to update UI
            QApplication.processEvents()

    def show_end(self):
        """Show the match end animation and final beat."""
        # Wait until all commentary beats are processed
        if len(self.commentary_queue) > 0 or self.display_timer.isActive():
            QTimer.singleShot(500, self.show_end)
            return
        
        # Add final match ended beat
        self.queue_beat("🏁 Match ended!", None)
        self.continue_button.setVisible(True)

    def log_html(self, html_text):
        """Log HTML formatted text to the commentary box."""
        # Check if the commentary_box still exists
        if not hasattr(self, 'commentary_box') or self.commentary_box is None:
            return
            
        # Insert the HTML at the end of the document
        try:
            cursor = self.commentary_box.textCursor()
            cursor.movePosition(cursor.End)
            cursor.insertHtml(html_text)
            cursor.insertBlock()
            
            # Ensure the most recent text is visible
            self.commentary_box.ensureCursorVisible()
            
            # Process events to update UI
            QApplication.processEvents()
        except RuntimeError:
            # Object may have been deleted during processing
            pass

    def update_stamina_label(self, label, value):
        """Update stamina label with color based on value"""
        # Make sure value is a float
        try:
            value = float(value)
        except (ValueError, TypeError):
            print(f"DEBUG: Error converting stamina value to float: {value}")
            value = 100.0
            
        if value > 70:
            color = "#9be7ff"  # Blue - good stamina
        elif value > 40:
            color = "#ffc107"  # Yellow - medium stamina
        else:
            color = "#ff6f61"  # Red - low stamina
            
        # Add visual indicator based on remaining stamina
        bars = int(value / 10)
        indicator = "⚡" * bars
        
        print(f"DEBUG: Setting stamina label text to: {value:.1f}")
        label.setText(f"Stamina: {value:.1f}")
        label.setToolTip(f"Stamina: {value:.1f}/100 {indicator}")
        label.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {color}; font-family: Fira Code;")
        
    def update_damage_label(self, label, value):
        """Update damage label with color based on value"""
        # Make sure value is a float
        try:
            value = float(value)
        except (ValueError, TypeError):
            print(f"DEBUG: Error converting damage value to float: {value}")
            value = 0.0
            
        if value < 30:
            color = "#98FB98"  # Light green - low damage
        elif value < 60:
            color = "#ffaaaa"  # Light red - medium damage
        else:
            color = "#ff6347"  # Tomato red - high damage
            
        # Add visual indicator based on damage taken
        bars = 10 - int(value / 10)
        indicator = "❤" * bars
        
        print(f"DEBUG: Setting damage label text to: {value:.1f}")
        label.setText(f"Damage: {value:.1f}")
        label.setToolTip(f"{indicator}")
        label.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {color}; font-family: Fira Code;")
