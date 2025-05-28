from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QHBoxLayout, QProgressBar,
    QSlider, QFrame, QGroupBox, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor
from match_engine import get_all_wrestlers, load_wrestler_by_id
from ui.theme import apply_styles
from promo.versus_promo_engine import VersusPromoEngine
import statistics

class VersusPromoUI(QWidget):
    """UI for testing the versus promo system with two wrestlers."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Versus Promo Test")
        self.wrestlers = get_all_wrestlers()
        self.current_promo = None
        self.initUI()
        self.setStyleSheet("""
            background-color: #42494a;
            color: #e0e0e0;
            font-family: Fira Code;
        """)
        
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Wrestler selection area
        selection_area = QHBoxLayout()
        
        # Wrestler 1 selection
        w1_group = QGroupBox("Wrestler 1")
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
        
        # Wrestler 2 selection
        w2_group = QGroupBox("Wrestler 2")
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
        self.load_wrestlers(self.w2_combo)
        # Default to a different wrestler
        if self.w2_combo.count() > 1:
            self.w2_combo.setCurrentIndex(1)
        w2_layout.addWidget(self.w2_combo)
        w2_group.setLayout(w2_layout)
        selection_area.addWidget(w2_group)
        
        layout.addLayout(selection_area)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Promo")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4682b4;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5b9bd5;
            }
        """)
        self.start_button.clicked.connect(self.start_promo)
        button_layout.addWidget(self.start_button)
        
        layout.addLayout(button_layout)
        
        # Results area
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-size: 14pt;
                font-family: Fira Code;
                border: 1px solid #444;
                padding: 10px;
            }
        """)
        layout.addWidget(self.results_display)
        
        # Stats display
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-size: 12pt;
                font-family: Fira Code;
                border: 1px solid #444;
                padding: 10px;
            }
        """)
        layout.addWidget(self.stats_display)
        
    def load_wrestlers(self, combo):
        """Load wrestler data into the given combobox."""
        combo.clear()
        for wrestler_id, wrestler_name in self.wrestlers:
            combo.addItem(wrestler_name, wrestler_id)
            
    def start_promo(self):
        """Run the versus promo simulation."""
        # Get selected wrestlers
        w1_id = self.w1_combo.currentData()
        w2_id = self.w2_combo.currentData()
        
        # Load wrestler data
        w1 = load_wrestler_by_id(w1_id)
        w2 = load_wrestler_by_id(w2_id)
        
        if not w1 or not w2:
            self.results_display.setText("Error: Could not load wrestler data")
            return
            
        # Run the versus promo
        engine = VersusPromoEngine(w1, w2)
        result = engine.simulate()
        
        # Display the results
        self.display_results(result, w1, w2)
        
    def display_results(self, result, w1, w2):
        """Display the results of the versus promo."""
        # Clear previous results
        self.results_display.clear()
        self.stats_display.clear()
        
        # Display promo text
        html = "<h2>Versus Promo Results</h2>"
        html += f"<h3>{w1['name']} vs {w2['name']}</h3>"
        
        # Display each beat
        for i, beat in enumerate(result["beats"]):
            if "wrestler" in beat and "promo_line" in beat and beat["wrestler"] is not None:
                wrestler = beat["wrestler"]
                name = wrestler["name"]
                
                # Add colors based on which wrestler is speaking
                color = "#66CCFF" if wrestler == w1 else "#FF9966"
                
                # Get score information if available
                score_text = ""
                if "score" in beat and beat["score"] is not None:
                    score = beat["score"]
                    score_text = f" (Score: {score:.1f})"
                
                html += f'<p style="color:{color}"><b>{name}:</b> {beat["promo_line"]}{score_text}</p>'
            elif "promo_line" in beat:
                # Handle the case where there's a promo line but no wrestler (like a summary line)
                html += f'<p style="color:#FFFFFF"><i>{beat["promo_line"]}</i></p>'
        
        self.results_display.setHtml(html)
        
        # Display statistics
        stats_html = "<h2>Promo Statistics</h2>"
        
        # Final scores
        scores = result["final_scores"]
        stats_html += "<h3>Final Scores</h3>"
        stats_html += f"<p><b>{w1['name']}:</b> {scores['wrestler1_score']:.1f}</p>"
        stats_html += f"<p><b>{w2['name']}:</b> {scores['wrestler2_score']:.1f}</p>"
        stats_html += f"<p><b>Overall Score:</b> {scores['overall_score']:.1f}</p>"
        stats_html += f"<p><b>Competition Bonus:</b> {scores['competition_bonus']}</p>"
        stats_html += f"<p><b>Quality Bonus:</b> {scores['quality_bonus']}</p>"
        
        # Calculate per-wrestler statistics
        w1_beats = [b for b in result["beats"] if b.get("wrestler") == w1]
        w2_beats = [b for b in result["beats"] if b.get("wrestler") == w2]
        
        w1_scores = [b.get("score", 0) for b in w1_beats if b.get("score") is not None]
        w1_momentum = [b.get("momentum", 0) for b in w1_beats if b.get("momentum") is not None]
        
        w2_scores = [b.get("score", 0) for b in w2_beats if b.get("score") is not None]
        w2_momentum = [b.get("momentum", 0) for b in w2_beats if b.get("momentum") is not None]
        
        # Add wrestler statistics
        stats_html += f"<h3>{w1['name']} Statistics</h3>"
        if w1_scores:
            stats_html += f"<p>Average Beat Score: {statistics.mean(w1_scores):.1f}</p>"
        if w1_momentum:
            stats_html += f"<p>Average Momentum: {statistics.mean(w1_momentum):.1f}</p>"
        stats_html += f"<p>Total Beats: {len(w1_beats)}</p>"
        
        stats_html += f"<h3>{w2['name']} Statistics</h3>"
        if w2_scores:
            stats_html += f"<p>Average Beat Score: {statistics.mean(w2_scores):.1f}</p>"
        if w2_momentum:
            stats_html += f"<p>Average Momentum: {statistics.mean(w2_momentum):.1f}</p>"
        stats_html += f"<p>Total Beats: {len(w2_beats)}</p>"
        
        # Add winner declaration
        if scores['wrestler1_score'] > scores['wrestler2_score']:
            stats_html += f"<h3>Winner: {w1['name']}</h3>"
        elif scores['wrestler2_score'] > scores['wrestler1_score']:
            stats_html += f"<h3>Winner: {w2['name']}</h3>"
        else:
            stats_html += "<h3>Result: Draw</h3>"
        
        self.stats_display.setHtml(stats_html)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    ui = VersusPromoUI()
    ui.show()
    sys.exit(app.exec_()) 