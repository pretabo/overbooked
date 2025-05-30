import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSpacerItem, QSizePolicy,
    QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from src.ui.event_manager_helper import update_event_results, get_event_by_id
from src.core.match_engine import get_all_wrestlers, load_wrestler_by_id
from src.ui.match_ui_pyqt import WrestlingMatchUI
from src.ui.theme import apply_styles
from src.core.game_state import get_game_date, set_event_lock
from src.ui.event_manager_helper import save_match_to_db  # or your new module


class EventSummaryUI(QWidget):
    def __init__(self, event_data, on_back=None, diplomacy_system=None):
        super().__init__()
        self.event = event_data
        self.on_back = on_back
        self.diplomacy_system = diplomacy_system
        self.segment_index = len(self.event.get("results", []))

        # Print debug info
        print(f"🎭 Loading event: {self.event['name']} (ID: {self.event['id']})")
        print(f"🎭 Segments played: {self.segment_index} of {len(self.event.get('card', []))}")

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(25)

        # Title Block (Event name + date)
        self.title_label = QLabel(self.event["name"])
        self.title_label.setAlignment(Qt.AlignCenter)
        apply_styles(self.title_label, "label_header")
        main_layout.addWidget(self.title_label)

        self.date_label = QLabel(get_game_date())
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setStyleSheet("font-size: 16pt; color: #aaa; font-family: Fira Code;")
        main_layout.addWidget(self.date_label)

        # Create scrollable area for match segments
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)  # Remove the frame border
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Scroll area container
        scroll_container = QWidget()
        self.summary_layout = QVBoxLayout(scroll_container)
        self.summary_layout.setSpacing(12)
        self.summary_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add styled background to the scroll container
        scroll_container.setStyleSheet("background-color: #1e1e1e; border: 1px solid #444; border-radius: 8px;")
        
        # Populate the segments
        self.populate_segments()
        
        # Set the scroll area widget
        scroll_area.setWidget(scroll_container)
        
        # Make the scroll area take up as much space as possible
        main_layout.addWidget(scroll_area, 1)  # 1 = stretch factor
        
        # Button container (fixed at bottom)
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        # Segment controls
        if self.segment_index < len(self.event["card"]):
            segment = self.event["card"][self.segment_index]
            next_type = "Promo" if isinstance(segment[1], str) and segment[1] == "Promo" else "Match"
            
            # Create a more prominent play button with icon
            self.play_button = QPushButton(f"▶ Play Next {next_type}")
            self.play_button.setFixedHeight(50)  # Make button taller
            self.play_button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 14pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
            """)
            self.play_button.clicked.connect(self.play_next_segment)
            button_layout.addWidget(self.play_button)
        else:
            # All segments played, show a completion message
            completion_label = QLabel("✅ All segments of this event have been played!")
            completion_label.setStyleSheet("""
                color: #4CAF50;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px;
                background-color: #1e1e1e;
                border-radius: 6px;
            """)
            completion_label.setAlignment(Qt.AlignCenter)
            button_layout.addWidget(completion_label)
            
            # Unlock events since all segments are played
            set_event_lock(False)
            print("🔓 All segments completed - event lock disabled")

        if self.on_back:
            back_btn = QPushButton("Back")
            apply_styles(back_btn, "button_nav")
            back_btn.clicked.connect(self.handle_back)
            button_layout.addWidget(back_btn)
        
        # Add button container to main layout
        main_layout.addWidget(button_container)

    def populate_segments(self):
        while self.summary_layout.count():
            child = self.summary_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        results_lookup = {
            tuple(result[:2]): result[2]
            for result in self.event.get("results", []) if len(result) == 3
        }
        
        # Debug print match ratings
        print(f"Match ratings in event: {self.event.get('match_ratings', [])}")

        for idx, segment in enumerate(self.event["card"]):
            # Create a container for each segment with better styling
            segment_container = QFrame()
            segment_container.setStyleSheet("""
                background-color: #2a2a2a;
                border-radius: 8px;
                margin: 4px 8px;
                padding: 8px;
            """)
            segment_layout = QVBoxLayout(segment_container)
            segment_layout.setContentsMargins(12, 10, 12, 10)
            
            if isinstance(segment[1], str) and segment[1] == "Promo":
                # This is a promo
                name = segment[0]
                # Look for a promo result
                promo_rating = None
                for result in self.event.get("results", []):
                    if len(result) == 3 and result[1] == "Promo" and result[0] == name:
                        promo_rating = result[2]
                        break
                
                if promo_rating is not None:
                    # Make sure promo_rating is a number (could be a string)
                    if isinstance(promo_rating, str):
                        try:
                            promo_rating = float(promo_rating)
                        except ValueError:
                            # If conversion fails, default to a reasonable value
                            promo_rating = 70.0
                    
                    # Show completed promo with rating
                    stars = min(5, promo_rating / 20)  # Convert to star rating
                    color = self.get_rating_color(promo_rating)
                    
                    # Title with segment number
                    title = QLabel(f"{idx + 1}. Promo by {name}")
                    title.setStyleSheet(f"""
                        font-family: Fira Code;
                        font-size: 14pt;
                        font-weight: bold;
                        color: {color};
                    """)
                    segment_layout.addWidget(title)
                    
                    # Rating details
                    rating_container = QHBoxLayout()
                    
                    # Numeric rating
                    rating_label = QLabel(f"Rating: {promo_rating:.1f}")
                    rating_label.setStyleSheet("""
                        font-family: Fira Code;
                        font-size: 12pt;
                        color: #e0e0e0;
                    """)
                    rating_container.addWidget(rating_label)
                    
                    # Star display
                    star_label = QLabel()
                    star_display = ""
                    for i in range(5):
                        if i < int(stars):
                            star_display += "★"  # Full star
                        elif i == int(stars) and stars - int(stars) >= 0.5:
                            star_display += "½"  # Half star
                        else:
                            star_display += "☆"  # Empty star
                    
                    star_label.setText(star_display)
                    star_label.setStyleSheet("""
                        font-family: Fira Code;
                        font-size: 28pt;
                        font-weight: bold;
                        color: gold;
                        padding: 0;
                        margin: 0;
                    """)
                    # Make star label take more space in the container
                    rating_container.addWidget(star_label, alignment=Qt.AlignRight | Qt.AlignVCenter)
                    # Set a 3:1 ratio between stars and numeric rating
                    rating_container.setStretch(0, 1)  # Numeric rating
                    rating_container.setStretch(1, 3)  # Star display
                    
                    segment_layout.addLayout(rating_container)
                else:
                    # Show pending promo
                    title = QLabel(f"{idx + 1}. Promo by {name}")
                    title.setStyleSheet("""
                        font-family: Fira Code;
                        font-size: 14pt;
                        font-weight: bold;
                        color: #e0e0e0;
                    """)
                    segment_layout.addWidget(title)
                    
                    status = QLabel("(Pending)")
                    status.setStyleSheet("""
                        font-family: Fira Code;
                        font-size: 11pt;
                        font-style: italic;
                        color: #aaaaaa;
                    """)
                    segment_layout.addWidget(status)
            else:
                # This is a match
                name1, name2 = segment
                winner = results_lookup.get((name1, name2)) or results_lookup.get((name2, name1))
                
                if winner:
                    # Show completed match
                    loser = name2 if winner == name1 else name1
                    
                    # Look for match rating if available
                    match_rating = None
                    for result in self.event.get("match_ratings", []):
                        if result[0] == self.event["id"] and result[1] == idx:
                            match_rating = result[2]
                            break
                    
                    # Title with segment number and winner
                    title = QLabel(f"{idx + 1}. {winner} defeated {loser}")
                    title.setStyleSheet("""
                        font-family: Fira Code;
                        font-size: 14pt;
                        font-weight: bold;
                        color: #4CAF50;
                    """)
                    segment_layout.addWidget(title)
                    
                    # If we have a match rating, display it
                    if match_rating:
                        stars = min(5, match_rating / 20)
                        
                        # Rating container
                        rating_container = QHBoxLayout()
                        
                        # Numeric rating
                        rating_label = QLabel(f"Rating: {match_rating:.1f}")
                        rating_label.setStyleSheet("""
                            font-family: Fira Code;
                            font-size: 12pt;
                            color: #e0e0e0;
                        """)
                        rating_container.addWidget(rating_label)
                        
                        # Star display
                        star_label = QLabel()
                        star_display = ""
                        for i in range(5):
                            if i < int(stars):
                                star_display += "★"  # Full star
                            elif i == int(stars) and stars - int(stars) >= 0.5:
                                star_display += "½"  # Half star
                            else:
                                star_display += "☆"  # Empty star
                        
                        star_label.setText(star_display)
                        star_label.setStyleSheet("""
                            font-family: Fira Code;
                            font-size: 28pt;
                            font-weight: bold;
                            color: gold;
                            padding: 0;
                            margin: 0;
                        """)
                        # Make star label take more space in the container
                        rating_container.addWidget(star_label, alignment=Qt.AlignRight | Qt.AlignVCenter)
                        # Set a 3:1 ratio between stars and numeric rating
                        rating_container.setStretch(0, 1)  # Numeric rating
                        rating_container.setStretch(1, 3)  # Star display
                        
                        segment_layout.addLayout(rating_container)
                else:
                    # Show pending match
                    title = QLabel(f"{idx + 1}. {name1} vs {name2}")
                    title.setStyleSheet("""
                        font-family: Fira Code;
                        font-size: 14pt;
                        font-weight: bold;
                        color: #e0e0e0;
                    """)
                    segment_layout.addWidget(title)
                    
                    status = QLabel("(Pending)")
                    status.setStyleSheet("""
                        font-family: Fira Code;
                        font-size: 11pt;
                        font-style: italic;
                        color: #aaaaaa;
                    """)
                    segment_layout.addWidget(status)
            
            # Add the segment container to the summary layout
            self.summary_layout.addWidget(segment_container)
            
        # Add a spacer at the end to push all segments to the top
        self.summary_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def get_rating_color(self, rating):
        """Return a color based on the rating value."""
        if rating >= 90:
            return "#FFD700"  # Gold
        elif rating >= 80:
            return "#4CAF50"  # Green
        elif rating >= 70:
            return "#2196F3"  # Blue
        elif rating >= 60:
            return "#FF9800"  # Orange
        elif rating >= 50:
            return "#FFEB3B"  # Yellow
        else:
            return "#F44336"  # Red

    def play_next_segment(self):
        if self.segment_index >= len(self.event["card"]):
            # All segments played, show summary
            self.show_summary()
            return
            
        # Get current segment
        segment = self.event["card"][self.segment_index]
        
        # Support for string or tuple segments for backward compatibility
        if isinstance(segment, str):
            segment_type = "promo"
            segment_data = segment
        elif isinstance(segment, tuple) and len(segment) == 2:
            segment_type = "match"
            segment_data = segment
        elif isinstance(segment, dict):
            segment_type = segment.get("type", "match")
            segment_data = segment.get("data")
        elif isinstance(segment, list) and len(segment) == 2 and segment[1] == "Promo":
            # This is a promo segment with a wrestler name and "Promo"
            segment_type = "solo_promo" 
            segment_data = segment[0]  # Wrestler name
        else:
            segment_type = "match"
            segment_data = segment
            
        # Get parent widget (main window)
        parent = self.parent()
        while parent and not hasattr(parent, 'right_panel'):
            parent = parent.parent()
            
        if not parent:
            print("Could not find parent widget with right_panel")
            return
            
        self.segment_index += 1
        
        # Handle different segment types
        if segment_type == "promo":
            # Get promo text based on segment data
            promo_text = segment_data
            if callable(segment_data):
                promo_text = segment_data()
                
            # Create and show promo UI
            promo_ui = PromoUI(promo_text, on_next=self.play_next_segment)
            
            parent.clear_right_panel()
            parent.right_panel.addWidget(promo_ui)
            parent.right_panel.setCurrentWidget(promo_ui)
        elif segment_type == "solo_promo":
            # Handle solo promos by wrestlers
            all_wrestlers = get_all_wrestlers()
            name_to_id = {name: id_ for id_, name in all_wrestlers}
            
            try:
                wrestler_id = name_to_id[segment_data]
                wrestler = load_wrestler_by_id(wrestler_id)
                
                # Create the promo engine
                from src.promo.promo_engine import PromoEngine
                # Import the proper EventPromoUI instead of PromoTestUI
                from src.ui.event_promo_ui import EventPromoUI
                
                # Store the wrestler name for use in the completion handler
                self.current_promo_wrestler = segment_data
                
                # Create the event promo UI with the wrestler
                def on_promo_finish(result):
                    # Use QTimer to safely call the handler
                    QTimer.singleShot(0, lambda: self.handle_promo_complete(result))
                
                # Use EventPromoUI instead of PromoTestUI
                promo_ui = EventPromoUI(
                    wrestler=wrestler, 
                    on_finish=on_promo_finish,
                    diplomacy_system=self.diplomacy_system
                )
                
                parent.clear_right_panel()
                parent.right_panel.addWidget(promo_ui)
                parent.right_panel.setCurrentWidget(promo_ui)
                
            except KeyError:
                print(f"Error: Could not find wrestler ID for {segment_data}")
                # Skip to next segment
                self.play_next_segment()
        else:
            # Handle match
            name1, name2 = segment_data
            all_wrestlers = get_all_wrestlers()
            name_to_id = {name: id_ for id_, name in all_wrestlers}
            w1 = load_wrestler_by_id(name_to_id[name1])
            w2 = load_wrestler_by_id(name_to_id[name2])

            def on_next_match(result):
                # Create match integrator to handle result processing
                from src.core.match_integrator import MatchIntegrator
                match_integrator = MatchIntegrator()
                
                # Process match results through integrator - this will handle stats, buffs, etc.
                match_integrator.process_match_result(result)
                
                # Save match to event database separately (this doesn't duplicate stats recording)
                save_match_to_db(
                    event_id=self.event["id"],
                    match_index=self.segment_index - 1,  # We already incremented earlier
                    name1=name1,
                    name2=name2,
                    result=result
                )

                # Update event results
                winner = result["winner"]
                updated_results = self.event.get("results", []) + [(name1, name2, winner)]
                
                # Store the match rating if available
                match_rating = None
                if "match_rating" in result:
                    match_rating = result["match_rating"]
                elif "quality" in result:
                    match_rating = result["quality"]
                
                # Make sure to always include match ratings for the UI
                match_ratings = self.event.get("match_ratings", [])
                
                if match_rating is not None:
                    match_ratings.append((self.event["id"], self.segment_index - 1, match_rating))
                    # Update event with match ratings
                    update_event_results(
                        self.event["id"], 
                        updated_results, 
                        match_ratings=match_ratings
                    )
                    print(f"Saving match rating: {match_rating} for match {self.segment_index - 1}")
                else:
                    # Update event with just the results
                    update_event_results(self.event["id"], updated_results)
                    print(f"No match rating available for match {self.segment_index - 1}")

                # Check if all segments have been played
                updated_event = get_event_by_id(self.event["id"])
                if len(updated_event.get("results", [])) >= len(updated_event.get("card", [])):
                    # All segments have been played, unlock events
                    set_event_lock(False)
                    print("🔓 All segments completed - unlocking events")

                # Get the updated event with all data
                updated_event = get_event_by_id(self.event["id"])

                new_summary = EventSummaryUI(updated_event, on_back=self.on_back, diplomacy_system=self.diplomacy_system)

                parent.clear_right_panel()
                parent.right_panel.addWidget(new_summary)
                parent.right_panel.setCurrentWidget(new_summary)

            match_ui = WrestlingMatchUI(w1, w2, on_next_match=on_next_match, diplomacy_system=self.diplomacy_system)
            parent.clear_right_panel()
            parent.right_panel.addWidget(match_ui)
            parent.right_panel.setCurrentWidget(match_ui)
            
    def handle_promo_complete(self, result=None):
        """Handle completion of a promo segment - safely called as callback"""
        # Use a safer approach that doesn't rely on 'self' which might be deleted
        
        # Get parent widget (main window) directly without using self
        def create_new_summary():
            # Find main app parent
            from PyQt5.QtWidgets import QApplication
            main_app = QApplication.activeWindow()
            
            if not main_app or not hasattr(main_app, 'right_panel'):
                print("Could not find main application window")
                return
                
            # Get the updated event with all data
            event_id = self.event["id"]
            updated_event = get_event_by_id(event_id)
            
            # Update the results to include this promo (using the stored wrestler name)
            wrestler_name = self.current_promo_wrestler
            
            # Get the promo rating if available
            promo_rating = None
            if result and "final_rating" in result:
                promo_rating = result["final_rating"]
            elif result and "rating" in result:
                promo_rating = result["rating"]
            else:
                # If no rating found, use a default
                promo_rating = 75.0
                
            # Make sure promo_rating is a float
            if isinstance(promo_rating, str):
                try:
                    promo_rating = float(promo_rating)
                except ValueError:
                    # If conversion fails, use a default
                    promo_rating = 75.0
            
            # Add the promo result to the event
            updated_results = updated_event.get("results", []) + [(wrestler_name, "Promo", promo_rating)]
            
            # Update the event with the new results
            update_event_results(event_id, updated_results)
            
            # Check if all segments have been played
            updated_event = get_event_by_id(event_id)
            if len(updated_event.get("results", [])) >= len(updated_event.get("card", [])):
                # All segments have been played, unlock events
                set_event_lock(False)
                print("🔓 All segments completed - unlocking events")
            
            # Create a new summary with the updated event data
            new_summary = EventSummaryUI(
                updated_event, 
                on_back=self.on_back, 
                diplomacy_system=self.diplomacy_system
            )
            
            # If there are more segments to play, set the index and continue
            segment_index = self.segment_index
            if segment_index < len(updated_event.get("card", [])):
                new_summary.segment_index = segment_index
                
                # Clear and add the new summary
                main_app.clear_right_panel()
                main_app.right_panel.addWidget(new_summary)
                main_app.right_panel.setCurrentWidget(new_summary)
                
                # Play the next segment with a small delay
                QTimer.singleShot(100, new_summary.play_next_segment)
            else:
                # All segments played, just show the final summary
                main_app.clear_right_panel()
                main_app.right_panel.addWidget(new_summary)
                main_app.right_panel.setCurrentWidget(new_summary)
        
        # Use a timer to delay execution to avoid C++ object deleted issues
        QTimer.singleShot(0, create_new_summary)

    def handle_back(self):
        """Handle back button press with event unlocking"""
        # Check if all segments have been played
        if self.segment_index >= len(self.event["card"]):
            # Unlock events since all segments are played
            set_event_lock(False)
            print("🔓 All segments completed when going back - event lock disabled")
            
        # Call the original back handler
        if self.on_back:
            self.on_back()

    def show_summary(self):
        """Show the event summary when all segments are complete."""
        # Get the updated event with all data
        updated_event = get_event_by_id(self.event["id"])
        
        # Get the parent widget (main window)
        parent = self.parent()
        while parent and not hasattr(parent, 'right_panel'):
            parent = parent.parent()
            
        if not parent:
            print("Could not find parent widget with right_panel")
            return
            
        # Create a new summary with updated data
        new_summary = EventSummaryUI(updated_event, on_back=self.on_back, diplomacy_system=self.diplomacy_system)
        
        # All segments have been played, unlock events
        set_event_lock(False)
        print("🔓 All segments completed - unlocking events")
        
        # Display the updated summary
        parent.clear_right_panel()
        parent.right_panel.addWidget(new_summary)
        parent.right_panel.setCurrentWidget(new_summary)
