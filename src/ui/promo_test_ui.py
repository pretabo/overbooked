from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QHBoxLayout, QProgressBar,
    QSlider, QFrame, QGroupBox, QTabWidget, QSplitter,
    QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QDateTime, QEasingCurve, pyqtProperty, QPoint
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QLinearGradient, QPen
from src.core.match_engine import get_all_wrestlers, load_wrestler_by_id
from src.ui.theme import apply_styles
import random
from src.promo.promo_engine import PromoEngine
from src.promo.promo_engine_helpers import (
    roll_promo_score,
    determine_line_quality
)
from src.promo.commentary_engine import generate_commentary
# Import our fixed commentary engine
from src.promo.custom_commentary_engine import fixed_generate_commentary
import math
import statistics
from src.storyline.storyline_manager import StorylineManager
from src.promo.versus_promo_engine import VersusPromoEngine

class TriangleMomentumMeter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0.0
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Shake animation
        self.shake_offset = 0
        self.shake_timer = QTimer(self)
        self.shake_timer.timeout.connect(self.update_shake)
        self.shake_amplitude = 0
        
    @pyqtProperty(float)
    def value(self):
        return self._value
        
    @value.setter
    def value(self, val):
        self._value = float(val)
        self.update()
        
    def setValue(self, value):
        self.animation.stop()
        self.animation.setStartValue(float(self.value))
        self.animation.setEndValue(float(value))
        self.animation.start()
        
        # Update shake based on value
        self.shake_amplitude = min(5, value / 20)
        if value > 50 and not self.shake_timer.isActive():
            self.shake_timer.start(50)
        elif value <= 50:
            self.shake_timer.stop()
            self.shake_offset = 0
            
    def update_shake(self):
        self.shake_offset = math.sin(QDateTime.currentMSecsSinceEpoch() / 100) * self.shake_amplitude
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the static rectangle background
        width = self.width()
        height = self.height()
        
        # Draw background
        painter.fillRect(0, 0, width, height, QColor(50, 50, 50))
        
        # Calculate fill width based on value (0-100)
        fill_width = int((self.value / 100.0) * width)  # Convert to int
        
        if fill_width > 0:
            # Create a separate painter for the filled portion with shake
            fill_painter = QPainter(self)
            fill_painter.setRenderHint(QPainter.Antialiasing)
            
            # Only apply shake to the filled portion
            if self.shake_offset != 0:
                fill_painter.translate(self.shake_offset, 0)
            
            # Create gradient from red to yellow
            gradient = QLinearGradient(0, 0, width, 0)
            gradient.setColorAt(0, QColor(255, 50, 50))
            gradient.setColorAt(1, QColor(255, 255, 50))
            
            # Draw the filled portion
            fill_painter.fillRect(0, 0, fill_width, height, gradient)

class HealthBarConfidenceMeter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 50.0
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
    @pyqtProperty(float)
    def value(self):
        return self._value
        
    @value.setter
    def value(self, val):
        self._value = float(val)
        self.update()
        
    def setValue(self, value):
        self.animation.stop()
        self.animation.setStartValue(float(self.value))
        self.animation.setEndValue(float(value))
        self.animation.start()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(50, 50, 50))
        
        # Draw health bar
        width = int(self.width() * (self.value / 100))
        if width > 0:
            if self.value > 66:
                color = QColor(100, 255, 100)  # Green
            elif self.value > 33:
                color = QColor(255, 255, 100)  # Yellow
            else:
                color = QColor(255, 100, 100)  # Red
            painter.fillRect(0, 0, width, self.height(), color)
            
        # Draw segments using QPoint to avoid float issues
        segment_width = self.width() / 10
        for i in range(1, 10):
            x = int(i * segment_width)
            start = QPoint(x, 0)
            end = QPoint(x, self.height())
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawLine(start, end)

class PromoDisplayWidget(QWidget):
    """Custom widget to display promo beats with timing controls."""
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.beats = []
        self.current_beat = 0
        self.speed = 3500  # Increased from 2000 to 3500 milliseconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_next_beat)
        self.is_playing = False
        
        # Wrestler data
        self.wrestler1 = None
        self.wrestler2 = None
        self.is_versus_mode = False
        
        # Cash-in state
        self.w1_momentum_cashed = False
        self.w2_momentum_cashed = False
        
        self.initUI()
        
        self.play_button.setEnabled(False)
        self.finish_button.setEnabled(False)
        self.fast_forward_button.setEnabled(False)

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to maximize space
        layout.setSpacing(10)  # Reduce spacing between elements
        self.setLayout(layout)
        
        # Rating display at the top with larger font
        self.rating_label = QLabel(self)
        self.rating_label.setAlignment(Qt.AlignCenter)
        self.rating_label.setStyleSheet("""
            font-family: Fira Code;
            font-size: 24pt;
            font-weight: bold;
            color: gold;
            padding: 10px;
            background-color: #2a2a2a;
            border-radius: 8px;
            margin: 0;
        """)
        self.rating_label.setText("Current Rating: -- (--★)")
        layout.addWidget(self.rating_label)
        
        # Wrestler meters (side by side)
        self.meters_container = QWidget()
        meters_layout = QHBoxLayout(self.meters_container)
        meters_layout.setContentsMargins(0, 0, 0, 0)
        
        # Wrestler 1 meters
        self.w1_meters = QGroupBox("Wrestler 1")
        self.w1_meters.setStyleSheet("""
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
        w1_layout = QVBoxLayout(self.w1_meters)
        
        # Momentum meter for wrestler 1
        w1_momentum_container = QWidget()
        w1_momentum_layout = QHBoxLayout(w1_momentum_container)
        w1_momentum_layout.setContentsMargins(0, 0, 0, 0)
        w1_momentum_label = QLabel("MOMENTUM")
        w1_momentum_label.setFixedWidth(100)
        w1_momentum_label.setStyleSheet("font-family: Fira Code; font-weight: bold; color: #ff6b6b;")
        w1_momentum_layout.addWidget(w1_momentum_label)
        self.w1_momentum_meter = TriangleMomentumMeter()
        self.w1_momentum_meter.setFixedHeight(25)
        w1_momentum_layout.addWidget(self.w1_momentum_meter, stretch=1)
        w1_layout.addWidget(w1_momentum_container)
        
        # Confidence meter for wrestler 1
        w1_confidence_container = QWidget()
        w1_confidence_layout = QHBoxLayout(w1_confidence_container)
        w1_confidence_layout.setContentsMargins(0, 0, 0, 0)
        w1_confidence_label = QLabel("CONFIDENCE")
        w1_confidence_label.setFixedWidth(100)
        w1_confidence_label.setStyleSheet("font-family: Fira Code; font-weight: bold; color: #4ecdc4;")
        w1_confidence_layout.addWidget(w1_confidence_label)
        self.w1_confidence_meter = HealthBarConfidenceMeter()
        self.w1_confidence_meter.setFixedHeight(20)
        w1_confidence_layout.addWidget(self.w1_confidence_meter, stretch=1)
        w1_layout.addWidget(w1_confidence_container)
        
        # Cash-in button for wrestler 1
        self.w1_cashin_button = QPushButton("🌟 Cash In Momentum")
        self.w1_cashin_button.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: #777;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:disabled {
                color: #555;
            }
        """)
        self.w1_cashin_button.setEnabled(False)
        self.w1_cashin_button.clicked.connect(lambda: self.cash_in_momentum(1))
        w1_layout.addWidget(self.w1_cashin_button)
        
        # Wrestler 2 meters
        self.w2_meters = QGroupBox("Wrestler 2")
        self.w2_meters.setStyleSheet("""
            QGroupBox {
                font-family: Fira Code;
                font-weight: bold;
                color: #FF9966;
                border: 1px solid #444;
                border-radius: 8px;
                margin-top: 1em;
                padding: 10px;
            }
        """)
        w2_layout = QVBoxLayout(self.w2_meters)
        
        # Momentum meter for wrestler 2
        w2_momentum_container = QWidget()
        w2_momentum_layout = QHBoxLayout(w2_momentum_container)
        w2_momentum_layout.setContentsMargins(0, 0, 0, 0)
        w2_momentum_label = QLabel("MOMENTUM")
        w2_momentum_label.setFixedWidth(100)
        w2_momentum_label.setStyleSheet("font-family: Fira Code; font-weight: bold; color: #ff6b6b;")
        w2_momentum_layout.addWidget(w2_momentum_label)
        self.w2_momentum_meter = TriangleMomentumMeter()
        self.w2_momentum_meter.setFixedHeight(25)
        w2_momentum_layout.addWidget(self.w2_momentum_meter, stretch=1)
        w2_layout.addWidget(w2_momentum_container)
        
        # Confidence meter for wrestler 2
        w2_confidence_container = QWidget()
        w2_confidence_layout = QHBoxLayout(w2_confidence_container)
        w2_confidence_layout.setContentsMargins(0, 0, 0, 0)
        w2_confidence_label = QLabel("CONFIDENCE")
        w2_confidence_label.setFixedWidth(100)
        w2_confidence_label.setStyleSheet("font-family: Fira Code; font-weight: bold; color: #4ecdc4;")
        w2_confidence_layout.addWidget(w2_confidence_label)
        self.w2_confidence_meter = HealthBarConfidenceMeter()
        self.w2_confidence_meter.setFixedHeight(20)
        w2_confidence_layout.addWidget(self.w2_confidence_meter, stretch=1)
        w2_layout.addWidget(w2_confidence_container)
        
        # Cash-in button for wrestler 2
        self.w2_cashin_button = QPushButton("🌟 Cash In Momentum")
        self.w2_cashin_button.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: #777;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:disabled {
                color: #555;
            }
        """)
        self.w2_cashin_button.setEnabled(False)
        self.w2_cashin_button.clicked.connect(lambda: self.cash_in_momentum(2))
        w2_layout.addWidget(self.w2_cashin_button)
        
        # Add wrestler meters to container
        meters_layout.addWidget(self.w1_meters)
        meters_layout.addWidget(self.w2_meters)
        
        # Add meters container to main layout
        layout.addWidget(self.meters_container)
        
        # Initially hide wrestler 2 meters (for solo promos)
        self.w2_meters.setVisible(False)
        
        # Beat display with fixed height and scrolling
        self.beat_display = QTextEdit(self)
        self.beat_display.setReadOnly(True)
        self.beat_display.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.beat_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.beat_display.setFixedHeight(200)  # Reduced height from 250 to 200
        self.beat_display.setStyleSheet("""
            QTextEdit {
                font-family: Fira Code;
                font-size: 11pt;  /* Further reduced font size */
                background-color: #1a1a1a;
                color: #ddd;
                border: 2px solid #333;
                border-radius: 8px;
                padding: 10px;
                margin: 0;
            }
            QScrollBar:vertical {
                border: none;
                background: #2a2a2a;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #444;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        layout.addWidget(self.beat_display)
        
        # Speed controls container with fixed height
        speed_container = QWidget(self)
        speed_container.setFixedHeight(40)  # Reduced height from 50 to 40
        speed_layout = QHBoxLayout(speed_container)
        speed_layout.setSpacing(10)
        speed_layout.setContentsMargins(0, 0, 0, 0)
        
        speed_label = QLabel("Speed:", speed_container)
        speed_label.setStyleSheet("color: #ddd;")
        speed_layout.addWidget(speed_label)
        
        for speed in ["Slow", "Normal", "Fast"]:
            btn = QPushButton(speed, speed_container)
            btn.clicked.connect(lambda checked, s=speed: self.set_speed_preset(s))
            btn.setFixedWidth(80)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #333;
                    color: #ddd;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #444;
                }
            """)
            speed_layout.addWidget(btn)
        
        # Play and finish buttons
        self.play_button = QPushButton("Play", speed_container)
        self.play_button.clicked.connect(self.toggle_play)
        self.play_button.setFixedWidth(100)
        self.play_button.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
        """)
        speed_layout.addWidget(self.play_button)
        
        # Add Fast Forward button
        self.fast_forward_button = QPushButton("⏩ Fast Forward", speed_container)
        self.fast_forward_button.clicked.connect(self.fast_forward)
        self.fast_forward_button.setFixedWidth(120)
        self.fast_forward_button.setStyleSheet("""
            QPushButton {
                background-color: #3a2a2a;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #4a3a3a;
            }
        """)
        speed_layout.addWidget(self.fast_forward_button)
        
        self.finish_button = QPushButton("Finish Promo", speed_container)
        self.finish_button.clicked.connect(self.finish_promo)
        self.finish_button.setFixedWidth(100)
        self.finish_button.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
        """)
        speed_layout.addWidget(self.finish_button)
        
        layout.addWidget(speed_container)
        
        self.play_button.setEnabled(False)
        self.finish_button.setEnabled(False)
        self.fast_forward_button.setEnabled(False)

    def set_wrestlers(self, wrestler1, wrestler2=None):
        """Set the wrestlers for this display."""
        self.wrestler1 = wrestler1
        self.wrestler2 = wrestler2
        self.is_versus_mode = wrestler2 is not None
        
        # Update UI based on versus mode
        if self.is_versus_mode:
            self.w1_meters.setTitle(wrestler1["name"])
            self.w2_meters.setTitle(wrestler2["name"])
            self.w2_meters.setVisible(True)
        else:
            self.w1_meters.setTitle(wrestler1["name"])
            self.w2_meters.setVisible(False)

    def set_speed_preset(self, preset):
        """Set speed based on preset button."""
        speeds = {"Slow": 5000, "Normal": 3500, "Fast": 2000}  # in milliseconds (increased from previous values)
        self.speed = speeds[preset]
        if self.is_playing:
            self.timer.setInterval(self.speed)

    def toggle_play(self):
        """Toggle between play and pause."""
        if self.is_playing:
            self.timer.stop()
            self.play_button.setText("Play")
        else:
            self.timer.start(self.speed)
            self.play_button.setText("Pause")
        self.is_playing = not self.is_playing

    def set_beats(self, beats):
        """Set the beats to display and reset the display."""
        self.beats = beats
        self.current_beat = 0
        self.beat_display.clear()
        self.w1_momentum_meter.setValue(0)
        self.w1_confidence_meter.setValue(50)  # Start at neutral confidence
        self.w2_momentum_meter.setValue(0)
        self.w2_confidence_meter.setValue(50)  # Start at neutral confidence
        
        # Reset cash-in state
        self.w1_momentum_cashed = False
        self.w2_momentum_cashed = False
        self.w1_cashin_button.setEnabled(False)
        self.w2_cashin_button.setEnabled(False)
        
        self.play_button.setEnabled(True)
        self.finish_button.setEnabled(True)
        self.fast_forward_button.setEnabled(True)
        
        # Add initial separator
        self.beat_display.insertHtml('<div style="margin: 10px 0;"></div>')
        
        # Start playing automatically
        self.is_playing = True
        self.play_button.setText("Pause")
        self.timer.start(self.speed)

    def fast_forward(self):
        """Display all remaining beats instantly without delays."""
        # Stop the timer
        self.timer.stop()
        self.is_playing = False
        self.play_button.setText("Play")
        self.fast_forward_button.setEnabled(False)
        
        # Display all remaining beats at once
        while self.current_beat < len(self.beats):
            self.display_next_beat()
            
        # Signal that we're done
        self.finished.emit()

    def calculate_rolling_rating(self):
        """Calculate the current rating based on beats shown so far."""
        if not self.beats or self.current_beat == 0:
            return 0, 0
            
        # Get scores up to current beat
        scores = [b.get("score", 0) for b in self.beats[:self.current_beat]]
        
        # Calculate weighted scores
        weighted_scores = []
        for score in scores:
            if score >= 85:  # Excellent scores get 2x weight
                weighted_scores.extend([score, score])
            elif score >= 70:  # Good scores get 1.5x weight
                weighted_scores.extend([score, score * 0.5])
            else:
                weighted_scores.append(score)
        
        avg_score = sum(weighted_scores) / len(weighted_scores)
        
        # Calculate consistency bonus
        score_std = statistics.stdev(scores) if len(scores) > 1 else 0
        consistency_bonus = max(0, (20 - score_std) / 20) * 5
        
        # Calculate finish bonus based on last 3 beats
        finish_bonus = 0
        if len(scores) >= 3:
            final_beats_avg = sum(scores[-3:]) / 3
            if final_beats_avg >= 85:
                finish_bonus = 5
            elif final_beats_avg >= 70:
                finish_bonus = 3
        
        final_rating = avg_score + consistency_bonus + finish_bonus
        final_rating = max(0, min(100, final_rating))
        
        # Convert to star rating (0-5 stars)
        star_rating = final_rating / 20  # 100 rating = 5 stars
        
        return round(final_rating, 1), round(star_rating, 2)

    def get_star_display(self, stars):
        """Convert star rating to display format."""
        full_stars = int(stars)
        partial = stars - full_stars
        
        display = "★" * full_stars
        if partial >= 0.75:
            display += "★"
        elif partial >= 0.25:
            display += "½"
            
        return display

    def get_score_color(self, score):
        """Get color for score display based on value."""
        if score >= 90:
            return "#ffd700"  # Gold
        elif score >= 80:
            return "#98fb98"  # Pale green
        elif score >= 70:
            return "#87ceeb"  # Sky blue
        elif score >= 60:
            return "#dda0dd"  # Plum
        elif score >= 50:
            return "#f0e68c"  # Khaki
        else:
            return "#cd5c5c"  # Indian red

    def display_next_beat(self):
        """Display the next beat with momentum and confidence updates."""
        if self.current_beat >= len(self.beats):
            self.timer.stop()
            self.play_button.setEnabled(False)
            self.fast_forward_button.setEnabled(False)
            self.finished.emit()
            return

        beat = self.beats[self.current_beat]
        
        # Get commentary from the engine
        commentary = fixed_generate_commentary(beat)
        
        # Check if this is a special beat (intro, summary, or cash-in)
        is_intro = commentary.get("is_intro", False)
        is_summary = commentary.get("is_summary", False)
        is_cash_in = "🌟" in commentary["promo_line"]
        
        # Check if this is a versus promo beat
        is_versus = beat.get("versus_mode", False)
        is_versus_beat = beat.get("is_versus_beat", False)
        
        # Update appropriate wrestler's meters
        if not is_intro and not is_summary:
            # Get momentum and confidence values
            momentum = beat.get("momentum", 0)
            confidence = beat.get("confidence", 50)
            
            # Determine which wrestler is speaking (for versus mode)
            if is_versus_beat and "wrestler" in beat:
                if beat["wrestler"] == self.wrestler1:
                    # Update wrestler 1 meters
                    self.w1_momentum_meter.setValue(int(momentum))
                    self.w1_confidence_meter.setValue(int(confidence))
                    
                    # Enable cash-in button if momentum is high enough and not already cashed in
                    if momentum >= 70 and not self.w1_momentum_cashed:
                        self.w1_cashin_button.setEnabled(True)
                        # Add pulse animation to draw attention
                        self.w1_cashin_button.setStyleSheet("""
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
                        """)
                    else:
                        self.w1_cashin_button.setEnabled(momentum >= 70 and not self.w1_momentum_cashed)
                elif beat["wrestler"] == self.wrestler2:
                    # Update wrestler 2 meters
                    self.w2_momentum_meter.setValue(int(momentum))
                    self.w2_confidence_meter.setValue(int(confidence))
                    
                    # Enable cash-in button if momentum is high enough and not already cashed in
                    if momentum >= 70 and not self.w2_momentum_cashed:
                        self.w2_cashin_button.setEnabled(True)
                        # Add pulse animation to draw attention
                        self.w2_cashin_button.setStyleSheet("""
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
                        """)
                    else:
                        self.w2_cashin_button.setEnabled(momentum >= 70 and not self.w2_momentum_cashed)
            else:
                # Solo mode - just update wrestler 1
                self.w1_momentum_meter.setValue(int(momentum))
                self.w1_confidence_meter.setValue(int(confidence))
                
                # Enable cash-in button if momentum is high enough and not already cashed in
                if momentum >= 70 and not self.w1_momentum_cashed:
                    self.w1_cashin_button.setEnabled(True)
                    # Add pulse animation to draw attention
                    self.w1_cashin_button.setStyleSheet("""
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
                    """)
                else:
                    self.w1_cashin_button.setEnabled(momentum >= 70 and not self.w1_momentum_cashed)
                
                # Enable cash-in button if momentum is high enough and not already cashed in
                if momentum >= 70 and not self.w1_momentum_cashed:
                    self.w1_cashin_button.setEnabled(True)
                    # Add pulse animation to draw attention
                    self.w1_cashin_button.setStyleSheet("""
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
                    """)
                else:
                    self.w1_cashin_button.setEnabled(momentum >= 70 and not self.w1_momentum_cashed)
        
        # Get wrestler info for styling
        wrestler_name = beat.get("wrestler", {}).get("name", "Wrestler")
        wrestler_color = beat.get("wrestler_color", "#66CCFF") if is_versus_beat else "#66CCFF"
        
        # Get score for big display
        score = commentary.get('score', 0)
        score_color = self.get_score_color(score)
        
        # Build the complete beat HTML before inserting
        if is_intro:
            beat_html = f'''
                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 10px 0;">
                    <tr><td style="
                        background: linear-gradient(135deg, #1a1a2a 0%, #2a2a3a 100%);
                        border: 1px solid #4a4a6a;
                        border-radius: 8px;
                        box-shadow: 0 0 15px rgba(74, 74, 106, 0.2);
                        padding: 10px;
                    ">
                    <div style="
                        font-family: Fira Code;
                        font-size: 14pt;
                        font-style: italic;
                        line-height: 1.4;
                        color: #8a8aaa;
                        text-align: center;
                    ">{commentary["promo_line"]}</div>
                    </td></tr>
                </table>
            '''
        elif is_summary:
            beat_html = f'''
                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 10px 0;">
                    <tr><td style="
                        background: linear-gradient(135deg, #2a1a1a 0%, #3a2a2a 100%);
                        border: 1px solid #6a4a4a;
                        border-radius: 8px;
                        box-shadow: 0 0 15px rgba(106, 74, 74, 0.2);
                        padding: 10px;
                    ">
                    <div style="
                        font-family: Fira Code;
                        font-size: 14pt;
                        font-style: italic;
                        line-height: 1.4;
                        color: #aa8a8a;
                        text-align: center;
                    ">{commentary["promo_line"]}</div>
                    </td></tr>
                </table>
            '''
        else:
            # Use consistent styling for both solo and versus beats
            beat_html = f'''
                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 10px 0;">
                    <tr>
                    <!-- Score column -->
                    <td width="80" style="
                        background-color: #333;
                        border-radius: 8px 0 0 8px;
                        padding: 10px;
                        text-align: center;
                        vertical-align: middle;
                    ">
                    <div style="
                        font-family: Fira Code;
                        font-weight: bold;
                        font-size: 24pt;
                        color: {score_color};
                    ">{score:.1f}</div>
                    </td>
                    
                    <!-- Beat content column -->
                    <td style="
                        background-color: #252525;
                        border-radius: 0 8px 8px 0;
                        padding: 10px;
                    ">
                    <div style="
                        font-family: Fira Code;
                        font-weight: bold;
                        font-size: 14pt;
                        color: {wrestler_color};
                        margin-bottom: 5px;
                    ">{wrestler_name}:</div>
                    <div style="
                        font-family: Fira Code;
                        font-size: 14pt;
                        line-height: 1.4;
                        color: #fff;
                        margin: 5px 0;
                    ">'{commentary["promo_line"]}'.</div>
            '''
            
            # Add commentary lines if present
            if commentary['commentary_line']:
                beat_html += f'''
                    <div style="
                        margin: 4px 0;
                        font-family: Fira Code;
                        font-size: 11pt;
                        font-style: italic;
                        color: #888;
                    ">
                        {commentary['commentary_line']}
                    </div>
                '''
            
            # Add momentum and confidence info consistently for all beats
            beat_html += f'''
                <div style="
                    margin: 6px 0 0 0;
                    font-family: Fira Code;
                    font-size: 11pt;
                ">
                    <span style="color: #ff6b6b;">⚡ {beat["momentum"]:.1f}</span>
                    <span style="color: #888;"> | </span>
                    <span style="color: #4ecdc4;">💪 {beat["confidence"]:.1f}</span>
                </div>
            '''
            
            # Close the beat content column and row
            beat_html += '</td></tr></table>'
        
        # Insert the complete beat HTML
        cursor = self.beat_display.textCursor()
        cursor.movePosition(cursor.End)
        self.beat_display.setTextCursor(cursor)
        self.beat_display.insertHtml(beat_html)
        
        # Update rating to show only stars
        _, stars = self.calculate_rolling_rating()
        self.rating_label.setText(f"{self.get_star_display(stars)}")
        
        # Auto-scroll to bottom of text display
        scrollbar = self.beat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Move to next beat
        self.current_beat += 1

    def style_progress_bar(self, bar, value):
        """Style progress bar based on value."""
        style = "QProgressBar { border: 2px solid grey; border-radius: 5px; text-align: center; } "
        style += "QProgressBar::chunk { "
        
        if value >= 75:
            style += "background-color: #4CAF50; }"  # Green
        elif value >= 50:
            style += "background-color: #FFC107; }"  # Yellow
        elif value >= 25:
            style += "background-color: #FF9800; }"  # Orange
        else:
            style += "background-color: #f44336; }"  # Red
        
        bar.setStyleSheet(style)

    def finish_promo(self):
        """Display all remaining beats instantly."""
        self.timer.stop()
        self.play_button.setEnabled(False)
        self.finish_button.setEnabled(False)
        
        # Display all remaining beats
        while self.current_beat < len(self.beats):
            self.display_next_beat()
        
        self.finished.emit()

    def cash_in_momentum(self, wrestler_index):
        """Handle a wrestler cashing in their momentum for a special line."""
        # Determine which wrestler is cashing in
        wrestler = None
        if wrestler_index == 1:
            wrestler = self.wrestler1
            meter = self.w1_momentum_meter
            self.w1_momentum_cashed = True
            self.w1_cashin_button.setEnabled(False)
            # Reset button style
            self.w1_cashin_button.setStyleSheet("""
                QPushButton {
                    background-color: #333;
                    color: #777;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 5px;
                    font-weight: bold;
                }
                QPushButton:disabled {
                    color: #555;
                }
            """)
        else:
            wrestler = self.wrestler2
            meter = self.w2_momentum_meter
            self.w2_momentum_cashed = True
            self.w2_cashin_button.setEnabled(False)
            # Reset button style
            self.w2_cashin_button.setStyleSheet("""
                QPushButton {
                    background-color: #333;
                    color: #777;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 5px;
                    font-weight: bold;
                }
                QPushButton:disabled {
                    color: #555;
                }
            """)
            
        if not wrestler:
            return
            
        # Get current momentum value
        momentum = meter.value
        
        # Create a special cash-in line based on momentum level
        cash_in_lines = [
            f"{wrestler['name']} unleashes their signature catchphrase, energizing the crowd! 🌟",
            f"{wrestler['name']} plays to the audience, drawing a massive reaction! 🌟",
            f"{wrestler['name']} delivers a devastating verbal knockout! 🌟",
            f"{wrestler['name']} raises intensity to a whole new level! 🌟",
            f"{wrestler['name']} makes a bold declaration that stuns everyone! 🌟"
        ]
        
        # Pick a random cash-in line
        cash_in_line = random.choice(cash_in_lines)
        
        # Calculate bonus based on momentum (max bonus of 15 points)
        bonus = min(15, momentum / 5) # Increased bonus calculation
        
        # First pause the playback
        was_playing = self.is_playing
        if was_playing:
            self.toggle_play()  # Pause
        
        # Create a special beat to display
        special_html = f'''
            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 10px 0;">
                <tr>
                <!-- Score column - Cash-in gets a special golden color -->
                <td width="80" style="
                    background-color: #665500;
                    border-radius: 8px 0 0 8px;
                    padding: 10px;
                    text-align: center;
                    vertical-align: middle;
                ">
                <div style="
                    font-family: Fira Code;
                    font-weight: bold;
                    font-size: 24pt;
                    color: gold;
                ">+{bonus:.1f}</div>
                </td>
                
                <!-- Beat content column with gold border -->
                <td style="
                    background-color: #333333;
                    border: 2px solid gold;
                    border-radius: 0 8px 8px 0;
                    padding: 10px;
                ">
                <div style="
                    font-family: Fira Code;
                    font-weight: bold;
                    font-size: 14pt;
                    color: gold;
                    margin-bottom: 5px;
                ">🌟 MOMENTUM CASH-IN:</div>
                <div style="
                    font-family: Fira Code;
                    font-size: 14pt;
                    line-height: 1.4;
                    color: #fff;
                    margin: 5px 0;
                ">{cash_in_line}</div>
                <div style="
                    margin: 4px 0;
                    font-family: Fira Code;
                    font-size: 11pt;
                    font-style: italic;
                    color: #FFDD33;
                ">
                    The crowd goes wild as momentum is converted to a scoring bonus!
                </div>
                </td></tr>
            </table>
        '''
        
        # Insert the special beat
        cursor = self.beat_display.textCursor()
        cursor.movePosition(cursor.End)
        self.beat_display.setTextCursor(cursor)
        self.beat_display.insertHtml(special_html)
        
        # Add a gold flash effect to the whole display
        orig_style = self.beat_display.styleSheet()
        self.beat_display.setStyleSheet("""
            QTextEdit {
                font-family: Fira Code;
                font-size: 12pt;
                background-color: #665522;
                color: #ddd;
                border: 2px solid gold;
                border-radius: 8px;
                padding: 10px;
                margin: 0;
            }
        """)
        
        # Auto-scroll to bottom of text display
        scrollbar = self.beat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Reset the momentum meter
        meter.setValue(0)
        
        # After a short delay, restore original style and resume playback if needed
        QTimer.singleShot(2000, lambda: self._finish_cash_in(orig_style, was_playing))
        
    def _finish_cash_in(self, orig_style, was_playing):
        """Helper function to complete the cash-in animation and resume playback."""
        # Restore original style
        self.beat_display.setStyleSheet(orig_style)
        
        # Resume playback if it was playing before
        if was_playing and not self.is_playing:
            self.toggle_play()

class PromoSummaryWidget(QWidget):
    """Widget for displaying the promo summary on a separate screen."""
    
    continue_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.promo_result = None
        self.initUI()
        self.setVisible(False)
        
    def initUI(self):
        """Initialize the UI elements."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        self.setLayout(layout)
        
        # Create a stylish container for the summary
        summary_container = QGroupBox()
        summary_container.setStyleSheet("""
            QGroupBox {
                background-color: #2a2a2a;
                border: 2px solid #555;
                border-radius: 10px;
                margin-top: 15px;
            }
        """)
        summary_layout = QVBoxLayout(summary_container)
        summary_layout.setSpacing(5)
        summary_layout.setContentsMargins(10, 10, 10, 10)
        
        # Top section (compact)
        top_section = QHBoxLayout()
        
        # Left side - Title and Score
        left_section = QVBoxLayout()
        
        # Title
        self.title_label = QLabel("Promo Complete")
        self.title_label.setStyleSheet("""
            font-family: Fira Code;
            font-size: 18pt;
            font-weight: bold;
            color: #fff;
        """)
        self.title_label.setAlignment(Qt.AlignLeft)
        left_section.addWidget(self.title_label)
        
        # Score
        self.score_label = QLabel("Score: 100.0")
        self.score_label.setStyleSheet("""
            font-family: Fira Code;
            font-size: 14pt;
            color: #fff;
        """)
        self.score_label.setAlignment(Qt.AlignLeft)
        left_section.addWidget(self.score_label)
        
        top_section.addLayout(left_section, 3)
        
        # Right side - Star rating and quality
        right_section = QVBoxLayout()
        
        # Star rating
        self.star_rating = QLabel("★★★★★")
        self.star_rating.setStyleSheet("""
            font-family: Fira Code;
            font-size: 20pt;
            color: gold;
            text-align: right;
        """)
        self.star_rating.setAlignment(Qt.AlignRight)
        right_section.addWidget(self.star_rating)
        
        # Quality text
        self.quality_label = QLabel("Excellent!")
        self.quality_label.setStyleSheet("""
            font-family: Fira Code;
            font-size: 14pt;
            color: #4CAF50;
            text-align: right;
        """)
        self.quality_label.setAlignment(Qt.AlignRight)
        right_section.addWidget(self.quality_label)
        
        top_section.addLayout(right_section, 2)
        summary_layout.addLayout(top_section)
        
        # Horizontal line separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #555;")
        summary_layout.addWidget(line)
        
        # Wrestler scores (for versus promos)
        self.versus_container = QWidget()
        versus_layout = QHBoxLayout(self.versus_container)
        versus_layout.setContentsMargins(5, 5, 5, 5)
        versus_layout.setSpacing(5)
        
        # Wrestler 1 score
        self.w1_container = QGroupBox()
        self.w1_container.setStyleSheet("""
            QGroupBox {
                background-color: #333;
                border: 1px solid #66CCFF;
                border-radius: 8px;
                padding: 5px;
                margin: 5px;
            }
        """)
        w1_layout = QVBoxLayout(self.w1_container)
        w1_layout.setContentsMargins(5, 5, 5, 5)
        w1_layout.setSpacing(2)
        
        self.w1_name = QLabel("Wrestler 1")
        self.w1_name.setStyleSheet("""
            font-family: Fira Code;
            font-size: 12pt;
            font-weight: bold;
            color: #66CCFF;
            text-align: center;
        """)
        self.w1_name.setAlignment(Qt.AlignCenter)
        w1_layout.addWidget(self.w1_name)
        
        self.w1_score = QLabel("Score: 0.0")
        self.w1_score.setStyleSheet("""
            font-family: Fira Code;
            font-size: 11pt;
            color: #fff;
            text-align: center;
        """)
        self.w1_score.setAlignment(Qt.AlignCenter)
        w1_layout.addWidget(self.w1_score)
        
        versus_layout.addWidget(self.w1_container)
        
        # Versus label
        self.versus_label = QLabel("VS")
        self.versus_label.setStyleSheet("""
            font-family: Fira Code;
            font-size: 14pt;
            font-weight: bold;
            color: #fff;
            text-align: center;
        """)
        self.versus_label.setAlignment(Qt.AlignCenter)
        versus_layout.addWidget(self.versus_label)
        
        # Wrestler 2 score
        self.w2_container = QGroupBox()
        self.w2_container.setStyleSheet("""
            QGroupBox {
                background-color: #333;
                border: 1px solid #FF9966;
                border-radius: 8px;
                padding: 5px;
                margin: 5px;
            }
        """)
        w2_layout = QVBoxLayout(self.w2_container)
        w2_layout.setContentsMargins(5, 5, 5, 5)
        w2_layout.setSpacing(2)
        
        self.w2_name = QLabel("Wrestler 2")
        self.w2_name.setStyleSheet("""
            font-family: Fira Code;
            font-size: 12pt;
            font-weight: bold;
            color: #FF9966;
            text-align: center;
        """)
        self.w2_name.setAlignment(Qt.AlignCenter)
        w2_layout.addWidget(self.w2_name)
        
        self.w2_score = QLabel("Score: 0.0")
        self.w2_score.setStyleSheet("""
            font-family: Fira Code;
            font-size: 11pt;
            color: #fff;
            text-align: center;
        """)
        self.w2_score.setAlignment(Qt.AlignCenter)
        w2_layout.addWidget(self.w2_score)
        
        versus_layout.addWidget(self.w2_container)
        
        summary_layout.addWidget(self.versus_container)
        
        # Winner banner
        self.winner_label = QLabel("Winner: Wrestler 1")
        self.winner_label.setStyleSheet("""
            font-family: Fira Code;
            font-size: 14pt;
            font-weight: bold;
            color: gold;
            background-color: #333;
            border-radius: 8px;
            padding: 5px;
            margin: 5px;
            text-align: center;
        """)
        self.winner_label.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(self.winner_label)
        
        # Highlights section - make it more compact
        self.highlights_container = QGroupBox("Highlights")
        self.highlights_container.setStyleSheet("""
            QGroupBox {
                font-family: Fira Code;
                font-size: 12pt;
                color: #ddd;
                background-color: #333;
                border: 1px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        highlights_layout = QVBoxLayout(self.highlights_container)
        highlights_layout.setContentsMargins(5, 10, 5, 5)
        highlights_layout.setSpacing(2)
        
        # Make highlights scrollable with a maximum height
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        scroll_area.setMaximumHeight(80)  # Limit height
        
        highlights_widget = QWidget()
        highlights_inner_layout = QVBoxLayout(highlights_widget)
        highlights_inner_layout.setContentsMargins(5, 5, 5, 5)
        
        self.highlights_text = QLabel("No highlights available.")
        self.highlights_text.setStyleSheet("""
            font-family: Fira Code;
            font-size: 11pt;
            color: #bbb;
            margin: 0px;
        """)
        self.highlights_text.setWordWrap(True)
        highlights_inner_layout.addWidget(self.highlights_text)
        
        scroll_area.setWidget(highlights_widget)
        highlights_layout.addWidget(scroll_area)
        
        summary_layout.addWidget(self.highlights_container)
        
        # Continue button
        self.continue_button = QPushButton("Continue")
        self.continue_button.setStyleSheet("""
            QPushButton {
                font-family: Fira Code;
                font-size: 12pt;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0a5999;
            }
        """)
        self.continue_button.setFixedHeight(40)
        self.continue_button.clicked.connect(self.on_continue)
        summary_layout.addWidget(self.continue_button)
        
        # Add the summary container to the main layout
        layout.addWidget(summary_container)
        
        # Initially hide the versus-specific elements
        self.versus_container.setVisible(False)
        self.winner_label.setVisible(False)
        
        # Set a maximum height for the entire summary widget
        self.setMaximumHeight(350)  # Reduced from 400 to 350

    def on_continue(self):
        """Handle the continue button click."""
        self.setVisible(False)
        self.continue_clicked.emit()
    
    def show_single_summary(self, result):
        """Display a single promo summary."""
        self.promo_result = result
        
        # Hide versus-specific elements
        self.versus_container.setVisible(False)
        self.winner_label.setVisible(False)
        
        # Set title
        self.title_label.setText("Promo Complete")
        
        # Get score and calculate stars
        score = result.get("final_rating", 0)
        stars = min(5, score / 20)  # 100 points = 5 stars
        
        # Update score display
        self.score_label.setText(f"Score: {score:.1f}")
        
        # Update star rating
        star_display = ""
        full_stars = int(stars)
        partial = stars - full_stars
        
        star_display = "★" * full_stars
        if partial >= 0.75:
            star_display += "★"
        elif partial >= 0.25:
            star_display += "½"
            
        # Pad with empty stars
        empty_stars = 5 - len(star_display)
        if partial >= 0.25 and partial < 0.75:
            empty_stars -= 1
        star_display += "☆" * empty_stars
            
        self.star_rating.setText(star_display)
        
        # Set quality text and color
        if score >= 90:
            quality = "Perfect!"
            color = "#E91E63"  # Pink
        elif score >= 80:
            quality = "Excellent!"
            color = "#4CAF50"  # Green
        elif score >= 70:
            quality = "Great!"
            color = "#2196F3"  # Blue
        elif score >= 60:
            quality = "Good"
            color = "#FF9800"  # Orange
        elif score >= 50:
            quality = "Average"
            color = "#FFC107"  # Amber
        elif score >= 30:
            quality = "Poor"
            color = "#FF5722"  # Deep Orange
        else:
            quality = "Terrible"
            color = "#F44336"  # Red
            
        self.quality_label.setText(quality)
        self.quality_label.setStyleSheet(f"""
            font-family: Fira Code;
            font-size: 14pt;
            color: {color};
        """)
        
        # Update highlights
        if "highlights" in result and result["highlights"]:
            highlights_html = "<ul>"
            for highlight in result["highlights"]:
                highlights_html += f"<li>{highlight}</li>"
            highlights_html += "</ul>"
            self.highlights_text.setText(highlights_html)
        else:
            self.highlights_text.setText("No highlights available.")
            
        # Show the summary screen
        self.setVisible(True)
    
    def show_versus_summary(self, result, wrestler1, wrestler2):
        """Display a versus promo summary."""
        self.promo_result = result
        
        # Show versus-specific elements
        self.versus_container.setVisible(True)
        
        # Set title
        self.title_label.setText("Versus Promo Complete")
        
        # Get scores
        scores = result["final_scores"]
        w1_score = scores["wrestler1_score"]
        w2_score = scores["wrestler2_score"]
        overall_score = scores["overall_score"]
        
        # Calculate stars based on overall score
        stars = min(5, overall_score / 20)  # 100 points = 5 stars
        
        # Update score displays
        self.score_label.setText(f"Overall Score: {overall_score:.1f}")
        self.w1_name.setText(wrestler1["name"])
        self.w1_score.setText(f"Score: {w1_score:.1f}")
        self.w2_name.setText(wrestler2["name"])
        self.w2_score.setText(f"Score: {w2_score:.1f}")
        
        # Update star rating
        star_display = ""
        full_stars = int(stars)
        partial = stars - full_stars
        
        star_display = "★" * full_stars
        if partial >= 0.75:
            star_display += "★"
        elif partial >= 0.25:
            star_display += "½"
            
        # Pad with empty stars
        empty_stars = 5 - len(star_display)
        if partial >= 0.25 and partial < 0.75:
            empty_stars -= 1
        star_display += "☆" * empty_stars
            
        self.star_rating.setText(star_display)
        
        # Set quality text and color based on overall score
        if overall_score >= 90:
            quality = "Perfect!"
            color = "#E91E63"  # Pink
        elif overall_score >= 80:
            quality = "Excellent!"
            color = "#4CAF50"  # Green
        elif overall_score >= 70:
            quality = "Great!"
            color = "#2196F3"  # Blue
        elif overall_score >= 60:
            quality = "Good"
            color = "#FF9800"  # Orange
        elif overall_score >= 50:
            quality = "Average"
            color = "#FFC107"  # Amber
        elif overall_score >= 30:
            quality = "Poor"
            color = "#FF5722"  # Deep Orange
        else:
            quality = "Terrible"
            color = "#F44336"  # Red
            
        self.quality_label.setText(quality)
        self.quality_label.setStyleSheet(f"""
            font-family: Fira Code;
            font-size: 14pt;
            color: {color};
        """)
        
        # Determine winner and show winner banner
        if w1_score > w2_score + 5:
            winner_text = f"Winner: {wrestler1['name']}"
            self.winner_label.setVisible(True)
        elif w2_score > w1_score + 5:
            winner_text = f"Winner: {wrestler2['name']}"
            self.winner_label.setVisible(True)
        else:
            winner_text = "Result: Even Match"
            self.winner_label.setVisible(True)
            
        self.winner_label.setText(winner_text)
        
        # Update highlights section - versus promos don't have highlights currently
        self.highlights_text.setText("No highlights available for versus promos.")
        
        # Show the summary screen
        self.setVisible(True)

class PromoTestUI(QWidget):
    def __init__(self, on_finish=None):
        super().__init__()
        self.on_finish = on_finish
        self.promo_result = None
        self.beat_mode_active = False
        self.wrestlers = get_all_wrestlers()
        self.wrestler1 = None
        self.wrestler2 = None
        
        # Set size constraints to prevent the widget from expanding too much
        self.setMinimumHeight(500)
        self.setMaximumHeight(800)
        
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create a scroll area to contain everything
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)  # Remove border
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create a container widget for all content
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a stacked widget to switch between screens
        self.stacked_widget = QWidget()
        stacked_layout = QVBoxLayout(self.stacked_widget)
        stacked_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.addWidget(self.stacked_widget)
        
        # Create main promo screen
        self.promo_screen = QWidget()
        promo_layout = QVBoxLayout(self.promo_screen)
        
        # Wrestler selection area
        selection_area = QHBoxLayout()
        
        # Main wrestler selection
        w1_group = QGroupBox("Promo Wrestler")
        w1_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #e0e0e0;
                border: 1px solid #666;
                border-radius: 5px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
        """)
        w1_layout = QVBoxLayout()
        self.w1_combo = QComboBox()
        self.w1_combo.setStyleSheet("""
            QComboBox {
                background-color: #333;
                color: white;
                padding: 4px;
                font-size: 11pt;
            }
        """)
        self.load_wrestlers(self.w1_combo)
        w1_layout.addWidget(self.w1_combo)
        w1_group.setLayout(w1_layout)
        selection_area.addWidget(w1_group)
        
        # Opponent wrestler selection
        w2_group = QGroupBox("Opponent (Optional)")
        w2_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #e0e0e0;
                border: 1px solid #666;
                border-radius: 5px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
        """)
        w2_layout = QVBoxLayout()
        self.w2_combo = QComboBox()
        self.w2_combo.setStyleSheet("""
            QComboBox {
                background-color: #333;
                color: white;
                padding: 4px;
                font-size: 11pt;
            }
        """)
        self.load_wrestlers(self.w2_combo, include_none=True)
        # Default to None for opponent
        self.w2_combo.setCurrentIndex(0)
        w2_layout.addWidget(self.w2_combo)
        w2_group.setLayout(w2_layout)
        selection_area.addWidget(w2_group)
        
        promo_layout.addLayout(selection_area)
        
        # Promo Setup Controls
        controls_box = QGroupBox("Promo Controls")
        controls_layout = QVBoxLayout()
        controls_box.setLayout(controls_layout)
        
        # Tone and Theme selection
        subject_layout = QHBoxLayout()
        
        # Tone dropdown
        tone_group = QGroupBox("Tone")
        tone_layout = QVBoxLayout()
        self.tone_dropdown = QComboBox()
        self.tone_dropdown.addItems(["boast", "challenge", "insult", "callout", "humble"])
        tone_layout.addWidget(self.tone_dropdown)
        tone_group.setLayout(tone_layout)
        subject_layout.addWidget(tone_group)
        
        # Theme dropdown
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(["legacy", "dominance", "betrayal", "power", "comeback", "respect"])
        theme_layout.addWidget(self.theme_dropdown)
        theme_group.setLayout(theme_layout)
        subject_layout.addWidget(theme_group)
        
        controls_layout.addLayout(subject_layout)
        
        # Speed control
        mode_layout = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(3)
        self.speed_slider.setValue(1)  # Default to 1 second
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(1)
        self.speed_slider.valueChanged.connect(self.update_speed_display)
        
        speed_label = QLabel("Speed:")
        self.speed_display = QLabel("1 second")
        
        mode_layout.addWidget(speed_label)
        mode_layout.addWidget(self.speed_slider)
        mode_layout.addWidget(self.speed_display)
        controls_layout.addLayout(mode_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Promo")
        self.start_button.clicked.connect(self.start_promo)
        button_layout.addWidget(self.start_button)
        
        # Add button to test event promo
        self.test_event_promo_button = QPushButton("Test Event Promo")
        self.test_event_promo_button.clicked.connect(self.test_event_promo)
        apply_styles(self.test_event_promo_button, "button_yellow")
        button_layout.addWidget(self.test_event_promo_button)
        
        controls_layout.addLayout(button_layout)
        promo_layout.addWidget(controls_box)
        
        # Promo display (used for both single and versus promos)
        self.promo_display = PromoDisplayWidget()
        self.promo_display.finished.connect(self.handle_promo_end)
        promo_layout.addWidget(self.promo_display)
        
        # Add promo screen to stacked widget
        stacked_layout.addWidget(self.promo_screen)
        
        # Create summary screen with new widget
        self.summary_screen = PromoSummaryWidget()
        self.summary_screen.continue_clicked.connect(self.handle_continue)
        stacked_layout.addWidget(self.summary_screen)
        
        # Set the scroll content and add to main layout
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
    def load_wrestlers(self, combo, include_none=False):
        """Load wrestler data into the given combobox."""
        combo.clear()
        
        if include_none:
            combo.addItem("None", None)
            
        for wrestler_id, wrestler_name in self.wrestlers:
            combo.addItem(wrestler_name, wrestler_id)

    def handle_promo_end(self):
        """Called when the promo display is complete."""
        # Show the summary screen with appropriate data
        if self.promo_result:
            # Check if this was a versus promo
            if "final_scores" in self.promo_result:
                self.summary_screen.show_versus_summary(self.promo_result, self.wrestler1, self.wrestler2)
            else:
                self.summary_screen.show_single_summary(self.promo_result)
                
            # Make the summary screen visible (it's a widget in the stacked layout)
            self.promo_screen.setVisible(False)
            self.summary_screen.setVisible(True)
        
    def handle_continue(self):
        """Called when the user clicks continue after promo end."""
        # Reset UI for another promo
        self.enable_controls()
        
        # Switch back to the promo screen
        self.summary_screen.setVisible(False)
        self.promo_screen.setVisible(True)
        
        if self.on_finish and self.promo_result:
            self.on_finish(self.promo_result)
            
    def start_promo(self):
        """Start a promo with the selected wrestler(s) and settings."""
        # Disable controls
        self.start_button.setEnabled(False)
        self.speed_slider.setEnabled(False)
        self.w1_combo.setEnabled(False)
        self.w2_combo.setEnabled(False)
        self.tone_dropdown.setEnabled(False)
        self.theme_dropdown.setEnabled(False)
        
        # Get selected wrestlers
        w1_id = self.w1_combo.currentData()
        w2_id = self.w2_combo.currentData()
        
        if not w1_id:
            self.enable_controls()
            return
            
        self.wrestler1 = load_wrestler_by_id(w1_id)
        if not self.wrestler1:
            self.enable_controls()
            return
            
        # Set up tone and theme
        tone = self.tone_dropdown.currentText()
        theme = self.theme_dropdown.currentText()
        
        # Check if we have an opponent selected
        if w2_id:
            # Run versus promo
            self.wrestler2 = load_wrestler_by_id(w2_id)
            if not self.wrestler2:
                self.enable_controls()
                return
                
            # Run the versus promo
            engine = VersusPromoEngine(self.wrestler1, self.wrestler2)
            result = engine.simulate()
            
            # Format the versus promo result into a format that PromoDisplayWidget can handle
            display_beats = self.format_versus_promo_for_display(result, self.wrestler1, self.wrestler2)
            self.promo_result = result  # Store full result for later
            
            # Show in the promo display
            self.promo_display.set_wrestlers(self.wrestler1, self.wrestler2)
            self.promo_display.set_beats(display_beats)
        else:
            # Run single promo
            self.wrestler2 = None
            engine = PromoEngine(
                self.wrestler1,
                tone=tone,
                theme=theme,
                opponent=None
            )
            result = engine.simulate()
            self.promo_result = result
            
            # Show single promo display
            self.promo_display.set_wrestlers(self.wrestler1)
            self.promo_display.set_beats(result["beats"])

    def format_versus_promo_for_display(self, versus_result, wrestler1, wrestler2):
        """Format a versus promo result into a structure PromoDisplayWidget can display."""
        display_beats = []
        
        # Add intro beat - explicitly mark as intro
        intro_beat = {
            "phase": "opening",
            "momentum": 0,
            "confidence": 50,
            "is_first_beat": True,
            "score": 0,
            "promo_line": f"{wrestler1['name']} and {wrestler2['name']} face off in the ring, microphones in hand.",
            "is_intro": True,
            "versus_mode": True
        }
        display_beats.append(intro_beat)
        
        # Process all the actual promo beats
        for beat in versus_result["beats"]:
            if "wrestler" not in beat or "promo_line" not in beat or beat.get("promo_line") is None:
                continue
                
            # Skip any summary lines or intro lines (we'll add our own)
            if isinstance(beat.get("promo_line"), str) and ("summary" in beat.get("promo_line", "").lower() or "face off" in beat.get("promo_line", "").lower()):
                continue
                
            # Determine momentum and confidence
            momentum = beat.get("momentum", 0)
            confidence = beat.get("confidence", 50)
            
            # Determine if this is wrestler1 or wrestler2 speaking
            is_wrestler1 = (beat.get("wrestler") == wrestler1)
            current_wrestler = wrestler1 if is_wrestler1 else wrestler2
            opponent = wrestler2 if is_wrestler1 else wrestler1
            
            # Create the display beat
            display_beat = {
                "phase": beat.get("phase", "middle"),
                "momentum": momentum,
                "confidence": confidence,
                "score": beat.get("score", 50),
                "promo_line": beat.get("promo_line", "..."),
                "wrestler": current_wrestler,
                "versus_mode": True,
                "opponent": opponent,
                "is_versus_beat": True,
                "wrestler_color": "#66CCFF" if is_wrestler1 else "#FF9966"
            }
            
            display_beats.append(display_beat)
        
        # Add summary beat - explicitly mark as summary
        scores = versus_result["final_scores"]
        winner_text = ""
        if scores['wrestler1_score'] > scores['wrestler2_score'] + 5:
            winner_text = f"{wrestler1['name']} won the verbal battle!"
        elif scores['wrestler2_score'] > scores['wrestler1_score'] + 5:
            winner_text = f"{wrestler2['name']} won the verbal battle!"
        else:
            winner_text = "The exchange was fairly even."
            
        summary_text = f"Versus Promo Complete. {wrestler1['name']}: {scores['wrestler1_score']:.1f} | {wrestler2['name']}: {scores['wrestler2_score']:.1f} | {winner_text}"
        
        summary_beat = {
            "phase": "ending",
            "momentum": 0,
            "confidence": 50,
            "is_last_beat": True,
            "score": versus_result["final_scores"]["overall_score"],
            "promo_line": summary_text,
            "final_quality": "good",  # Placeholder quality
            "is_summary": True,
            "versus_mode": True
        }
        display_beats.append(summary_beat)
        
        return display_beats
    
    def enable_controls(self):
        """Re-enable all UI controls."""
        self.start_button.setEnabled(True)
        self.speed_slider.setEnabled(True)
        self.w1_combo.setEnabled(True)
        self.w2_combo.setEnabled(True)
        self.tone_dropdown.setEnabled(True)
        self.theme_dropdown.setEnabled(True)

    def update_speed_display(self):
        """Update the speed display based on the slider value."""
        value = self.speed_slider.value()
        speeds = ["0.5", "1", "2", "3"]
        self.speed_display.setText(f"{speeds[value]} seconds")

    def test_event_promo(self):
        """Test the event promo UI with the currently selected wrestler."""
        # Get main app reference
        parent = self.window()
        
        # Get selected wrestler
        w1_id = self.w1_combo.currentData()
        
        if not w1_id:
            QMessageBox.warning(self, "Error", "Please select a wrestler first.")
            return
            
        # Load the wrestler
        wrestler = load_wrestler_by_id(w1_id)
        if not wrestler:
            QMessageBox.warning(self, "Error", "Could not load selected wrestler.")
            return
            
        # Call the main app's event promo test method if available
        if hasattr(parent, 'load_event_promo_test'):
            parent.load_event_promo_test()
        else:
            # Fall back to direct loading
            from ui.event_promo_ui import EventPromoUI
            
            def on_promo_finish(result):
                QMessageBox.information(
                    self, 
                    "Promo Complete", 
                    f"Event promo complete! Rating: {result.get('final_rating', 0):.1f}"
                )
                
            promo_ui = EventPromoUI(wrestler, on_finish=on_promo_finish)
            parent.clear_right_panel()
            parent.right_panel.addWidget(promo_ui)
            parent.right_panel.setCurrentWidget(promo_ui)
