from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QApplication, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap

from src.core.game_state import get_game_date, advance_day, save_game_state, load_game_state
from src.ui.roster_ui_pyqt import RosterUI
from src.ui.calendar_view_ui_pyqt import CalendarViewUI
from src.ui.promo_test_ui import PromoTestUI
from src.ui.theme import apply_styles
from datetime import datetime
from src.core.diplomacy_system import DiplomacySystem
import logging
try:
    import src.core.game_state_debug as game_state_debug
except ImportError:
    game_state_debug = None
from src.ui.wrestler_creator_ui import WrestlerCreatorUI
from src.ui.debug_ui_pyqt import DebugUI
from src.ui.business_ui import BusinessDashboard
from src.ui.business_stats_ui import BusinessStatsUI
from src.ui.testing_ui import TestingUI
from src.ui.merchandise_manager_ui import MerchandiseManagerUI
from src.ui.event_manager_helper import get_all_events
import sqlite3
from src.db.utils import db_path


# Import other screens here as needed

class MainApp(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Overbooked: Wrestling Simulator")
        self.setGeometry(100, 100, 1280, 720)
        
        # Set the application icon
        app_icon = QIcon("image_assets/logo.png")
        self.setWindowIcon(app_icon)
        
        self.pending_news_item = None
        self.diplomacy_system = DiplomacySystem()

        logging.info("Initializing MainApp")
        self.diplomacy_system.load_from_db()
        
        # Ensure relationships are properly loaded from the database
        self.refresh_relationships()
        
        logging.info("[Diplomacy] Loaded relationships from database.")


        from src.core.game_state import load_game_state
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
        main_layout.addWidget(self.left_panel_widget, 1)
        main_layout.addWidget(self.right_panel, 4)

        # Add logo at the top of left panel
        logo_label = QLabel()
        logo_pixmap = QIcon("image_assets/logo.png").pixmap(200, 100)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setContentsMargins(10, 10, 10, 0)
        self.left_panel.addWidget(logo_label)

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

        # Main navigation buttons
        self.add_nav_button("News Feed", self.load_news_feed_ui)
        self.add_nav_button("Event Calendar", self.load_calendar_ui)
        self.add_nav_button("Event Overview", self.load_event_overview_ui)
        self.add_nav_button("View Roster", self.load_roster_ui)
        self.add_nav_button("Manage Storylines", self.load_storyline_management_ui)
        self.add_nav_button("Business", self.load_business_stats_ui)
        self.add_nav_button("Testing", self.load_testing_ui)

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
        logging.info("MainApp initialization complete")

    def add_nav_button(self, label, callback):
        btn = QPushButton(label)
        from src.ui.theme import apply_styles
        apply_styles(btn, "button_nav")
        btn.clicked.connect(callback)
        self.left_panel.addWidget(btn)

    def clear_right_panel(self):
        while self.right_panel.count():
            widget = self.right_panel.widget(0)
            self.right_panel.removeWidget(widget)
            widget.deleteLater()

    def load_business_dashboard(self):
        """Load the business dashboard UI"""
        self.clear_right_panel()
        dashboard = BusinessDashboard()
        
        # Add button to access merchandise manager
        merchandise_btn = QPushButton("Merchandise Manager")
        merchandise_btn.clicked.connect(self.load_merchandise_manager_ui)
        dashboard.layout().addWidget(merchandise_btn)
        
        self.right_panel.addWidget(dashboard)
        self.right_panel.setCurrentWidget(dashboard)

    def load_business_stats_ui(self):
        """Load the business stats UI"""
        self.clear_right_panel()
        stats_ui = BusinessStatsUI()
        # Connect the dashboard button to load the dashboard
        stats_ui.open_business_dashboard = self.load_business_dashboard
        self.right_panel.addWidget(stats_ui)
        self.right_panel.setCurrentWidget(stats_ui)
        
    def load_merchandise_manager_ui(self):
        """Load the merchandise manager UI"""
        self.clear_right_panel()
        merchandise_ui = MerchandiseManagerUI()
        self.right_panel.addWidget(merchandise_ui)
        self.right_panel.setCurrentWidget(merchandise_ui)

    def load_testing_ui(self):
        """Load the testing UI with all testing tools"""
        self.clear_right_panel()
        testing_ui = TestingUI(load_screen_callback=self.load_testing_screen)
        self.right_panel.addWidget(testing_ui)
        self.right_panel.setCurrentWidget(testing_ui)

    def load_testing_screen(self, screen_name):
        """Load a specific testing screen"""
        if screen_name == "add_wrestler":
            self.load_wrestler_creator_ui()
        elif screen_name == "simulate_match":
            self.load_match_ui()
        elif screen_name == "test_promos":
            self.load_promo_test_ui()
        elif screen_name == "test_event_promos":
            self.load_event_promo_test()
        elif screen_name == "diplomacy_manager":
            self.load_dev_diplomacy_ui()
        elif screen_name == "debug_menu":
            self.load_debug_menu_ui()
        elif screen_name == "news_feed":
            self.load_news_feed_ui()

    def advance_game_day(self):
        """Advance the game by one day and check for events."""
        from src.core.game_state import (
            get_game_date, is_event_locked, set_event_lock,
            advance_day, save_game_state, check_and_clear_event_lock
        )

        # First check if we're locked because of an event
        event_locked = is_event_locked()
        
        # Try to clear the lock automatically if no event exists for today
        if event_locked:
            lock_cleared = check_and_clear_event_lock()
            if lock_cleared:
                event_locked = False
                logging.info("Event lock cleared automatically as no event exists for today")
                print("🔓 Event lock cleared automatically as no event exists for today")
        
        # If still locked, we must have a real event that needs to be played
        if event_locked:
            logging.warning("🔒 Date locked — event must be played first.")
            print("🔒 Date locked — event must be played first.")
            # Show a message box to inform the user
            QMessageBox.warning(
                self, 
                "Event Locked", 
                "You need to play the scheduled event before advancing the date.",
                QMessageBox.Ok
            )
            return

        # Advance the game date
        logging.info("Advancing game date...")
        print("🧭 Advancing game date...")
        advance_day()
        
        # Save relationships
        self.diplomacy_system.save_to_db()
        logging.info("[Diplomacy] Autosaved relationships after date advance.")
        
        # Update the date label
        today = datetime.strptime(get_game_date(), "%A, %d %B %Y")
        formatted = today.strftime("%A\n%d %B %Y")
        self.date_label.setText(formatted)
        
        # Format today's date for database comparison
        todays_date = today.strftime("%Y-%m-%d")
        logging.info(f"Checking for events on {todays_date}")
        print(f"📅 Current game date: {today.strftime('%A, %d %B %Y')}")
        print(f"📅 Checking for events on {todays_date}")

        # Get all events and check for matches
        all_events = get_all_events()
        event_found = False
        
        # Debug output
        print(f"📊 Found {len(all_events)} events in database")
        
        for ev in all_events:
            ev_id, ev_name, _, _, _, ev_date = ev[0], ev[1], ev[2], ev[3], ev[4], ev[5]
            print(f"🔍 Checking event #{ev_id}: {ev_name} - Date: {ev_date}")
            
            # Check if the event is for today
            if ev_date == todays_date:
                event_found = True
                logging.info(f"Event found for today: {ev_name} (ID: {ev_id})")
                print(f"🎯 Event FOUND on {todays_date}: {ev_name}")
                
                # Lock the game
                set_event_lock(True)
                print("🔒 Event lock ENABLED")
                
                # Save game state with the lock
                save_game_state()
                
                # Show the event in the news feed
                self.show_news_item({
                    "type": "event",
                    "text": f"📢 An event is scheduled for today: {ev_name}",
                    "action_label": "Play Event",
                    "event_id": ev_id
                })
                
                # Show a message box to inform the user
                QMessageBox.information(
                    self, 
                    "Event Ready", 
                    f"An event '{ev_name}' is scheduled for today. You need to play it before continuing.",
                    QMessageBox.Ok
                )
                
                break
        
        if not event_found:
            print("✅ No events found for today")
        
        # Save game state
        save_game_state()
        print("💾 Game state saved")
        
        # Update the UI - go to news feed
        self.load_news_feed_ui()

    def load_roster_ui(self):
        self.clear_right_panel()
        roster_ui = RosterUI(on_view_profile=self.load_wrestler_profile)
        self.right_panel.addWidget(roster_ui)
        self.right_panel.setCurrentWidget(roster_ui)

    def load_wrestler_profile(self, wrestler_id):
        from src.ui.wrestler_profile_pyqt import WrestlerProfileUI
        self.clear_right_panel()
        profile_ui = WrestlerProfileUI(wrestler_id, on_back=self.load_roster_ui, diplomacy_system=self.diplomacy_system)
        self.right_panel.addWidget(profile_ui)
        self.right_panel.setCurrentWidget(profile_ui)

    def load_news_feed_ui(self):
        from src.ui.news_feed_pyqt import NewsFeedUI
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
        from src.ui.calendar_view_ui_pyqt import CalendarViewUI
        self.clear_right_panel()
        calendar = CalendarViewUI(on_back=self.load_news_feed_ui, news_callback=self.show_news_item)
        self.right_panel.addWidget(calendar)
        self.right_panel.setCurrentWidget(calendar)

    def load_match_ui(self):
        from src.ui.match_ui_pyqt import WrestlingMatchUI
        from src.core.match_engine import load_wrestler_by_id
        from src.core.match_engine import get_all_wrestlers
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
        from src.ui.wrestler_database_pyqt import WrestlerDatabaseUI
        self.clear_right_panel()
        creator = WrestlerDatabaseUI()
        self.right_panel.addWidget(creator)
        self.right_panel.setCurrentWidget(creator)

    def play_event_from_news(self, event_id):
        from src.ui.event_manager_helper import get_event_by_id
        from src.ui.event_summary_pyqt import EventSummaryUI
        from src.core.game_state import set_event_lock, save_game_state

        event_data = get_event_by_id(event_id)
        print(f"🎮 Playing event from news: {event_data['name']} (ID: {event_id})")

        def on_event_complete():
            # Make sure to unlock events when returning from the event screen
            set_event_lock(False)
            save_game_state()
            print("🔓 Event completed - unlocking (from on_event_complete)")
            
            # Clear the pending news item and return to news feed
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
        from src.ui.news_feed_pyqt import NewsFeedUI
        if isinstance(current, NewsFeedUI):
            current.add_item(
                text=item["text"],
                action_label=item["action_label"],
                action=lambda: self.play_event_from_news(item["event_id"])
            )

    def load_event_list_ui(self):
        from src.ui.event_list_pyqt import EventsUI
        self.clear_right_panel()
        screen = EventsUI(on_back=self.load_calendar_ui, load_screen=self.set_screen)
        self.right_panel.addWidget(screen)
        self.right_panel.setCurrentWidget(screen)

    def set_screen(self, widget):
        self.clear_right_panel()
        self.right_panel.addWidget(widget)
        self.right_panel.setCurrentWidget(widget)

    def load_event_overview_ui(self):
        from src.ui.event_overview_ui import EventOverviewUI
        self.clear_right_panel()
        screen = EventOverviewUI(on_back=self.load_news_feed_ui, load_event=self.play_event_from_news)
        self.right_panel.addWidget(screen)
        self.right_panel.setCurrentWidget(screen)

    def load_dev_diplomacy_ui(self):
        from src.ui.dev_diplomacy_ui import DevDiplomacyUI
        self.clear_right_panel()
        dev_screen = DevDiplomacyUI(diplomacy_system=self.diplomacy_system, on_back=self.load_testing_ui)
        self.right_panel.addWidget(dev_screen)
        self.right_panel.setCurrentWidget(dev_screen)

    def load_debug_menu_ui(self):
        self.clear_right_panel()
        debug_ui = DebugUI(diplomacy_system=self.diplomacy_system)
        self.right_panel.addWidget(debug_ui)
        self.right_panel.setCurrentWidget(debug_ui)
        
    def save_game_state_manually(self):
        from src.core.game_state import save_game_state
        self.diplomacy_system.save_to_db()
        save_game_state()
        logging.info("Manual save completed")
        if game_state_debug:
            game_state_debug.export_debug_state()  # Also export debug state
        print("[Save] Manual Save Complete!")
        QMessageBox.information(self, "Save Complete", 
                               "Game state saved successfully.\nDebug state also exported.")

    def load_promo_test_ui(self):
        self.clear_right_panel()
        promo_ui = PromoTestUI()
        self.right_panel.addWidget(promo_ui)
        self.right_panel.setCurrentWidget(promo_ui)
        
    def load_event_promo_test(self):
        """Load the event promo UI with a random wrestler for testing."""
        from src.ui.event_promo_ui import EventPromoUI
        from src.core.match_engine import get_all_wrestlers, load_wrestler_by_id
        import random
        
        self.clear_right_panel()
        
        # Get a random wrestler
        wrestlers = get_all_wrestlers()
        if wrestlers:
            wrestler_id, _ = random.choice(wrestlers)
            wrestler = load_wrestler_by_id(wrestler_id)
            
            # Create and display the event promo UI
            def on_promo_finish(result):
                QMessageBox.information(
                    self, 
                    "Promo Complete", 
                    f"Event promo complete! Rating: {result.get('final_rating', 0):.1f}"
                )
                # Go back to test promo UI
                self.load_testing_ui()
                
            promo_ui = EventPromoUI(wrestler, on_finish=on_promo_finish, diplomacy_system=self.diplomacy_system)
            self.right_panel.addWidget(promo_ui)
            self.right_panel.setCurrentWidget(promo_ui)
        else:
            QMessageBox.warning(self, "Error", "No wrestlers found in database.")
            self.load_testing_ui()

    def load_storyline_management_ui(self):
        """Load the storyline management UI."""
        try:
            from src.ui.storyline_management_ui import StorylineManagementUI
            self.clear_right_panel()
            screen = StorylineManagementUI(on_back=self.load_news_feed_ui)
            self.right_panel.addWidget(screen)
            self.right_panel.setCurrentWidget(screen)
        except Exception as e:
            import logging
            logging.error(f"Unexpected error in storyline management: {str(e)}")
            QMessageBox.warning(
                self,
                "Storyline Manager Error",
                f"Could not load the storyline manager:\n{str(e)}"
            )

    def load_wrestler_creator_ui(self):
        """Load the wrestler creator UI in the right panel"""
        self.clear_right_panel()
        creator_ui = WrestlerCreatorUI()
        self.right_panel.addWidget(creator_ui)
        self.right_panel.setCurrentWidget(creator_ui)

    def setup_navigation(self):
        # Date container at the top
        date_container = QHBoxLayout()
        self.date_label = QLabel(get_game_date())
        self.date_label.setStyleSheet("color: white; font-size: 16pt;")
        date_container.addWidget(self.date_label)
        date_container.setAlignment(Qt.AlignCenter)
        self.left_panel.addLayout(date_container)
        
        # Navigation buttons
        self.left_panel.addSpacing(20)
        
        # Add buttons with icons
        roster_btn = QPushButton("Roster")
        roster_btn.clicked.connect(self.load_roster_ui)
        apply_styles(roster_btn, "button_nav")
        self.left_panel.addWidget(roster_btn)
        
        calendar_btn = QPushButton("Calendar")
        calendar_btn.clicked.connect(self.load_calendar_ui)
        apply_styles(calendar_btn, "button_nav")
        self.left_panel.addWidget(calendar_btn)
        
        promo_btn = QPushButton("Promo Test")
        promo_btn.clicked.connect(self.load_promo_test_ui)
        apply_styles(promo_btn, "button_nav")
        self.left_panel.addWidget(promo_btn)
        
        # Add versus promo button
        versus_promo_btn = QPushButton("Versus Promo")
        versus_promo_btn.clicked.connect(self.load_versus_promo_ui)
        apply_styles(versus_promo_btn, "button_nav")
        self.left_panel.addWidget(versus_promo_btn)
        
        wrestler_creator_btn = QPushButton("Wrestler Creator")
        wrestler_creator_btn.clicked.connect(self.load_wrestler_creator_ui)
        apply_styles(wrestler_creator_btn, "button_nav")
        self.left_panel.addWidget(wrestler_creator_btn)
        
        self.left_panel.addStretch()
        
        # Development tools section
        dev_label = QLabel("Development Tools")
        dev_label.setStyleSheet("color: #aaa; font-size: 10pt;")
        dev_label.setAlignment(Qt.AlignCenter)
        self.left_panel.addWidget(dev_label)
        
        # Debug menu button
        debug_btn = QPushButton("Debug Menu")
        debug_btn.clicked.connect(self.load_debug_menu_ui)
        apply_styles(debug_btn, "button_flat")
        self.left_panel.addWidget(debug_btn)

    def load_versus_promo_ui(self):
        self.clear_right_panel()
        from src.ui.versus_promo_ui import VersusPromoUI
        versus_ui = VersusPromoUI()
        self.right_panel.addWidget(versus_ui)
        self.right_panel.setCurrentWidget(versus_ui)

    def refresh_relationships(self):
        """Force reload relationships from the database"""
        try:
            # First save any existing relationships
            self.diplomacy_system.save_to_db()
            
            # Clear current relationships 
            self.diplomacy_system.relationships = {}
            
            # Reload from the database
            conn = sqlite3.connect(db_path("relationships.db"))
            cursor = conn.cursor()
            
            # Load relationships
            cursor.execute("SELECT wrestler1_id, wrestler2_id, relationship_value FROM relationships")
            relationships = cursor.fetchall()
            
            # Initialize relationship dictionary
            for w1, w2, value in relationships:
                key = self.diplomacy_system._make_key(w1, w2)
                self.diplomacy_system.relationships[key] = value
                
            conn.close()
            
            logging.info(f"Refreshed {len(self.diplomacy_system.relationships)} relationships")
        except Exception as e:
            logging.error(f"Error refreshing relationships: {e}")
