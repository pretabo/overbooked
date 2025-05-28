from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QSpinBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QFormLayout, QGroupBox, QScrollArea, QSizePolicy, QTextEdit,
    QHeaderView, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QFont
import sqlite3
import time

from src.core.match_engine import load_wrestler_by_id, simulate_match
from src.core.match_engine_utils import move_success, select_progressive_manoeuvre
from src.ui.theme import apply_styles
from db.utils import db_path

class SimulationWorker(QObject):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(int, int)  # current match, total matches
    
    def __init__(self, w1, w2, num_matches, diplomacy_system=None):
        super().__init__()
        self.w1 = w1
        self.w2 = w2
        self.num_matches = num_matches
        self.diplomacy_system = diplomacy_system
    
    def run(self):
        results = {
            "matches": [],
            "w1_stats": self._create_empty_stats(),
            "w2_stats": self._create_empty_stats(),
            "w1_move_exp": {},  # Move name -> experience
            "w2_move_exp": {},  # Move name -> experience
            "relationship_change": 0  # Track total relationship change
        }
        
        for i in range(self.num_matches):
            # Collect log of moves for this match
            move_log = []
            
            # Define a log function that captures the move log
            def log_function(msg):
                pass  # We don't need to print messages in simulation mode
            
            # Create a callback that captures statistics
            def stats_callback(stats):
                # Track who hit/missed what
                if "hits" in stats and isinstance(stats["hits"], dict):
                    for name, count in stats["hits"].items():
                        if name == self.w1["name"]:
                            results["w1_stats"]["hits"] = count
                        elif name == self.w2["name"]:
                            results["w2_stats"]["hits"] = count
                
                # Track reversals
                if "reversals" in stats and isinstance(stats["reversals"], dict):
                    for name, count in stats["reversals"].items():
                        if name == self.w1["name"]:
                            results["w1_stats"]["reversals"] = count
                        elif name == self.w2["name"]:
                            results["w2_stats"]["reversals"] = count
            
            # Use fast mode for simulation
            match_result = simulate_match(
                self.w1, 
                self.w2, 
                log_function=log_function,
                stats_callback=stats_callback,
                fast_mode=True
            )
            
            # Process the match results
            results["matches"].append(match_result)
            
            # Update win/loss records
            if match_result["winner"] == self.w1["name"]:
                results["w1_stats"]["wins"] += 1
                results["w2_stats"]["losses"] += 1
            else:
                results["w2_stats"]["wins"] += 1
                results["w1_stats"]["losses"] += 1
            
            # Track match quality
            w1_quality_sum = results["w1_stats"].get("quality_sum", 0) + match_result["quality"]
            w2_quality_sum = results["w2_stats"].get("quality_sum", 0) + match_result["quality"]
            results["w1_stats"]["quality_sum"] = w1_quality_sum
            results["w2_stats"]["quality_sum"] = w2_quality_sum
            
            # Update relationship if diplomacy system is available
            if self.diplomacy_system:
                # Import here to avoid circular imports
                from src.core.diplomacy_hooks import handle_match_relationship_effects
                
                # Update relationship based on match result - use wrestler IDs instead of names
                old_relationship = self.diplomacy_system.get_relationship(self.w1["id"], self.w2["id"])
                
                # Handle relationship effects
                handle_match_relationship_effects(self.w1, self.w2, match_result, self.diplomacy_system)
                
                # Calculate the change in relationship
                new_relationship = self.diplomacy_system.get_relationship(self.w1["id"], self.w2["id"])
                results["relationship_change"] += (new_relationship - old_relationship)
            
            # Update progress signal
            self.progress.emit(i + 1, self.num_matches)
        
        # Calculate average match quality
        if len(results["matches"]) > 0:
            results["w1_stats"]["avg_match_quality"] = results["w1_stats"]["quality_sum"] / len(results["matches"])
            results["w2_stats"]["avg_match_quality"] = results["w2_stats"]["quality_sum"] / len(results["matches"])
        
        # Process wrestler stats after all matches
        self._process_move_experience(self.w1["id"], results["w1_move_exp"])
        self._process_move_experience(self.w2["id"], results["w2_move_exp"])
        
        self.finished.emit(results)
    
    def _create_empty_stats(self):
        """Create empty stats structure for tracking wrestler performance"""
        return {
            "wins": 0,
            "losses": 0,
            "hits": 0,
            "reversals": 0,
            "quality_sum": 0,
            "avg_match_quality": 0
        }
    
    def _process_move_experience(self, wrestler_id, move_exp_dict):
        """Get the wrestler's move experience from the database"""
        conn = sqlite3.connect(db_path("wrestlers.db"))
        cursor = conn.cursor()
        
        # Query the wrestler's move experience
        cursor.execute("""
            SELECT move_name, experience, times_used, times_succeeded
            FROM wrestler_move_experience
            WHERE wrestler_id = ?
            ORDER BY experience DESC
        """, (wrestler_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        # Process the results
        for move_name, exp, times_used, times_succeeded in results:
            move_exp_dict[move_name] = {
                "experience": exp,
                "times_used": times_used,
                "times_succeeded": times_succeeded,
                "success_rate": (times_succeeded / times_used * 100) if times_used > 0 else 0
            }
        
        # Get move type statistics using a separate connection
        move_types = {"grapple": 0, "strike": 0, "slam": 0, "aerial": 0, "submission": 0, "other": 0}
        success_by_type = {"grapple": 0, "strike": 0, "slam": 0, "aerial": 0, "submission": 0, "other": 0}
        
        # Create a new separate connection for manoeuvres database
        try:
            manoeuvres_conn = sqlite3.connect(db_path("manoeuvres.db"))
            manoeuvres_cursor = manoeuvres_conn.cursor()
            
            # Get move types for each move
            for move_name, stats in move_exp_dict.items():
                if move_name.startswith('__'):
                    continue
                    
                # Query the move type
                manoeuvres_cursor.execute("""
                    SELECT type FROM manoeuvres WHERE name = ?
                """, (move_name,))
                
                result = manoeuvres_cursor.fetchone()
                move_type = result[0] if result else "other"
                
                # Update statistics
                if move_type in move_types:
                    move_types[move_type] += stats["times_used"]
                    success_by_type[move_type] += stats["times_succeeded"]
                else:
                    move_types["other"] += stats["times_used"]
                    success_by_type["other"] += stats["times_succeeded"]
            
            manoeuvres_conn.close()
        except Exception as e:
            print(f"Error getting move types: {e}")
        
        # Add move type statistics to the dictionary
        move_exp_dict["__move_types"] = move_types
        move_exp_dict["__success_by_type"] = success_by_type


class DebugSimulationTab(QWidget):
    def __init__(self, parent=None, diplomacy_system=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.thread = None
        self.worker = None
        self.diplomacy_system = diplomacy_system
        
        self.init_ui()
    
    def init_ui(self):
        # Wrestler selection
        selection_layout = QHBoxLayout()
        
        # Wrestler 1 selection
        w1_group = QGroupBox("Wrestler 1")
        w1_layout = QFormLayout()
        self.w1_combo = QComboBox()
        self.load_wrestlers(self.w1_combo)
        w1_layout.addRow("Select:", self.w1_combo)
        w1_group.setLayout(w1_layout)
        selection_layout.addWidget(w1_group)
        
        # Wrestler 2 selection
        w2_group = QGroupBox("Wrestler 2")
        w2_layout = QFormLayout()
        self.w2_combo = QComboBox()
        self.load_wrestlers(self.w2_combo)
        w2_layout.addRow("Select:", self.w2_combo)
        w2_group.setLayout(w2_layout)
        selection_layout.addWidget(w2_group)
        
        # Match count selection
        match_group = QGroupBox("Simulation Settings")
        match_layout = QFormLayout()
        self.match_count = QSpinBox()
        self.match_count.setMinimum(1)
        self.match_count.setMaximum(100)
        self.match_count.setValue(10)
        match_layout.addRow("Number of Matches:", self.match_count)
        
        # Add diplomacy checkbox
        self.update_diplomacy = QCheckBox("Update Relationships")
        self.update_diplomacy.setChecked(True)
        match_layout.addRow("", self.update_diplomacy)
        
        match_group.setLayout(match_layout)
        selection_layout.addWidget(match_group)
        
        self.layout.addLayout(selection_layout)
        
        # Run button
        self.run_button = QPushButton("Run Simulation")
        apply_styles(self.run_button, "button_blue")
        self.run_button.clicked.connect(self.run_simulation)
        self.layout.addWidget(self.run_button)
        
        # Progress indicator
        self.progress_label = QLabel("Ready to simulate")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.progress_label)
        
        # Results area
        self.results_tabs = QTabWidget()
        self.summary_tab = QWidget()
        self.moves_tab = QWidget()
        self.results_tabs.addTab(self.summary_tab, "Summary")
        self.results_tabs.addTab(self.moves_tab, "Move Experience")
        
        # Setup summary tab
        summary_layout = QVBoxLayout(self.summary_tab)
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        summary_layout.addWidget(self.summary_text)
        
        # Setup move experience tab
        moves_layout = QHBoxLayout(self.moves_tab)
        
        # Wrestler 1 move experience
        w1_move_group = QGroupBox("Wrestler 1 Top Moves")
        w1_move_layout = QVBoxLayout()
        self.w1_move_table = QTableWidget(5, 4)  # 5 rows for top 5 moves, 4 columns
        self.w1_move_table.setHorizontalHeaderLabels(["Move", "Experience", "Times Used", "Success Rate"])
        self.w1_move_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        w1_move_layout.addWidget(self.w1_move_table)
        w1_move_group.setLayout(w1_move_layout)
        moves_layout.addWidget(w1_move_group)
        
        # Wrestler 2 move experience
        w2_move_group = QGroupBox("Wrestler 2 Top Moves")
        w2_move_layout = QVBoxLayout()
        self.w2_move_table = QTableWidget(5, 4)  # 5 rows for top 5 moves, 4 columns
        self.w2_move_table.setHorizontalHeaderLabels(["Move", "Experience", "Times Used", "Success Rate"])
        self.w2_move_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        w2_move_layout.addWidget(self.w2_move_table)
        w2_move_group.setLayout(w2_move_layout)
        moves_layout.addWidget(w2_move_group)
        
        self.layout.addWidget(self.results_tabs)
    
    def load_wrestlers(self, combo):
        """Load all wrestlers into the combo box"""
        conn = sqlite3.connect(db_path("wrestlers.db"))
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM wrestlers ORDER BY name")
        wrestlers = cursor.fetchall()
        conn.close()
        
        for wrestler_id, name in wrestlers:
            combo.addItem(name, wrestler_id)
    
    def run_simulation(self):
        """Run the simulation with the selected wrestlers and number of matches"""
        self.run_button.setEnabled(False)
        self.progress_label.setText("Simulating matches...")
        
        # Get selected wrestlers
        w1_id = self.w1_combo.currentData()
        w2_id = self.w2_combo.currentData()
        
        # Load full wrestler data
        w1 = load_wrestler_by_id(w1_id)
        w2 = load_wrestler_by_id(w2_id)
        
        if not w1 or not w2:
            self.progress_label.setText("Error loading wrestler data")
            self.run_button.setEnabled(True)
            return
        
        # Get number of matches
        num_matches = self.match_count.value()
        
        # Check if we should update diplomacy
        diplomacy_system = None
        if self.update_diplomacy.isChecked() and self.diplomacy_system:
            diplomacy_system = self.diplomacy_system
        
        # Setup worker thread
        self.thread = QThread()
        self.worker = SimulationWorker(w1, w2, num_matches, diplomacy_system)
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.process_results)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_progress)
        
        # Start the thread
        self.thread.start()
    
    def update_progress(self, current, total):
        """Update the progress indicator"""
        self.progress_label.setText(f"Simulating match {current} of {total}...")
    
    def process_results(self, results):
        """Process and display the simulation results"""
        self.run_button.setEnabled(True)
        self.progress_label.setText(f"Simulation complete - {len(results['matches'])} matches")
        
        # Extract the wrestlers' names
        w1_name = self.w1_combo.currentText()
        w2_name = self.w2_combo.currentText()
        
        # Process results to get stats
        w1_wins = results["w1_stats"]["wins"]
        w2_wins = results["w2_stats"]["wins"]
        total_matches = len(results["matches"])
        
        # Create summary text
        summary = f"<h2>Simulation Results: {w1_name} vs {w2_name}</h2>\n"
        summary += f"<p>Total Matches: {total_matches}</p>\n"
        summary += f"<p>{w1_name} Wins: {w1_wins} ({w1_wins/total_matches*100:.1f}%)</p>\n"
        summary += f"<p>{w2_name} Wins: {w2_wins} ({w2_wins/total_matches*100:.1f}%)</p>\n"
        
        # Display match quality stats
        total_quality = sum(m["quality"] for m in results["matches"])
        avg_quality = total_quality / total_matches
        summary += f"<p>Average Match Quality: {avg_quality:.1f}</p>\n"
        
        # Add hits and reversals
        summary += f"<p>{w1_name} Hits: {results['w1_stats'].get('hits', 0)} | Reversals: {results['w1_stats'].get('reversals', 0)}</p>\n"
        summary += f"<p>{w2_name} Hits: {results['w2_stats'].get('hits', 0)} | Reversals: {results['w2_stats'].get('reversals', 0)}</p>\n"
        
        # Display relationship change
        if "relationship_change" in results and self.diplomacy_system:
            relationship_change = results["relationship_change"]
            
            # Get the wrestler IDs
            w1_id = self.w1_combo.currentData()
            w2_id = self.w2_combo.currentData()
            
            # Get current relationship using IDs
            current_relationship = self.diplomacy_system.get_relationship(w1_id, w2_id)
            
            # Calculate the initial relationship (current minus the changes)
            initial_relationship = current_relationship - relationship_change
            
            # Add relationship section
            summary += f"<h3>Relationship Changes</h3>\n"
            summary += f"<p>Initial Relationship: {initial_relationship:.1f}</p>\n"
            summary += f"<p>Final Relationship: {current_relationship:.1f}</p>\n"
            
            # Add relationship change with color based on positive/negative
            if relationship_change > 0:
                summary += f"<p style='color: green;'>Overall Change: +{relationship_change:.1f}</p>\n"
            elif relationship_change < 0:
                summary += f"<p style='color: red;'>Overall Change: {relationship_change:.1f}</p>\n"
            else:
                summary += f"<p>Overall Change: 0.0 (unchanged)</p>\n"
            
            # Add interpretation
            if current_relationship > 75:
                summary += "<p><b>Interpretation:</b> Strong allies/friends</p>\n"
            elif current_relationship > 50:
                summary += "<p><b>Interpretation:</b> Friendly relationship</p>\n"
            elif current_relationship > 25:
                summary += "<p><b>Interpretation:</b> Cordial relationship</p>\n"
            elif current_relationship > 0:
                summary += "<p><b>Interpretation:</b> Neutral/professional relationship</p>\n"
            elif current_relationship > -25:
                summary += "<p><b>Interpretation:</b> Mild dislike</p>\n"
            elif current_relationship > -50:
                summary += "<p><b>Interpretation:</b> Strong dislike</p>\n"
            else:
                summary += "<p><b>Interpretation:</b> Bitter rivals/enemies</p>\n"
        
        # Display move type stats if available
        if "w1_move_exp" in results and "w2_move_exp" in results:
            # Add tables for move type statistics
            summary += "<h3>Move Type Analysis</h3>\n"
            
            # Create a HTML table for move type statistics
            summary += "<table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%;'>\n"
            summary += "<tr><th>Move Type</th><th>"+w1_name+" Usage</th><th>"+w1_name+" Success</th><th>"+w2_name+" Usage</th><th>"+w2_name+" Success</th></tr>\n"
            
            # Get move type statistics
            w1_move_types = results["w1_move_exp"].get("__move_types", {})
            w1_success = results["w1_move_exp"].get("__success_by_type", {})
            w2_move_types = results["w2_move_exp"].get("__move_types", {})
            w2_success = results["w2_move_exp"].get("__success_by_type", {})
            
            # Add a row for each move type
            for move_type in ["grapple", "strike", "slam", "aerial", "submission", "other"]:
                w1_usage = w1_move_types.get(move_type, 0)
                w1_success_count = w1_success.get(move_type, 0)
                w1_success_rate = (w1_success_count / w1_usage * 100) if w1_usage > 0 else 0
                
                w2_usage = w2_move_types.get(move_type, 0)
                w2_success_count = w2_success.get(move_type, 0)
                w2_success_rate = (w2_success_count / w2_usage * 100) if w2_usage > 0 else 0
                
                summary += f"<tr><td>{move_type.capitalize()}</td>"
                summary += f"<td>{w1_usage}</td><td>{w1_success_rate:.1f}%</td>"
                summary += f"<td>{w2_usage}</td><td>{w2_success_rate:.1f}%</td></tr>\n"
            
            summary += "</table>\n"
            
            # Display top moves for each wrestler
            summary += f"<h3>{w1_name}'s Top Moves</h3>\n"
            self._display_move_stats(results["w1_move_exp"], self.w1_move_table)
            
            summary += f"<h3>{w2_name}'s Top Moves</h3>\n"
            self._display_move_stats(results["w2_move_exp"], self.w2_move_table)
        
        # Update the summary text
        self.summary_text.setHtml(summary)
    
    def _display_move_stats(self, move_exp, table):
        """Display the top 5 moves by experience in the table"""
        # Filter out special keys starting with __
        filtered_moves = {k: v for k, v in move_exp.items() if not k.startswith('__')}
        
        # Sort moves by experience
        sorted_moves = sorted(
            filtered_moves.items(), 
            key=lambda x: x[1]["experience"], 
            reverse=True
        )[:5]  # Get top 5
        
        # Clear the table
        table.clearContents()
        
        # Fill the table with the top 5 moves
        for i, (move_name, stats) in enumerate(sorted_moves):
            if i >= 5:  # Only show top 5
                break
                
            table.setItem(i, 0, QTableWidgetItem(move_name))
            table.setItem(i, 1, QTableWidgetItem(str(stats["experience"])))
            table.setItem(i, 2, QTableWidgetItem(str(stats["times_used"])))
            table.setItem(i, 3, QTableWidgetItem(f"{stats['success_rate']:.1f}%"))


class DebugUI(QTabWidget):
    def __init__(self, parent=None, diplomacy_system=None):
        super().__init__(parent)
        
        # Add various debug tabs
        self.simulation_tab = DebugSimulationTab(diplomacy_system=diplomacy_system)
        self.addTab(self.simulation_tab, "Match Simulation")
        
        # Add more tabs as needed (e.g., for other debug features)
        
        # Set up sizing
        self.setMinimumSize(800, 600) 