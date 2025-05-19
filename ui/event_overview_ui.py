from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QFrame
from PyQt5.QtCore import Qt, QTimer
from ui.theme import apply_styles
from ui.event_manager_helper import get_all_events, get_main_event, get_main_event_result
from ui.weekly_show_settings_ui import WeeklyShowSettingsUI



class EventOverviewUI(QWidget):
    def __init__(self, on_back=None, load_event=None):
        super().__init__()
        self.on_back = on_back
        self.load_event = load_event

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Header
        header = QLabel("📅 Event Overview")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 24pt; font-weight: bold; color: #eeeeee;")
        layout.addWidget(header)

        top_row = QHBoxLayout()
        top_row.addWidget(self.build_upcoming_events(), 0)
        top_row.addSpacing(20)
        top_row.addWidget(self.build_previous_events(), 0)
        layout.addLayout(top_row)

        mid_row = QHBoxLayout()
        mid_row.setSpacing(20)
        mid_row.addWidget(self.build_tv_summary())
        mid_row.addWidget(self.build_big_event_summary())
        mid_row.addWidget(self.build_house_show_summary())
        layout.addLayout(mid_row)

        if self.on_back:
            back_button = QPushButton("Back")
            apply_styles(back_button, "button_flat")
            back_button.clicked.connect(self.on_back)
            layout.addWidget(back_button, alignment=Qt.AlignRight)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


    def build_upcoming_events(self):
        frame = QFrame()
        frame.setFixedSize(320, 180)
        frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout = QVBoxLayout(frame)
        label = QLabel("Upcoming Events")
        label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #fff;")
        layout.addWidget(label)

        list_widget = QListWidget()
        today = self.get_today()
        upcoming = [ev for ev in get_all_events() if ev[5] > today]
        upcoming = sorted(upcoming, key=lambda e: e[5])[:5]

        for ev in upcoming:
            event_id, name, _, _, _, date = ev[:6]
            main_event = get_main_event(event_id)
            item_text = f"{date}: {name} ({main_event})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, event_id)
            list_widget.addItem(item)

        list_widget.itemClicked.connect(lambda item: self.load_event(item.data(Qt.UserRole)))
        layout.addWidget(list_widget)
        return frame

    def build_previous_events(self):
        frame = QFrame()
        frame.setFixedSize(320, 180)
        frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout = QVBoxLayout(frame)
        label = QLabel("Previous Events")
        label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #fff;")
        layout.addWidget(label)

        list_widget = QListWidget()
        list_widget.setFixedSize(320, 150)
        list_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        today = self.get_today()
        past = [ev for ev in get_all_events() if ev[5] < today]
        past = sorted(past, key=lambda e: e[5], reverse=True)[:5]

        for ev in past:
            event_id, name, _, _, _, date = ev[:6]
            main_result = get_main_event_result(event_id)
            item_text = f"{date}: {name} ({main_result})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, event_id)
            list_widget.addItem(item)

        list_widget.itemClicked.connect(lambda item: self.load_event(item.data(Qt.UserRole)))
        layout.addWidget(list_widget)
        return frame


    def get_today(self):
        from game_state import get_game_date
        from datetime import datetime
        return datetime.strptime(get_game_date(), "%A, %d %B %Y").strftime("%Y-%m-%d")

    def load_weekly_settings(self):
        from ui.weekly_show_settings_ui import WeeklyShowSettingsUI
        parent = self.window()
        screen = WeeklyShowSettingsUI(on_back=self.__reload_self)
        parent.clear_right_panel()
        parent.right_panel.addWidget(screen)
        parent.right_panel.setCurrentWidget(screen)

    def load_big_event_settings(self):
        from ui.big_event_settings_ui import BigEventSettingsUI
        parent = self.window()
        screen = BigEventSettingsUI(on_back=self.__reload_self)
        parent.clear_right_panel()
        parent.right_panel.addWidget(screen)
        parent.right_panel.setCurrentWidget(screen)

    def __reload_self(self):
        parent = self.window()
        if not parent:
            return

        def reload():
            screen = EventOverviewUI(on_back=self.on_back, load_event=self.load_event)
            parent.clear_right_panel()
            parent.right_panel.addWidget(screen)
            parent.right_panel.setCurrentWidget(screen)

        QTimer.singleShot(0, reload)

    def fixed_box(self, label_text, content_widget, button_text, button_callback):
        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy

        frame = QFrame()
        frame.setFixedSize(250, 220)  # same size for all
        frame.setStyleSheet("background-color: #1e1e1e; border: 1px solid #444; border-radius: 6px;")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel(f"{label_text}")
        title.setStyleSheet("font-weight: bold; font-size: 16pt; color: #fff;")
        layout.addWidget(title)

        content_widget.setFixedHeight(100)
        content_widget.setWordWrap(True)
        content_widget.setStyleSheet("font-family: Fira Code; font-size: 14pt; color: #ccc;")
        layout.addWidget(content_widget)

        btn = QPushButton(button_text)
        btn.setFixedHeight(32)
        btn.setFixedWidth(230)
        btn.clicked.connect(button_callback)
        apply_styles(btn, "button_blue")  # or button_yellow, button_flat depending on use
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        return frame

    def build_tv_summary(self):
        summary = QLabel("Name: Weekly Slam\nDay: Wednesday\nAvg Viewers: 870k\nAvg Match: 71\nAvg Segment: 68")
        return self.fixed_box("TV Show", summary, "Manage Weekly", self.load_weekly_settings)

    def build_big_event_summary(self):
        summary = QLabel("Cadence: Monthly PPV\nAvg Viewers: 1200k\nAvg Match: 78\nAvg Segment: 75")
        return self.fixed_box("Big Events", summary, "Manage Big Events", self.load_big_event_settings)

    def build_house_show_summary(self):
        summary = QLabel("Used to develop talent.\nNo booking, low risk.\nAffects condition over time.")
        return self.fixed_box("House Shows", summary, "Manage House Shows", self.load_house_show_settings)

    def load_house_show_settings(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Coming Soon", "House Show Management is coming soon.")
