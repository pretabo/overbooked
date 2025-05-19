from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QApplication
)
from PyQt5.QtCore import Qt

from game_state import get_game_date, advance_game_date, is_event_locked, set_event_lock
from ui.roster_ui_pyqt import RosterUI  # Assuming you've ported this
from ui.calendar_view_ui_pyqt import CalendarViewUI  # Placeholder for future
from ui.promo_test_ui import PromoTestUI
from ui.theme import apply_styles
from PyQt5.QtGui import QIcon
from datetime import datetime
from diplomacy_system import DiplomacySystem


# Import other screens here as needed

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Overbooked: Wrestling Simulator")
        self.setGeometry(100, 100, 1280, 720)
        self.pending_news_item = None
        self.diplomacy_system = DiplomacySystem()

        self.diplomacy_system.load_from_db()
        print("[Diplomacy] Loaded relationships from database.")


        from game_state import load_game_state
        load_game_state()


        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.left_panel = QVBoxLayout()
        self.right_panel = QStackedWidget()


        # Left panel
        self.left_panel_widget = QWidget()
        self.left_panel_widget.setLayout(self.left_panel)
        self.left_panel_widget.setStyleSheet("background-color: #535a5d;") 
        self.left_panel_widget.setFixedWidth(240)  # or any width you prefer

        # Main layout
        main_layout = QHBoxLayout()
        self.central_widget.setLayout(main_layout)
        main_layout.addLayout(self.left_panel, 1)
        main_layout.addWidget(self.left_panel_widget)
        main_layout.addWidget(self.right_panel, 4)


        # Date container
        self.date_container = QWidget()
        self.date_container.setFixedHeight(100)

        date_layout = QVBoxLayout()
        date_layout.setContentsMargins(0, 20, 0, 0)  # top margin for spacing
        date_layout.setAlignment(Qt.AlignTop)

        today = datetime.strptime(get_game_date(), "%A, %d %B %Y")
        formatted = today.strftime("%A\n%d %B %Y")

        self.date_label = QLabel(formatted)
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setStyleSheet("""
            font-family: Fira Code;
            font-size: 16pt;
            color: #eee;
            padding: 10px;
        """)
        apply_styles(self.date_label, "label_header")
        self.date_label.setAlignment(Qt.AlignCenter)

        date_layout.addWidget(self.date_label)
        self.date_container.setLayout(date_layout)

        self.left_panel.addWidget(self.date_container)

        # Continue Button
        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.advance_game_day)
        self.left_panel.addWidget(self.continue_button)
        apply_styles(self.continue_button, "button_blue")


        # Nav buttons
        self.add_nav_button("News Feed", self.load_news_feed_ui)
        self.add_nav_button("Event Calendar", self.load_calendar_ui)
        self.add_nav_button("Event Overview", self.load_event_overview_ui)
        self.add_nav_button("View Roster", self.load_roster_ui)
        self.add_nav_button("Simulate Match", self.load_match_ui)
        self.add_nav_button("Test Promos", self.load_promo_test_ui)
        self.add_nav_button("Manage Storylines", self.load_storyline_management_ui)


        self.add_nav_button("[DEV] Diplomacy Manager", self.load_dev_diplomacy_ui)


        self.left_panel.addStretch()  # Pushes everything above upward


        save_btn = QPushButton("Save Game")
        apply_styles(save_btn, "button_red")  
        save_btn.clicked.connect(self.save_game_state_manually)
        self.left_panel.addWidget(save_btn)

        exit_btn = QPushButton("Exit Game")
        apply_styles(exit_btn, "button_red")  # Optional: red button style
        exit_btn.clicked.connect(QApplication.quit)

        self.left_panel.addWidget(exit_btn)


        self.pending_news_item = None

        self.load_news_feed_ui()

    def add_nav_button(self, label, callback):
        btn = QPushButton(label)
        from ui.theme import apply_styles
        apply_styles(btn, "button_nav")
        btn.clicked.connect(callback)
        self.left_panel.addWidget(btn)

    def clear_right_panel(self):
        while self.right_panel.count():
            widget = self.right_panel.widget(0)
            self.right_panel.removeWidget(widget)
            widget.deleteLater()

    def advance_game_day(self):
        from ui.event_manager_helper import get_all_events
        from datetime import datetime
        from game_state import get_game_date, is_event_locked, set_event_lock, advance_game_date

        if is_event_locked():
            print("🚫 Date locked — event must be played first.")
            return

        print("🧭 Advancing game date...")
        advance_game_date()
        self.diplomacy_system.save_to_db()
        print("[Diplomacy] Autosaved relationships after date advance.")

        new_date = datetime.strptime(get_game_date(), "%A, %d %B %Y")
        formatted = new_date.strftime("%A\n%d %B %Y")
        self.date_label.setText(formatted)

        todays_date = datetime.strptime(get_game_date(), "%A, %d %B %Y").strftime("%Y-%m-%d")
        print("📨 Checking for events on", todays_date)

        for ev in get_all_events():
            if ev[5] == todays_date:
                print("🔎 Event row:", ev)
                event_id, name = ev[0], ev[1]
                print("🎯 Event FOUND on", todays_date, ":", name)
                set_event_lock(True)

                self.show_news_item({
                    "type": "event",
                    "text": f"📢 An event is scheduled for today: {name}",
                    "action_label": "Play Event",
                    "event_id": event_id
                })
                break  # still allow news feed to load

        # ✅ Always go back to the News Feed
        self.load_news_feed_ui()

    def load_roster_ui(self):
        self.clear_right_panel()
        roster_ui = RosterUI(on_view_profile=self.load_wrestler_profile)
        self.right_panel.addWidget(roster_ui)
        self.right_panel.setCurrentWidget(roster_ui)

    def load_wrestler_profile(self, wrestler_id):
        from ui.wrestler_profile_pyqt import WrestlerProfileUI
        self.clear_right_panel()
        profile_ui = WrestlerProfileUI(wrestler_id, on_back=self.load_roster_ui, diplomacy_system=self.diplomacy_system)
        self.right_panel.addWidget(profile_ui)
        self.right_panel.setCurrentWidget(profile_ui)

    def load_news_feed_ui(self):
        from ui.news_feed_pyqt import NewsFeedUI
        self.clear_right_panel()
        feed = NewsFeedUI(on_event_play=self.play_event_from_news)
        self.right_panel.addWidget(feed)
        self.right_panel.setCurrentWidget(feed)

        if self.pending_news_item:
            feed.add_item(
                text=self.pending_news_item["text"],
                action_label=self.pending_news_item["action_label"],
                action=lambda: self.play_event_from_news(self.pending_news_item["event_id"])
            )

    def load_calendar_ui(self):
        from ui.calendar_view_ui_pyqt import CalendarViewUI
        self.clear_right_panel()
        calendar = CalendarViewUI(on_back=self.load_news_feed_ui, news_callback=self.show_news_item)
        self.right_panel.addWidget(calendar)
        self.right_panel.setCurrentWidget(calendar)

    def load_match_ui(self):
        from ui.match_ui_pyqt import WrestlingMatchUI
        from match_engine import load_wrestler_by_id
        from match_engine import get_all_wrestlers
        import random

        wrestlers = get_all_wrestlers()
        if len(wrestlers) < 2:
            print("❌ Not enough wrestlers in DB.")
            return

        # ✅ Randomly pick 2 different wrestlers
        w1_id, w2_id = random.sample([w[0] for w in wrestlers], 2)
        w1 = load_wrestler_by_id(w1_id)
        w2 = load_wrestler_by_id(w2_id)

        self.clear_right_panel()
        match_ui = WrestlingMatchUI(w1, w2, diplomacy_system=self.diplomacy_system)
        self.right_panel.addWidget(match_ui)
        self.right_panel.setCurrentWidget(match_ui)

    def load_database_ui(self):
        from ui.wrestler_database_pyqt import WrestlerDatabaseUI
        self.clear_right_panel()
        creator = WrestlerDatabaseUI()
        self.right_panel.addWidget(creator)
        self.right_panel.setCurrentWidget(creator)

    def play_event_from_news(self, event_id):
        from ui.event_manager_helper import get_event_by_id
        from ui.event_summary_pyqt import EventSummaryUI
        from game_state import set_event_lock

        event_data = get_event_by_id(event_id)

        def on_event_complete():
            set_event_lock(False)
            self.pending_news_item = None
            self.load_news_feed_ui()

        self.clear_right_panel()
        summary = EventSummaryUI(event_data, on_back=on_event_complete, diplomacy_system=self.diplomacy_system)
        self.right_panel.addWidget(summary)
        self.right_panel.setCurrentWidget(summary)

    def show_news_item(self, item):
        self.pending_news_item = item  # Store it so it can be displayed later

        # If NewsFeedUI is currently showing, add the item directly
        current = self.right_panel.currentWidget()
        from ui.news_feed_pyqt import NewsFeedUI
        if isinstance(current, NewsFeedUI):
            current.add_item(
                text=item["text"],
                action_label=item["action_label"],
                action=lambda: self.play_event_from_news(item["event_id"])
            )

    def load_event_list_ui(self):
        from ui.event_list_pyqt import EventsUI
        self.clear_right_panel()
        screen = EventsUI(on_back=self.load_calendar_ui, load_screen=self.set_screen)
        self.right_panel.addWidget(screen)
        self.right_panel.setCurrentWidget(screen)

    def set_screen(self, widget):
        self.clear_right_panel()
        self.right_panel.addWidget(widget)
        self.right_panel.setCurrentWidget(widget)

    def load_event_overview_ui(self):
        from ui.event_overview_ui import EventOverviewUI
        self.clear_right_panel()
        screen = EventOverviewUI(on_back=self.load_news_feed_ui, load_event=self.play_event_from_news)
        self.right_panel.addWidget(screen)
        self.right_panel.setCurrentWidget(screen)

    def load_dev_diplomacy_ui(self):
        from ui.dev_diplomacy_ui import DevDiplomacyUI
        self.clear_right_panel()
        dev_screen = DevDiplomacyUI(diplomacy_system=self.diplomacy_system, on_back=self.load_news_feed_ui)
        self.right_panel.addWidget(dev_screen)
        self.right_panel.setCurrentWidget(dev_screen)
    def save_game_state_manually(self):
        from game_state import save_game_state
        self.diplomacy_system.save_to_db()
        save_game_state()
        print("[Save] Manual Save Complete!")

    def load_promo_test_ui(self):
        self.clear_right_panel()
        promo_ui = PromoTestUI()
        self.right_panel.addWidget(promo_ui)
        self.right_panel.setCurrentWidget(promo_ui)

    def build_news_feed_ui(self):
        """Build the news feed UI with storyline management button."""
        news_feed = QWidget()
        layout = QVBoxLayout(news_feed)
        
        # Add storyline management button
        storyline_btn = QPushButton("Manage Storylines")
        apply_styles(storyline_btn, "button_blue")
        storyline_btn.clicked.connect(self.load_storyline_management_ui)
        layout.addWidget(storyline_btn)
        
        # Add other news feed content here
        layout.addStretch()
        
        return news_feed

    def load_storyline_management_ui(self):
        """Load the storyline management UI."""
        from ui.storyline_management_ui import StorylineManagementUI
        self.clear_right_panel()
        storyline_ui = StorylineManagementUI(on_back=self.load_news_feed_ui)
        self.right_panel.addWidget(storyline_ui)
        self.right_panel.setCurrentWidget(storyline_ui)
