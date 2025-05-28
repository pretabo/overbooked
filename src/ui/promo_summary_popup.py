from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton
)
from PyQt5.QtCore import Qt

class PromoSummaryPopup(QDialog):
    def __init__(self, final_rating, outcome_effects, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Promo Summary")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                font-family: Fira Code;
                color: #eeeeee;
            }
            QPushButton {
                font-family: Fira Code;
                padding: 6px 12px;
                background-color: #333;
                color: #eee;
                border: 1px solid #555;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        rating_label = QLabel(f"🎤 Final Promo Rating: {final_rating}")
        rating_label.setAlignment(Qt.AlignCenter)
        rating_label.setStyleSheet("font-size: 18pt;")
        layout.addWidget(rating_label)

        layout.addWidget(QLabel("🌟 Outcome Effects:"))
        for effect in outcome_effects:
            effect_label = QLabel(f"• {effect}")
            effect_label.setWordWrap(True)
            layout.addWidget(effect_label)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
