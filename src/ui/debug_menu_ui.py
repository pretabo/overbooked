"""
Debug Menu UI for Overbooked

This UI provides various debugging and testing tools to help with development.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QGroupBox, QScrollArea, QFrame,
    QLineEdit, QFormLayout, QSpinBox, QMessageBox, QSplitter,
    QTabWidget
)
from PyQt5.QtCore import Qt, QTimer
import logging
import game_state_debug
import time
import os
import json

from ui.theme import apply_styles

class DebugMenuUI(QWidget):
    def __init__(self):
        super().__init__()
        logging.info("Initializing Debug Menu UI")
        
        self.console_log_active = False
        self.console_log_buffer = []
        
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Header
        header = QLabel("🐞 Debug & Testing Menu")
        apply_styles(header, "label_header")
        main_layout.addWidget(header)
        
        # Create tab widget
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Game state tab
        game_state_tab = QWidget()
        game_state_layout = QVBoxLayout(game_state_tab)
        
        # Quick actions group
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()
        actions_group.setLayout(actions_layout)
        
        # Game summary button
        game_summary_btn = QPushButton("Print Game Summary")
        game_summary_btn.clicked.connect(self.print_game_summary)
        apply_styles(game_summary_btn, "button_blue")
        actions_layout.addWidget(game_summary_btn)
        
        # Export state button
        export_btn = QPushButton("Export Debug State")
        export_btn.clicked.connect(game_state_debug.export_debug_state)
        apply_styles(export_btn, "button_blue")
        actions_layout.addWidget(export_btn)
        
        # Reset stats button
        reset_btn = QPushButton("Reset Debug Stats")
        reset_btn.clicked.connect(game_state_debug.reset_stats)
        apply_styles(reset_btn, "button_blue")
        actions_layout.addWidget(reset_btn)
        
        game_state_layout.addWidget(actions_group)
        
        # Wrestler details group
        wrestler_group = QGroupBox("Wrestler Details")
        wrestler_layout = QHBoxLayout()
        wrestler_group.setLayout(wrestler_layout)
        
        self.wrestler_id_input = QSpinBox()
        self.wrestler_id_input.setMinimum(1)
        self.wrestler_id_input.setMaximum(9999)
        wrestler_layout.addWidget(QLabel("Wrestler ID:"))
        wrestler_layout.addWidget(self.wrestler_id_input)
        
        wrestler_btn = QPushButton("Show Details")
        wrestler_btn.clicked.connect(self.show_wrestler_details)
        apply_styles(wrestler_btn, "button_blue")
        wrestler_layout.addWidget(wrestler_btn)
        
        game_state_layout.addWidget(wrestler_group)
        
        # Console log
        console_group = QGroupBox("Console Output")
        console_layout = QVBoxLayout()
        console_group.setLayout(console_layout)
        
        console_controls = QHBoxLayout()
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setLineWrapMode(QTextEdit.NoWrap)
        self.console_output.setStyleSheet("""
            background-color: #0f0f0f;
            color: #00ff00;
            font-family: monospace;
        """)
        
        start_console = QPushButton("Start Console Capture")
        start_console.clicked.connect(self.toggle_console_capture)
        apply_styles(start_console, "button_blue")
        self.console_button = start_console
        
        clear_console = QPushButton("Clear Console")
        clear_console.clicked.connect(self.clear_console)
        apply_styles(clear_console, "button_red")
        
        console_controls.addWidget(start_console)
        console_controls.addWidget(clear_console)
        
        console_layout.addLayout(console_controls)
        console_layout.addWidget(self.console_output)
        
        game_state_layout.addWidget(console_group)
        
        # Performance tab
        performance_tab = QWidget()
        performance_layout = QVBoxLayout(performance_tab)
        
        # Simulation testing
        sim_group = QGroupBox("Simulation Testing")
        sim_layout = QVBoxLayout()
        sim_group.setLayout(sim_layout)
        
        form = QFormLayout()
        
        self.match_count = QSpinBox()
        self.match_count.setMinimum(1)
        self.match_count.setMaximum(100)
        self.match_count.setValue(10)
        form.addRow("Number of Test Matches:", self.match_count)
        
        self.promo_count = QSpinBox()
        self.promo_count.setMinimum(1)
        self.promo_count.setMaximum(100)
        self.promo_count.setValue(10)
        form.addRow("Number of Test Promos:", self.promo_count)
        
        sim_layout.addLayout(form)
        
        sim_buttons = QHBoxLayout()
        
        run_matches = QPushButton("Run Test Matches")
        run_matches.clicked.connect(self.run_test_matches)
        apply_styles(run_matches, "button_blue")
        sim_buttons.addWidget(run_matches)
        
        run_promos = QPushButton("Run Test Promos")
        run_promos.clicked.connect(self.run_test_promos)
        apply_styles(run_promos, "button_blue")
        sim_buttons.addWidget(run_promos)
        
        sim_layout.addLayout(sim_buttons)
        performance_layout.addWidget(sim_group)
        
        # Stats display
        stats_group = QGroupBox("Performance Statistics")
        stats_layout = QVBoxLayout()
        stats_group.setLayout(stats_layout)
        
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        stats_layout.addWidget(self.stats_display)
        
        refresh_stats = QPushButton("Refresh Stats")
        refresh_stats.clicked.connect(self.update_stats_display)
        apply_styles(refresh_stats, "button_blue")
        stats_layout.addWidget(refresh_stats)
        
        performance_layout.addWidget(stats_group)
        
        # Add tabs
        tabs.addTab(game_state_tab, "Game State")
        tabs.addTab(performance_tab, "Performance")
        
        # Update stats initially
        self.update_stats_display()
        
        # Setup timer for console updates
        self.console_timer = QTimer()
        self.console_timer.timeout.connect(self.update_console)
        
        logging.info("Debug Menu UI initialized")
    
    def toggle_console_capture(self):
        self.console_log_active = not self.console_log_active
        
        if self.console_log_active:
            self.console_button.setText("Stop Console Capture")
            logging.info("Console capture started")
            self.console_timer.start(1000)  # Update every second
        else:
            self.console_button.setText("Start Console Capture")
            logging.info("Console capture stopped")
            self.console_timer.stop()
    
    def clear_console(self):
        self.console_output.clear()
        self.console_log_buffer = []
        logging.info("Console cleared")
    
    def update_console(self):
        """Update the console output with recent log entries"""
        if not self.console_log_active:
            return
            
        # Check if the log file exists
        try:
            log_files = [f for f in os.listdir('logs') if f.startswith('overbooked_')]
            if not log_files:
                return
                
            # Get the most recent log file
            latest_log = max(log_files, key=lambda f: os.path.getmtime(os.path.join('logs', f)))
            log_path = os.path.join('logs', latest_log)
            
            # Read the last few lines
            with open(log_path, 'r') as f:
                lines = f.readlines()
                
            # Get only new lines
            if lines:
                if not self.console_log_buffer:
                    # First time, get last 20 lines
                    new_lines = lines[-20:]
                else:
                    # Find new lines since last update
                    last_line = self.console_log_buffer[-1] if self.console_log_buffer else ""
                    try:
                        last_idx = lines.index(last_line)
                        new_lines = lines[last_idx+1:]
                    except ValueError:
                        new_lines = lines[-10:]  # If can't find last line, get last 10
                
                if new_lines:
                    self.console_log_buffer.extend(new_lines)
                    # Keep buffer at a reasonable size
                    if len(self.console_log_buffer) > 500:
                        self.console_log_buffer = self.console_log_buffer[-500:]
                    
                    # Update the display
                    self.console_output.append("".join(new_lines))
                    # Scroll to bottom
                    scrollbar = self.console_output.verticalScrollBar()
                    scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
            logging.error(f"Error updating console: {e}")
    
    def print_game_summary(self):
        """Print a summary of the current game state"""
        game_state_debug.print_game_summary()
        QMessageBox.information(self, "Game Summary", 
                               "Game summary has been printed to the log.\nCheck the console or log file.")
    
    def show_wrestler_details(self):
        """Show details for a specific wrestler"""
        wrestler_id = self.wrestler_id_input.value()
        game_state_debug.print_wrestler_details(wrestler_id)
        QMessageBox.information(self, "Wrestler Details", 
                               f"Details for wrestler ID {wrestler_id} have been printed to the log.")
    
    def update_stats_display(self):
        """Update the performance statistics display"""
        stats = game_state_debug.performance_stats
        
        text = "=== PERFORMANCE STATISTICS ===\n\n"
        
        # Match stats
        text += "MATCH SIMULATION\n"
        text += f"Total simulations: {stats['match_simulations']}\n"
        if stats['match_simulations'] > 0:
            avg_time = stats['match_simulation_time'] / stats['match_simulations']
            text += f"Total time: {stats['match_simulation_time']:.2f}s\n"
            text += f"Average time: {avg_time:.2f}s\n"
        text += "\n"
        
        # Promo stats
        text += "PROMO GENERATION\n"
        text += f"Total generations: {stats['promo_generations']}\n"
        if stats['promo_generations'] > 0:
            avg_time = stats['promo_generation_time'] / stats['promo_generations']
            text += f"Total time: {stats['promo_generation_time']:.2f}s\n"
            text += f"Average time: {avg_time:.2f}s\n"
        text += "\n"
        
        # Other stats
        text += "OTHER STATISTICS\n"
        text += f"Diplomacy adjustments: {stats['diplomacy_adjustments']}\n"
        text += f"Storyline updates: {stats['storyline_updates']}\n"
        text += f"Last reset: {stats['last_reset']}\n"
        
        self.stats_display.setText(text)
    
    def run_test_matches(self):
        """Run a batch of test matches for performance testing"""
        count = self.match_count.value()
        logging.info(f"Running {count} test matches...")
        
        try:
            from match_engine import get_all_wrestlers, load_wrestler_by_id, simulate_match
            import random
            
            wrestlers = get_all_wrestlers()
            if len(wrestlers) < 2:
                QMessageBox.warning(self, "Error", "Not enough wrestlers in database.")
                return
            
            wrestler_ids = [w[0] for w in wrestlers]
            
            QMessageBox.information(self, "Testing Started", 
                                   f"Running {count} test matches. This may take a while.\n"
                                   "Check the console for progress updates.")
            
            total_time = 0
            for i in range(count):
                # Pick random wrestlers
                w1_id, w2_id = random.sample(wrestler_ids, 2)
                w1 = load_wrestler_by_id(w1_id)
                w2 = load_wrestler_by_id(w2_id)
                
                # Measure time
                start_time = time.time()
                
                # Run simulation with minimal logging
                def minimal_log(msg):
                    pass
                
                logging.info(f"Test match {i+1}/{count}: {w1['name']} vs {w2['name']}")
                result = simulate_match(w1, w2, log_function=minimal_log, fast_mode=True)
                
                duration = time.time() - start_time
                game_state_debug.track_match_simulation(duration)
                total_time += duration
                
                logging.info(f"Match {i+1} completed in {duration:.2f}s")
            
            avg_time = total_time / count
            logging.info(f"All test matches completed. Average time: {avg_time:.2f}s")
            self.update_stats_display()
            
            QMessageBox.information(self, "Testing Complete", 
                                   f"Completed {count} test matches.\n"
                                   f"Average time: {avg_time:.2f}s")
        except Exception as e:
            logging.error(f"Error running test matches: {e}")
            QMessageBox.critical(self, "Error", f"Failed to run test matches: {str(e)}")
    
    def run_test_promos(self):
        """Run a batch of test promos for performance testing"""
        count = self.promo_count.value()
        logging.info(f"Running {count} test promos...")
        
        try:
            from promo.engine import generate_promo
            from match_engine import get_all_wrestlers, load_wrestler_by_id
            import random
            
            wrestlers = get_all_wrestlers()
            if not wrestlers:
                QMessageBox.warning(self, "Error", "No wrestlers in database.")
                return
            
            wrestler_ids = [w[0] for w in wrestlers]
            
            QMessageBox.information(self, "Testing Started", 
                                   f"Running {count} test promos. This may take a while.\n"
                                   "Check the console for progress updates.")
            
            total_time = 0
            for i in range(count):
                # Pick random wrestler
                w_id = random.choice(wrestler_ids)
                wrestler = load_wrestler_by_id(w_id)
                
                # Measure time
                start_time = time.time()
                
                # Generate promo
                logging.info(f"Test promo {i+1}/{count}: {wrestler['name']}")
                
                try:
                    # Try to generate promo
                    promo_text = generate_promo(
                        wrestler,
                        focus=random.randint(5, 15),
                        difficulty=random.randint(5, 15),
                        style="boast",
                        theme="legacy"
                    )
                    
                    duration = time.time() - start_time
                    game_state_debug.track_promo_generation(duration)
                    total_time += duration
                    
                    logging.info(f"Promo {i+1} completed in {duration:.2f}s")
                except Exception as e:
                    logging.error(f"Error generating promo {i+1}: {e}")
            
            if count > 0:
                avg_time = total_time / count
                logging.info(f"All test promos completed. Average time: {avg_time:.2f}s")
                self.update_stats_display()
                
                QMessageBox.information(self, "Testing Complete", 
                                      f"Completed {count} test promos.\n"
                                      f"Average time: {avg_time:.2f}s")
        except Exception as e:
            logging.error(f"Error running test promos: {e}")
            QMessageBox.critical(self, "Error", f"Failed to run test promos: {str(e)}") 