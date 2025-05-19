from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLineEdit
from PyQt5.QtCore import Qt
from ui.theme import apply_styles

class BigEventSettingsUI(QWidget):
    def __init__(self, on_back=None):
        super().__init__()
        self.on_back = on_back

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(20)

        title = QLabel("🎪 Manage Big Events")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20pt; font-weight: bold;")
        layout.addWidget(title)

        self.cadence_dropdown = QComboBox()
        self.cadence_dropdown.addItems(["Monthly", "Every 6 Weeks", "Every 2 Months", "Quarterly"])

        self.viewer_field = QLineEdit("1200000")
        self.match_quality_field = QLineEdit("78")
        self.segment_quality_field = QLineEdit("75")

        layout.addWidget(QLabel("Cadence:"))
        layout.addWidget(self.cadence_dropdown)

        layout.addWidget(QLabel("Average Viewers/Buyrate (last 5):"))
        layout.addWidget(self.viewer_field)

        layout.addWidget(QLabel("Avg Match Quality (last 5):"))
        layout.addWidget(self.match_quality_field)

        layout.addWidget(QLabel("Avg Segment Quality (last 5):"))
        layout.addWidget(self.segment_quality_field)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        back_btn = QPushButton("Back")
        apply_styles(save_btn, "button_blue")
        apply_styles(back_btn, "button_flat")
        save_btn.clicked.connect(self.save)
        back_btn.clicked.connect(self.on_back)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(back_btn)

        layout.addLayout(btn_row)

    def save(self):
        print("✅ Big event settings saved (stub)")
