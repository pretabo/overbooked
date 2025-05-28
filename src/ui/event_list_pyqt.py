from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from src.core.game_state import get_game_date
from src.ui.event_manager_helper import get_all_events, get_event_by_id, delete_event
from src.ui.manage_event_ui_pyqt import ManageEventUI
from src.ui.event_summary_pyqt import EventSummaryUI
from src.ui.theme import apply_styles


class EventsUI(QWidget):
    def __init__(self, on_back=None, load_screen=None):
        super().__init__()
        self.on_back = on_back
        self.load_screen = load_screen  # expects MainApp-like .right_panel loader

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel(f"Events - {get_game_date()}")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.build_buttons(layout)
        self.refresh_event_list()

    def build_buttons(self, layout):
        row = QHBoxLayout()

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.on_add_event)
        row.addWidget(add_btn)

        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.on_edit_event)
        row.addWidget(edit_btn)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.on_remove_event)
        row.addWidget(remove_btn)

        play_btn = QPushButton("Play")
        play_btn.clicked.connect(self.on_play_event)
        row.addWidget(play_btn)

        clear_btn = QPushButton("Clear All Events")
        clear_btn.clicked.connect(self.on_clear_all_events)
        row.addWidget(clear_btn)

        layout.addLayout(row)

    def refresh_event_list(self):
        self.list_widget.clear()
        for ev in get_all_events():
            event_id, name, *_ = ev
            self.list_widget.addItem(f"{event_id:>3} | {name}")

    def set_status(self, msg, delay=4000):
        self.status_label.setText(msg)
        if delay:
            def safe_clear():
                if self.status_label:
                    try:
                        self.status_label.setText("")
                    except RuntimeError:
                        pass  # QLabel deleted

            QTimer.singleShot(delay, safe_clear)

    def get_selected_event_id(self):
        row = self.list_widget.currentRow()
        if row < 0:
            return None
        item = self.list_widget.item(row)
        return int(item.text().split("|")[0].strip())

    def on_add_event(self):
        if self.load_screen:
            self.load_screen(ManageEventUI(fixed_date=None, on_back=self.reload_self))

    def on_edit_event(self):
        event_id = self.get_selected_event_id()
        if not event_id:
            self.set_status("Please select an event to edit.")
            return

        event_data = get_event_by_id(event_id)
        if not event_data:
            self.set_status("Could not load event.")
            return

        if self.load_screen:
            num_matches = len(event_data.get("card", []))
            num_results = len(event_data.get("results", []))
            if num_results == num_matches and num_matches > 0:
                self.load_screen(EventSummaryUI(event_data, on_back=self.reload_self))
            else:
                self.load_screen(ManageEventUI(event_data=event_data, on_back=self.reload_self))

    def on_remove_event(self):
        event_id = self.get_selected_event_id()
        if not event_id:
            self.set_status("Please select an event to remove.")
            return

        delete_event(event_id)
        self.refresh_event_list()
        self.set_status(f"Event {event_id} removed.")

    def on_play_event(self):
        event_id = self.get_selected_event_id()
        if not event_id:
            self.set_status("Please select an event to play.")
            return

        event_data = get_event_by_id(event_id)
        if not event_data:
            self.set_status("Could not load event.")
            return

        if self.load_screen:
            self.load_screen(EventSummaryUI(event_data, on_back=self.reload_self))

    def reload_self(self):
        if self.load_screen:
            self.load_screen(EventsUI(on_back=self.on_back, load_screen=self.load_screen))

    def on_clear_all_events(self):
        confirm = QMessageBox.question(
            self,
            "Confirm",
            "Are you sure you want to delete ALL events?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            for ev in get_all_events():
                delete_event(ev[0])
            self.refresh_event_list()
            self.set_status("All events cleared.")
