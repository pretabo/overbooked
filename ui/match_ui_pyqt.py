from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QSizePolicy, QComboBox, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject
from ui.theme import apply_styles
from ui.theme import ShadowTextLabel
from match_engine import simulate_match
from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt
from db.commentary_utils import get_commentary_line
from PyQt5.QtWidgets import QLabel, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal
from diplomacy_hooks import handle_match_relationship_effects
import time
from storyline.storyline_manager import StorylineManager
from PyQt5.QtWidgets import QApplication


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

    def run(self):
        def log_callback(msg):
            attacker = None
            if self.w1["name"] in msg:
                attacker = "w1"
            elif self.w2["name"] in msg:
                attacker = "w2"
            
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

        result = simulate_match(
            self.w1,
            self.w2,
            log_function=log_callback,
            update_callback=lambda a, b: self.update.emit(a, b),
            colour_callback=lambda line: self.colour_commentary.emit(line),
            stats_callback=lambda stats: self.stats_signal.emit(stats),
            fast_mode=self.fast_mode
        )
        self.latest_result = result
        self.finished.emit(result)


class WrestlingMatchUI(QWidget):
    def __init__(self, wrestler1, wrestler2, on_next_match=None, fast_mode=False, diplomacy_system=None):
        super().__init__()
        self.w1 = wrestler1
        self.w2 = wrestler2
        self.on_next_match = on_next_match
        self.match_result = None
        self.paused = False
        self.commentary_queue = []
        self.current_beat = 1  # Track current beat number
        self.current_commentary = []  # Store commentary for current beat
        self.fast_mode = fast_mode
        self.diplomacy_system = diplomacy_system
        
        self.layout = QVBoxLayout(self)
        self.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        self.build_top_row()
        self.build_info_bar()
        self.build_center()
        self.build_controls()

        # Setup timer for smooth UI updates
        self.display_timer = QTimer()
        self.display_timer.setSingleShot(True)
        self.display_timer.timeout.connect(self.process_next_beat)

        QTimer.singleShot(100, self.run_match_threaded)

    def build_top_row(self):
        top = QHBoxLayout()
        top.setSpacing(20)  # Add consistent spacing

        # Left wrestler block
        left_box = QVBoxLayout()
        left_box.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.left_name = ShadowTextLabel(self.w1["name"])
        
        # Fix width and alignment for left name - use ellipsis for long names
        self.left_name.setWordWrap(False)  # Changed to false to prevent layout shifting
        self.left_name.setFixedWidth(300)
        self.left_name.setFixedHeight(100)  # Increased height for bigger text
        self.left_name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Left align with vertical center
        
        # Use much larger font for names
        font = self.left_name.font()
        font.setPointSize(36)  # Increased from 24pt to 36pt for much bigger text
        font.setBold(True)  # Make sure it's bold
        self.left_name.setFont(font)
        
        self.left_name.setStyleSheet("""
            font-family: Georgia, serif;
            font-weight: bold;
            color: #2c3e50;
            padding: 12px;
            border-radius: 8px;
            text-align: left;
            text-overflow: ellipsis;
        """)

        # Create horizontal row with stars + stamina + damage
        self.left_stars = QLabel(self.format_star_stats(self.w1))
        self.left_stars.setStyleSheet("font-family: Fira Code; font-size: 13pt; color: #d4af37;")
        self.left_stars.setFixedWidth(300)  # Added fixed width
        self.left_stars.setAlignment(Qt.AlignLeft)  # Ensure left alignment

        left_box.addWidget(self.left_stars)
        left_box.addWidget(self.left_name)
        left_box.addStretch(1)  # Add stretch to keep everything at top

        # Right wrestler block
        right_box = QVBoxLayout()
        right_box.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.right_name = ShadowTextLabel(self.w2["name"])
        
        # Fix width and alignment for right name
        self.right_name.setWordWrap(False)  # Changed to false to prevent layout shifting
        self.right_name.setFixedWidth(300)
        self.right_name.setFixedHeight(100)  # Increased height for bigger text
        self.right_name.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Right align with vertical center
        
        # Use same font settings
        self.right_name.setFont(font)  # Use the same large font as left name
        
        self.right_name.setStyleSheet("""
            font-family: Georgia, serif;
            font-weight: bold;
            color: #7f1d1d;
            padding: 12px;
            border-radius: 8px;
            text-align: right;
            text-overflow: ellipsis;
        """)

        self.right_stars = QLabel(self.format_star_stats(self.w2))
        self.right_stars.setStyleSheet("font-family: Fira Code; font-size: 13pt; color: #d4af37;")
        self.right_stars.setFixedWidth(300)  # Added fixed width
        self.right_stars.setAlignment(Qt.AlignRight)  # Ensure right alignment

        right_box.addWidget(self.right_stars)
        right_box.addWidget(self.right_name)
        right_box.addStretch(1)  # Add stretch to keep everything at top

        # Momentum block
        center_box = QVBoxLayout()
        center_box.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        
        self.momentum_arrow = QLabel("⇦⇨")
        self.momentum_arrow.setAlignment(Qt.AlignCenter)
        self.momentum_arrow.setStyleSheet("""
            font-size: 46pt;
            font-weight: bold;
            color: orange;
            background-color: #333;
            padding: 8px 16px;
            border-radius: 8px;
        """)
        self.momentum_arrow.setFixedSize(100, 50)
        center_box.addWidget(self.momentum_arrow)
        center_box.addStretch(1)  # Add stretch to keep everything at top

        # Set stretch factors for the layout
        top.addLayout(left_box, 2)
        top.addLayout(center_box, 1)
        top.addLayout(right_box, 2)

        self.layout.addLayout(top)

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
        keys = [
            "Match Quality", "Fan Reaction",
            f"{self.w1['name']} Hits", f"{self.w2['name']} Hits",
            f"{self.w1['name']} Reversals", f"{self.w2['name']} Reversals",
            f"{self.w1['name']} Misses", f"{self.w2['name']} Misses",
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
        if updated1["name"] == self.w1["name"]:
            self.w1.update(updated1)
            self.w2.update(updated2)
        else:
            self.w1.update(updated2)
            self.w2.update(updated1)

        # Update name and star blocks
        self.left_name.setText(self.w1["name"])
        self.right_name.setText(self.w2["name"])
        self.left_stars.setText(self.format_star_stats(self.w1))
        self.right_stars.setText(self.format_star_stats(self.w2))

        # Live stat labels (from latest_result)
        stats = getattr(self.worker, 'latest_result', {})
        if stats:
            self.stat_labels["Match Quality"].setText(f"Match Quality: {stats.get('quality', 0)}")
            self.stat_labels["Fan Reaction"].setText(f"Fan Reaction: {stats.get('reaction', '...')}")
            
            # Add advanced match stats
            self.stat_labels["Flow Streak"].setText(f"Flow Streak: {stats.get('flow_streak', 0)}")
            self.stat_labels["Drama Score"].setText(f"Drama Score: {stats.get('drama_score', 0)}")
            self.stat_labels["False Finishes"].setText(f"False Finishes: {stats.get('false_finishes', 0)}")
            self.stat_labels["Signatures Landed"].setText(f"Signatures Landed: {stats.get('sig_moves_landed', 0)}")
            self.stat_labels["Turns"].setText(f"Match Length: {stats.get('turns', 0)} turns")

            for key in ["hits", "reversals", "misses"]:
                values = stats.get(key, {})
                if isinstance(values, int):
                    values = {
                        self.w1["name"]: values // 2,
                        self.w2["name"]: values // 2
                    }
                self.stat_labels[f"{self.w1['name']} {key.capitalize()}"].setText(f"{self.w1['name']} {key.capitalize()}: {values.get(self.w1['name'], 0)}")
                self.stat_labels[f"{self.w2['name']} {key.capitalize()}"].setText(f"{self.w2['name']} {key.capitalize()}: {values.get(self.w2['name'], 0)}")

        # Set momentum arrow only — no commentary
        if self.w1.get("momentum") and not self.w2.get("momentum"):
            self.momentum_arrow.setText("⇨")
        elif self.w2.get("momentum") and not self.w1.get("momentum"):
            self.momentum_arrow.setText("⇦")
        else:
            self.momentum_arrow.setText("⇦⇨")



        self.left_name.setText(self.w1["name"])
        self.right_name.setText(self.w2["name"])
        self.left_stars.setText(self.format_star_stats(self.w1))
        self.right_stars.setText(self.format_star_stats(self.w2))
        
        # Live update match stats (if available in result)
        stats = getattr(getattr(self, 'worker', None), 'latest_result', None)
        if stats:
            self.stat_labels["Match Quality"].setText(f"Match Quality: {stats.get('quality', 0)}")
            self.stat_labels["Fan Reaction"].setText(f"Fan Reaction: {stats.get('reaction', '...')}")

            reversals = stats.get("reversals", {})
            if isinstance(reversals, int):
                reversals = {
                    self.w1["name"]: reversals // 2,
                    self.w2["name"]: reversals // 2
                }

            stats = getattr(self.worker, 'latest_result', None)
            if not stats:
                return

            # Convert totals to per-wrestler dicts if needed
            for key in ["hits", "reversals", "misses"]:
                if isinstance(stats.get(key), int):
                    stats[key] = {
                        self.w1["name"]: stats[key] // 2,
                        self.w2["name"]: stats[key] // 2
                    }


            for who in [self.w1["name"], self.w2["name"]]:
                self.stat_labels[f"{who} Hits"].setText(f"{who} Hits: {stats.get('hits', {}).get(who, 0)}")
                self.stat_labels[f"{who} Reversals"].setText(f"{who} Reversals: {stats.get('reversals', {}).get(who, 0)}")
                self.stat_labels[f"{who} Misses"].setText(f"{who} Misses: {stats.get('misses', {}).get(who, 0)}")


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
        self.worker.finished.connect(self.handle_match_end)
        self.worker.beat_complete.connect(self.on_beat_completed)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def queue_beat(self, message, attacker):
        """Queue a beat for display without blocking the simulation thread."""
        if not message.strip():
            return
            
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
        
        # Clear the commentary box first
        self.commentary_box.clear()

        # Format the line based on the attacker
        if attacker == "w1":
            color = W1_COLOUR
            self.momentum_arrow.setText("⇨")
        elif attacker == "w2":
            color = W2_COLOUR
            self.momentum_arrow.setText("⇦")
        else:
            color = "#1c1c1c"
            self.momentum_arrow.setText("⇦⇨")

        # Parse momentum and confidence changes
        momentum_info = ""
        if "🌟" in message:
            parts = message.split("(")
            if len(parts) > 1:
                momentum_info = parts[1].strip(")")
                message = parts[0].strip()

        # Create beat HTML
        beat_html = f"""
            <div style='
                background-color: #1a1a1a;
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

        # Add any queued commentary for this beat
        for commentary in self.current_commentary:
            beat_html += f"""
                <div style='
                    margin: 8px 16px;
                    padding: 8px 12px;
                    background-color: #2a2a2a;
                    border-radius: 4px;
                    font-family: Fira Code;
                    font-size: 14pt;
                    font-style: italic;
                    color: #aaaaaa;
                    border-left: 3px solid #444;
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

        # Update stats
        self.update_stats(self.w1, self.w2)

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

    def update_live_stats(self, stats):
        if not stats or not isinstance(stats, dict):
            return

        # Don't overwrite the incoming data!
        hits = stats.get("hits", {})
        revs = stats.get("reversals", {})
        misses = stats.get("misses", {})

        # Fallbacks if stored as totals
        if isinstance(hits, int):
            hits = {self.w1["name"]: hits // 2, self.w2["name"]: hits // 2}
        if isinstance(revs, int):
            revs = {self.w1["name"]: revs // 2, self.w2["name"]: revs // 2}
        if isinstance(misses, int):
            misses = {self.w1["name"]: misses // 2, self.w2["name"]: misses // 2}

        self.stat_labels["Match Quality"].setText(f"Match Quality: {stats.get('quality', 0)}")
        self.stat_labels["Fan Reaction"].setText(f"Fan Reaction: {stats.get('reaction', '...')}")

        for who in [self.w1["name"], self.w2["name"]]:
            self.stat_labels[f"{who} Hits"].setText(f"{who} Hits: {hits.get(who, 0)}")
            self.stat_labels[f"{who} Reversals"].setText(f"{who} Reversals: {revs.get(who, 0)}")
            self.stat_labels[f"{who} Misses"].setText(f"{who} Misses: {misses.get(who, 0)}")
            # Update the advanced live stats
            self.stat_labels["Flow Streak"].setText(f"Flow Streak: {stats.get('flow_streak', 0)}")
            self.stat_labels["Drama Score"].setText(f"Drama Score: {stats.get('drama_score', 0)}")
            self.stat_labels["False Finishes"].setText(f"False Finishes: {stats.get('false_finishes', 0)}")
            self.stat_labels["Signatures Landed"].setText(f"Signatures Landed: {stats.get('sig_moves_landed', 0)}")
            self.stat_labels["Turns"].setText(f"Match Length: {stats.get('turns', 0)} turns")

        quality = stats.get("quality", 0)

        # Convert 0–100 into a 5-star scale with half stars
        if quality >= 99:
            stars = "★★★★★"
        elif quality >= 90:
            stars = "★★★★½"
        elif quality >= 80:
            stars = "★★★★"
        elif quality >= 70:
            stars = "★★★½"
        elif quality >= 60:
            stars = "★★★"
        elif quality >= 50:
            stars = "★★½"
        elif quality >= 40:
            stars = "★★"
        elif quality >= 30:
            stars = "★½"
        else:
            stars = "-"

        self.match_quality_stars.setText(stars)
        
        self.left_stamina.setText(f"Stamina: {self.w1.get('stamina', 0)}")
        self.right_stamina.setText(f"Stamina: {self.w2.get('stamina', 0)}")

        self.left_damage.setText(f"Damage: {self.w1.get('damage_taken', 0)}")
        self.right_damage.setText(f"Damage: {self.w2.get('damage_taken', 0)}")


    def update_stamina_label(label, value):
        if value > 60:
            colour = "#9be7ff"
        elif value > 30:
            colour = "#ffc107"
        else:
            colour = "#ff6f61"
        label.setText(f"Stamina: {value}")
        label.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {colour}; font-family: Fira Code;")


    def show_post_match_summary(self, result):
        """Show match summary with consistent styling."""
        winner = result.get("winner", "???")
        self.speed_slider.setVisible(False)
        self.speed_label_display.setVisible(False)
        self.pause_button.setVisible(False)

        self.commentary_box.setVisible(True)
        self.commentary_box.setText(f"""
            <div style='
                text-align: center;
                padding: 20px;
                background-color: #ffd700;
                border-radius: 10px;
                margin: 20px 0;
            '>
                <div style='
                    font-size: 28pt;
                    font-weight: bold;
                    color: #0028ff;
                    margin-bottom: 10px;
                '>🏆 {winner} Wins!</div>
            </div>
        """)

        # Hide momentum arrow
        self.momentum_arrow.setVisible(False)

    def handle_continue(self):
        if self.on_next_match and self.match_result:
            self.on_next_match(self.match_result)

    def format_star_stats(self, wrestler):
        def stars(val):
            full = int(round(val / 4))  # scale 0–20 → 0–5
            return "⭐" * full + " " * (5 - full)

        return (
            f"STR: {stars(wrestler['strength'])} "
            f"DEX: {stars(wrestler['dexterity'])} "
            f"END: {stars(wrestler['endurance'])} "
            f"INT: {stars(wrestler['intelligence'])} "
            f"CHA: {stars(wrestler['charisma'])}"
        )

    def build_info_bar(self):
        info_bar = QHBoxLayout()
        info_bar.setAlignment(Qt.AlignCenter)

        # Left wrestler stats
        self.left_stamina = QLabel("Stamina: 100")
        self.left_stamina.setFixedWidth(120)
        self.left_stamina.setStyleSheet("font-size: 14pt; font-weight: bold; color: #9be7ff; font-family: Fira Code;")

        self.left_damage = QLabel("Damage: 0")
        self.left_damage.setFixedWidth(120)
        self.left_damage.setStyleSheet("font-size: 14pt; font-weight: bold; color: #ffaaaa; font-family: Fira Code;")

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

        # Right wrestler stats
        self.right_stamina = QLabel("Stamina: 100")
        self.right_stamina.setFixedWidth(120)
        self.right_stamina.setStyleSheet("font-size: 14pt; font-weight: bold; color: #9be7ff; font-family: Fira Code;")

        self.right_damage = QLabel("Damage: 0")
        self.right_damage.setFixedWidth(120)
        self.right_damage.setStyleSheet("font-size: 14pt; font-weight: bold; color: #ffaaaa; font-family: Fira Code;")

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
        """Handle match end with proper timing."""
        self.match_result = result
        
        # Wait until all commentary beats are processed
        def show_end():
            if len(self.commentary_queue) > 0 or self.display_timer.isActive():
                QTimer.singleShot(500, show_end)
                return
                
            # Add final match ended beat
            self.queue_beat("🏁 Match ended!", None)
            
            # Setup handler for after final beat is shown
            def show_winner():
                if self.display_timer.isActive():
                    QTimer.singleShot(500, show_winner)
                    return
                
                # Show winner after all beats are processed
                self.show_post_match_summary(result)
                self.continue_button.setVisible(True)
                
                # Diplomacy adjustment based on match result
                if self.diplomacy_system is not None:
                    handle_match_relationship_effects(self.w1, self.w2, result, self.diplomacy_system)
                
            # Wait for the match end beat to complete, then show winner
            QTimer.singleShot(1500, show_winner)
            
        show_end()

    def on_match_complete(self, result):
        """Handle match completion."""
        # Update wrestler stats
        self.update_wrestler_stats(result)
        
        # Generate potential storylines
        storyline_manager = StorylineManager()
        storyline_manager.generate_potential_storylines_from_match(
            self.wrestler1['id'], self.wrestler2['id'], result
        )
        
        # Show match summary
        self.show_match_summary(result)

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
