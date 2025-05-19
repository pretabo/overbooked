from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from ui.event_manager_helper import update_event_results, get_event_by_id
from match_engine import get_all_wrestlers, load_wrestler_by_id
from ui.match_ui_pyqt import WrestlingMatchUI
from ui.theme import apply_styles
from game_state import get_game_date
from ui.event_manager_helper import save_match_to_db  # or your new module


class EventSummaryUI(QWidget):
    def __init__(self, event_data, on_back=None, diplomacy_system=None):
        super().__init__()
        self.event = event_data
        self.on_back = on_back
        self.diplomacy_system = diplomacy_system
        self.segment_index = len(self.event.get("results", []))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Title Block (Event name + date)
        self.title_label = QLabel(self.event["name"])
        self.title_label.setAlignment(Qt.AlignCenter)
        apply_styles(self.title_label, "label_header")
        layout.addWidget(self.title_label)

        self.date_label = QLabel(get_game_date())
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setStyleSheet("font-size: 16pt; color: #aaa; font-family: Fira Code;")
        layout.addWidget(self.date_label)

        # Match summary area
        self.summary_area = QFrame()
        self.summary_layout = QVBoxLayout(self.summary_area)
        self.summary_area.setStyleSheet("background-color: #1e1e1e; border: 1px solid #444; padding: 14px;")
        layout.addWidget(self.summary_area)

        self.populate_segments()

        # Segment controls
        if self.segment_index < len(self.event["card"]):
            next_type = "Match" if isinstance(self.event["card"][self.segment_index][1], str) else "Promo"
            self.play_button = QPushButton(f"Play Next {next_type}")
            apply_styles(self.play_button, "button_blue")
            self.play_button.clicked.connect(self.play_next_segment)
            layout.addWidget(self.play_button)

        if self.on_back:
            back_btn = QPushButton("Back")
            apply_styles(back_btn, "button_nav")
            back_btn.clicked.connect(self.on_back)
            layout.addWidget(back_btn)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def populate_segments(self):
        while self.summary_layout.count():
            child = self.summary_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        results_lookup = {
            tuple(result[:2]): result[2]
            for result in self.event.get("results", []) if len(result) == 3
        }

        for idx, segment in enumerate(self.event["card"]):
            if isinstance(segment[1], str) and segment[1] == "Promo":
                # This is a promo
                name = segment[0]
                text = f"{idx + 1}. Promo by {name}"
            else:
                # This is a match
                name1, name2 = segment
                winner = results_lookup.get((name1, name2)) or results_lookup.get((name2, name1))
                if winner:
                    loser = name2 if winner == name1 else name1
                    text = f"{idx + 1}. {winner} defeated {loser}"
                else:
                    text = f"{idx + 1}. {name1} vs {name2}"

            label = QLabel(text)
            label.setStyleSheet("""
                font-family: Fira Code;
                font-size: 11pt;
                color: #e0e0e0;
                padding: 4px 2px;
            """)
            self.summary_layout.addWidget(label)

    def play_next_segment(self):
        if self.segment_index >= len(self.event["card"]):
            return

        segment = self.event["card"][self.segment_index]
        parent = self.window()  # Store parent reference

        if isinstance(segment[1], str) and segment[1] == "Promo":
            # Handle promo
            name = segment[0]
            all_wrestlers = get_all_wrestlers()
            name_to_id = {name: id_ for id_, name in all_wrestlers}
            wrestler = load_wrestler_by_id(name_to_id[name])

            from ui.promo_test_ui import PromoTestUI
            
            # Create a closure to capture the parent reference safely
            def handle_promo_completion(result):
                # Update event results with promo result
                updated_results = self.event.get("results", []) + [(name, "Promo", result.get("final_rating", 0))]
                update_event_results(self.event["id"], updated_results)

                # Show updated event summary
                updated_event = get_event_by_id(self.event["id"])
                new_summary = EventSummaryUI(updated_event, on_back=self.on_back, diplomacy_system=self.diplomacy_system)

                parent.clear_right_panel()
                parent.right_panel.addWidget(new_summary)
                parent.right_panel.setCurrentWidget(new_summary)
            
            promo_ui = PromoTestUI(wrestler, on_finish=handle_promo_completion)
            parent.clear_right_panel()
            parent.right_panel.addWidget(promo_ui)
            parent.right_panel.setCurrentWidget(promo_ui)
        else:
            # Handle match
            name1, name2 = segment
            all_wrestlers = get_all_wrestlers()
            name_to_id = {name: id_ for id_, name in all_wrestlers}
            w1 = load_wrestler_by_id(name_to_id[name1])
            w2 = load_wrestler_by_id(name_to_id[name2])

            def on_next_match(result):
                # Save match stats to DB
                save_match_to_db(
                    event_id=self.event["id"],
                    match_index=self.segment_index,
                    name1=name1,
                    name2=name2,
                    result=result
                )

                # Update event results
                winner = result["winner"]
                updated_results = self.event.get("results", []) + [(name1, name2, winner)]
                update_event_results(self.event["id"], updated_results)

                updated_event = get_event_by_id(self.event["id"])
                new_summary = EventSummaryUI(updated_event, on_back=self.on_back, diplomacy_system=self.diplomacy_system)

                parent.clear_right_panel()
                parent.right_panel.addWidget(new_summary)
                parent.right_panel.setCurrentWidget(new_summary)

            match_ui = WrestlingMatchUI(w1, w2, on_next_match=on_next_match, diplomacy_system=self.diplomacy_system)
            parent.clear_right_panel()
            parent.right_panel.addWidget(match_ui)
            parent.right_panel.setCurrentWidget(match_ui)
