from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QHBoxLayout, QProgressBar,
    QSlider, QFrame, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QDateTime, QEasingCurve, pyqtProperty, QPoint
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QLinearGradient, QPen
from match_engine import get_all_wrestlers, load_wrestler_by_id
from ui.theme import apply_styles
import random
from promo.promo_engine import PromoEngine
from promo.promo_engine_helpers import (
    roll_promo_score,
    determine_line_quality
)
from promo.commentary_engine import generate_commentary
import math
import statistics
from storyline.storyline_manager import StorylineManager

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
        self.speed = 2000
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_next_beat)
        self.is_playing = False
        
        self.initUI()
        
        self.play_button.setEnabled(False)
        self.finish_button.setEnabled(False)

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
        
        # Score display widget
        self.score_display = QLabel(self)
        self.score_display.setAlignment(Qt.AlignCenter)
        self.score_display.setStyleSheet("""
            font-family: Fira Code;
            font-size: 20pt;
            font-weight: bold;
            color: #fff;
            padding: 8px;
            background-color: #2a2a2a;
            border-radius: 8px;
            margin: 0;
        """)
        self.score_display.setText("Score: --")
        layout.addWidget(self.score_display)
        
        # Beat display with fixed height and scrolling
        self.beat_display = QTextEdit(self)
        self.beat_display.setReadOnly(True)
        self.beat_display.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.beat_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.beat_display.setFixedHeight(300)  # Reduced fixed height
        self.beat_display.setStyleSheet("""
            QTextEdit {
                font-family: Fira Code;
                font-size: 12pt;  /* Reduced font size */
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
        
        # Meters container with improved styling and fixed height
        meters_container = QGroupBox("")
        meters_container.setFixedHeight(150)  # Fixed height for meters
        meters_container.setStyleSheet("""
            QGroupBox {
                font-family: Fira Code;
                font-size: 14pt;
                color: #ddd;
                border: 2px solid #444;
                border-radius: 8px;
                margin-top: 1em;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        meters_layout = QVBoxLayout(meters_container)
        meters_layout.setSpacing(15)
        
        # Momentum meter with improved label
        momentum_container = QWidget(meters_container)
        momentum_layout = QHBoxLayout(momentum_container)
        momentum_layout.setSpacing(10)
        momentum_layout.setContentsMargins(0, 0, 0, 0)  # Remove container margins
        momentum_label = QLabel("MOMENTUM", momentum_container)
        momentum_label.setFixedWidth(100)  # Fixed width for label
        momentum_label.setStyleSheet("font-family: Fira Code; font-weight: bold; color: #ff6b6b;")
        momentum_layout.addWidget(momentum_label)
        self.momentum_meter = TriangleMomentumMeter(momentum_container)
        self.momentum_meter.setFixedHeight(30)
        momentum_layout.addWidget(self.momentum_meter, stretch=1)
        meters_layout.addWidget(momentum_container)
        
        # Confidence meter with improved label
        confidence_container = QWidget(meters_container)
        confidence_layout = QHBoxLayout(confidence_container)
        confidence_layout.setSpacing(10)
        confidence_layout.setContentsMargins(0, 0, 0, 0)  # Remove container margins
        confidence_label = QLabel("CONFIDENCE", confidence_container)
        confidence_label.setFixedWidth(100)  # Fixed width for label
        confidence_label.setStyleSheet("font-family: Fira Code; font-weight: bold; color: #4ecdc4;")
        confidence_layout.addWidget(confidence_label)
        self.confidence_meter = HealthBarConfidenceMeter(confidence_container)
        self.confidence_meter.setFixedHeight(20)
        confidence_layout.addWidget(self.confidence_meter, stretch=1)
        meters_layout.addWidget(confidence_container)
        
        layout.addWidget(meters_container)
        
        # Speed controls container with fixed height
        speed_container = QWidget(self)
        speed_container.setFixedHeight(50)  # Fixed height for controls
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

    def set_speed_preset(self, preset):
        """Set speed based on preset button."""
        speeds = {"Slow": 3000, "Normal": 2000, "Fast": 1000}  # in milliseconds
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
        self.momentum_meter.setValue(0)
        self.confidence_meter.setValue(50)  # Start at neutral confidence
        self.play_button.setEnabled(True)
        self.finish_button.setEnabled(True)
        
        # Add initial separator
        self.beat_display.insertHtml('<div style="margin: 10px 0;"></div>')
        
        # Start playing automatically
        self.is_playing = True
        self.play_button.setText("Pause")
        self.timer.start(self.speed)

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
            self.finished.emit()
            return

        beat = self.beats[self.current_beat]
        
        # Update meters
        self.momentum_meter.setValue(int(beat["momentum"]))
        self.confidence_meter.setValue(int(beat["confidence"]))
        
        # Get commentary from the engine
        commentary = generate_commentary(beat)
        
        # Update score display with animation
        score_color = self.get_score_color(commentary['score'])
        self.score_display.setStyleSheet(f"""
            font-family: Fira Code;
            font-size: 20pt;
            font-weight: bold;
            color: {score_color};
            padding: 8px;
            background-color: #2a2a2a;
            border-radius: 8px;
            margin: 0;
        """)
        self.score_display.setText(f"{commentary['score']:.1f}")

        # Check if this is a special beat (intro, summary, or cash-in)
        is_intro = commentary.get("is_intro", False)
        is_summary = commentary.get("is_summary", False)
        is_cash_in = "🌟" in commentary["promo_line"]
        
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
        elif is_cash_in:
            beat_html = f'''
                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 10px 0;">
                    <tr><td style="
                        background: linear-gradient(135deg, #2d2d1a 0%, #3d3d2a 100%);
                        border: 1px solid #ffd700;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(255, 215, 0, 0.2);
                        padding: 10px;
                    ">
            '''
        else:
            beat_html = f'''
                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 10px 0;">
                    <tr><td style="
                        border-bottom: 1px solid #333;
                        padding: 10px;
                    ">
            '''
        
        # Add promo lines for non-intro/summary beats
        if not (is_intro or is_summary):
            promo_lines = [line.strip() for line in commentary["promo_line"].split('.') if line.strip()]
            for line in promo_lines:
                # Skip the cash-in marker in the text
                if "🌟" in line:
                    parts = line.split("(")
                    line = parts[0].replace("🌟", "").strip()
                
                beat_html += f'''
                    <div style="
                        margin: 5px 0;
                        font-family: Fira Code;
                        font-size: 16pt;
                        line-height: 1.4;
                        color: {'#ffd700' if is_cash_in else '#fff'};
                        font-weight: bold;
                    ">{line}.</div>
                '''

            # Add commentary lines if present
            if commentary['commentary_line']:
                commentary_lines = [line.strip() for line in commentary['commentary_line'].split('.') if line.strip()]
                for line in commentary_lines:
                    style = 'color: #ffd700;' if commentary.get('is_cash_in') else 'color: #888;'
                    beat_html += f'''
                        <div style="
                            margin: 4px 0;
                            font-family: Fira Code;
                            font-size: 11pt;
                            font-style: italic;
                            line-height: 1.3;
                            {style}
                        ">
                            {line}
                        </div>
                    '''
            
            # Add momentum and confidence info (only for non-cash-in beats)
            if not is_cash_in:
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

            # If this is a special moment (cash-in), add the effect description
            if is_cash_in:
                parts = commentary["promo_line"].split("(")
                if len(parts) > 1:
                    momentum_info = parts[1].strip(")")
                    beat_html += f'''
                        <div style="
                            margin: 6px 0 0 0;
                            font-family: Fira Code;
                            font-size: 11pt;
                            color: #ffd700;
                            text-shadow: 0 0 5px rgba(255, 215, 0, 0.3);
                        ">
                            ✨ {momentum_info}
                        </div>
                    '''
        
        # Close the beat container
        beat_html += '</td></tr></table>'
        
        # Insert the complete beat HTML
        cursor = self.beat_display.textCursor()
        cursor.movePosition(cursor.End)
        self.beat_display.setTextCursor(cursor)
        self.beat_display.insertHtml(beat_html)
        
        # Update rating to show only stars
        _, stars = self.calculate_rolling_rating()
        self.rating_label.setText(f"{self.get_star_display(stars)}")
        
        # Scroll to the new content
        self.beat_display.verticalScrollBar().setValue(
            self.beat_display.verticalScrollBar().maximum()
        )
        
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

class PromoTestUI(QWidget):
    def __init__(self, wrestler, on_finish=None):
        super().__init__()
        self.wrestler = wrestler
        self.on_finish = on_finish
        self.promo_result = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header with wrestler name
        header = QLabel(f"{wrestler['name']}'s Promo")
        header.setStyleSheet("font-size: 24pt; font-weight: bold; color: #fff;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Tone and Theme Selection
        controls = QHBoxLayout()
        
        # Tone dropdown
        tone_group = QGroupBox("Tone")
        tone_layout = QVBoxLayout()
        self.tone_dropdown = QComboBox()
        self.tone_dropdown.addItems(["boast", "insult", "callout", "humble"])
        tone_layout.addWidget(self.tone_dropdown)
        tone_group.setLayout(tone_layout)
        controls.addWidget(tone_group)
        
        # Theme dropdown
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(["legacy", "dominance", "betrayal", "power", "comeback"])
        theme_layout.addWidget(self.theme_dropdown)
        theme_group.setLayout(theme_layout)
        controls.addWidget(theme_group)
        
        layout.addLayout(controls)

        # Start button
        self.start_button = QPushButton("Start Promo")
        self.start_button.clicked.connect(self.start_promo)
        apply_styles(self.start_button, "button_blue")
        layout.addWidget(self.start_button)

        # Promo display area
        self.display_widget = PromoDisplayWidget()
        self.display_widget.finished.connect(self.handle_promo_end)
        layout.addWidget(self.display_widget)

        # Continue button (hidden initially)
        self.continue_button = QPushButton("Continue")
        apply_styles(self.continue_button, "button_blue")
        self.continue_button.clicked.connect(self.handle_continue)
        self.continue_button.setVisible(False)
        layout.addWidget(self.continue_button)

    def start_promo(self):
        # Disable controls
        self.start_button.setEnabled(False)
        self.tone_dropdown.setEnabled(False)
        self.theme_dropdown.setEnabled(False)
        
        # Run promo simulation
        engine = PromoEngine(
            self.wrestler,
            tone=self.tone_dropdown.currentText(),
            theme=self.theme_dropdown.currentText()
        )
        result = engine.simulate()
        self.promo_result = result
        
        # Display the promo
        self.display_widget.set_beats(result["beats"])

    def handle_promo_end(self):
        """Called when the promo display is complete."""
        self.continue_button.setVisible(True)
        
    def handle_continue(self):
        """Called when the user clicks continue after promo end."""
        if self.on_finish and self.promo_result:
            self.on_finish(self.promo_result)

    def on_promo_complete(self, result):
        """Handle promo completion."""
        # Generate potential storylines
        storyline_manager = StorylineManager()
        storyline_manager.generate_potential_storylines_from_promo(
            self.wrestler['id'], result
        )
        
        # Show promo summary
        self.show_promo_summary(result)
