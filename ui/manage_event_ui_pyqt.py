from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QPushButton, QListWidgetItem, QComboBox, QFrame, QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
import random
import json
from match_engine import get_all_wrestlers
from ui.theme import apply_styles

class ManageEventUI(QWidget):
    def __init__(self, event_data=None, fixed_date=None, on_back=None):
        super().__init__()
        self.event_data = event_data
        self.fixed_date = fixed_date
        self.on_back = on_back
        self.booked_wrestlers = set()

        self.card_slots = []

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        self.init_event_header(layout)
        self.init_main_layout(layout)
        self.init_footer(layout)

        if self.event_data:
            self.load_existing_event()

    def init_event_header(self, parent_layout):
        header = QHBoxLayout()

        self.event_name_input = QLineEdit()
        self.event_name_input.setPlaceholderText("Event Name")
        apply_styles(self.event_name_input, "input_text")

        header.addWidget(QLabel("Event Name:"))
        header.addWidget(self.event_name_input)
        header.addStretch()

        parent_layout.addLayout(header)

        # Buttons
        btn_row = QHBoxLayout()

        auto_btn = QPushButton("Auto-Generate Card")
        auto_btn.clicked.connect(self.auto_generate_card)
        apply_styles(auto_btn, "button_blue")
        btn_row.addWidget(auto_btn)

        add_match_btn = QPushButton("Add Match")
        add_match_btn.clicked.connect(lambda: self.add_slot("Match"))
        btn_row.addWidget(add_match_btn)

        add_promo_btn = QPushButton("Add Promo")
        add_promo_btn.clicked.connect(lambda: self.add_slot("Promo"))
        btn_row.addWidget(add_promo_btn)

        parent_layout.addLayout(btn_row)

    def init_main_layout(self, parent_layout):
        main = QHBoxLayout()

        # Wrestler list (left)
        self.wrestler_list = DraggableListWidget()
        apply_styles(self.wrestler_list, "list_wrestlers")
        self.name_to_id = {}
        for id_, name in get_all_wrestlers():
            self.name_to_id[name] = id_
            item = QListWidgetItem()
            # Explicitly set the text for display
            item.setText(str(name))
            item.setData(Qt.UserRole, name)
            self.wrestler_list.addItem(item)
        self.wrestler_list.itemDoubleClicked.connect(self.handle_wrestler_double_click)
        main.addWidget(self.wrestler_list, 2)

        # Match list container (right, scrollable)
        right_panel = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.card_container = QWidget()
        self.card_layout = QVBoxLayout(self.card_container)
        self.card_layout.setSpacing(10)
        scroll_area.setWidget(self.card_container)

        right_panel.addWidget(scroll_area)
        main.addLayout(right_panel, 4)

        parent_layout.addLayout(main)

    def init_footer(self, parent_layout):
        self.warning_label = QLabel("")
        apply_styles(self.warning_label, "warning")
        parent_layout.addWidget(self.warning_label)

        save_btn = QPushButton("Save Event")
        apply_styles(save_btn, "button_blue")
        save_btn.clicked.connect(self.save_event)
        parent_layout.addWidget(save_btn)

        back_btn = QPushButton("Back")
        apply_styles(back_btn, "button_nav")
        if self.on_back:
            back_btn.clicked.connect(self.on_back)
        parent_layout.addWidget(back_btn)

    def add_slot(self, slot_type):
        frame = CardSlot(slot_type, on_remove=self.remove_slot, on_remove_wrestler=self.remove_wrestler_from_slot)
        self.card_layout.addWidget(frame)
        self.card_slots.append(frame)

    def remove_slot(self, frame):
        self.card_layout.removeWidget(frame)
        frame.deleteLater()
        self.card_slots.remove(frame)

    def auto_generate_card(self):
        for i in reversed(range(self.card_layout.count())):
            widget = self.card_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.card_slots = []

        types = ["Match"] * 5 + ["Promo"] * 2 + ["Backstage"] * 2
        random.shuffle(types)

        for t in types:
            self.add_slot(t)

    def handle_wrestler_double_click(self, item):
        name = item.data(Qt.UserRole)
        self.assign_wrestler_to_slot(name)

    def assign_wrestler_to_slot(self, name):
        for frame in self.card_slots:
            if frame.can_accept_more():
                frame.add_wrestler(name)
                return
        QMessageBox.warning(self, "Warning", "No available slots to assign wrestler.")

    def remove_wrestler_from_slot(self, frame, name):
        frame.remove_wrestler(name)

    def save_event(self):
        from ui.event_manager_helper import add_event, update_event
        from game_state import get_game_date

        name = self.event_name_input.text().strip()
        if not name:
            self.warning_label.setText("Event name is required.")
            return

        card = []
        for frame in self.card_slots:
            if frame.slot_type == "Match" and len(frame.participants) == 2:
                card.append((frame.participants[0], frame.participants[1]))
            elif frame.slot_type == "Promo" and len(frame.participants) == 1:
                card.append((frame.participants[0], frame.slot_type))

        if self.event_data and self.event_data.get("id"):
            update_event(self.event_data["id"], name=name, card=card)
        else:
            date = self.fixed_date or get_game_date()
            add_event(name, card, "TBD", "TBD", date, results=json.dumps([]))

        self.warning_label.setText("Event saved successfully.")

    def load_existing_event(self):
        self.event_name_input.setText(self.event_data.get("name", ""))
        card = self.event_data.get("card", [])

        for entry in card:
            if isinstance(entry, tuple) and len(entry) == 2:
                if entry[1] == "Promo":
                    frame = CardSlot(entry[1], on_remove=self.remove_slot, on_remove_wrestler=self.remove_wrestler_from_slot)
                    frame.add_wrestler(entry[0])
                else:
                    frame = CardSlot("Match", on_remove=self.remove_slot, on_remove_wrestler=self.remove_wrestler_from_slot)
                    frame.add_wrestler(entry[0])
                    frame.add_wrestler(entry[1])

                self.card_layout.addWidget(frame)
                self.card_slots.append(frame)

class CardSlot(QFrame):
    def __init__(self, slot_type, on_remove, on_remove_wrestler):
        super().__init__()
        self.slot_type = slot_type
        self.on_remove = on_remove
        self.on_remove_wrestler = on_remove_wrestler
        self.participants = []

        self.setFrameShape(QFrame.Box)
        self.setStyleSheet("border: 1px solid #555; background-color: #2c2c2c; padding: 8px;")

        layout = QVBoxLayout(self)
        header = QHBoxLayout()

        type_label = QLabel(f"{slot_type}")
        type_label.setStyleSheet("font-weight: bold; color: #eee;")
        header.addWidget(type_label)

        remove_btn = QPushButton("❌")
        remove_btn.setFixedSize(24, 24)
        remove_btn.clicked.connect(lambda: self.on_remove(self))
        header.addWidget(remove_btn)

        layout.addLayout(header)

        self.participant_layout = QHBoxLayout()
        layout.addLayout(self.participant_layout)

    def add_wrestler(self, name):
        if self.slot_type == "Match" and len(self.participants) >= 2:
            return
        if self.slot_type in ["Promo", "Backstage"] and len(self.participants) >= 1:
            return

        self.participants.append(name)
        label = QLabel(name)
        label.setStyleSheet("font-size: 12pt; color: #ccc;")
        remove_btn = QPushButton("❌")
        remove_btn.setFixedSize(20, 20)
        remove_btn.clicked.connect(lambda: self.on_remove_wrestler(self, name))

        wrapper = QHBoxLayout()
        wrapper.addWidget(label)
        wrapper.addWidget(remove_btn)

        wrapper_frame = QWidget()
        wrapper_frame.setLayout(wrapper)

        self.participant_layout.addWidget(wrapper_frame)

    def remove_wrestler(self, name):
        self.participants.remove(name)
        for i in reversed(range(self.participant_layout.count())):
            item = self.participant_layout.itemAt(i).widget()
            if item:
                label = item.layout().itemAt(0).widget()
                if label.text() == name:
                    item.deleteLater()
                    break

    def can_accept_more(self):
        if self.slot_type == "Match" and len(self.participants) < 2:
            return True
        if self.slot_type in ["Promo", "Backstage"] and len(self.participants) < 1:
            return True
        return False

class DraggableListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(item.data(Qt.UserRole))
        drag.setMimeData(mime)
        drag.exec_(supportedActions)
