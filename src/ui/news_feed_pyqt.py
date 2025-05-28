from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton
)
from PyQt5.QtCore import Qt
from src.core.game_state import get_game_date


class NewsFeedUI(QWidget):
    def __init__(self, on_event_play=None):
        super().__init__()

        self.on_event_play = on_event_play

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.date_label = QLabel(f"📰 News Feed - {get_game_date()}")
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(self.date_label)

        self.news_box = QTextEdit()
        self.news_box.setReadOnly(True)
        self.news_box.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")
        layout.addWidget(self.news_box)

        # Add intro message
        self.news_box.append("🔥 Welcome to Overbooked Wrestling!\n\nCheck back here after shows for recaps, surprises, and scandalous headlines...")

        self.pending_button = None

    def refresh_date(self):
        self.date_label.setText(f"📰 News Feed - {get_game_date()}")

    def add_item(self, text, action_label=None, action=None):
        self.news_box.setReadOnly(False)
        self.news_box.append(f"\n{text}")
        self.news_box.setReadOnly(True)

        # Optionally add a button for the action
        if action_label and action:
            btn = QPushButton(action_label)
            btn.clicked.connect(action)
            self.layout().addWidget(btn)
            self.pending_button = btn
