import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from match_engine_utils import select_weighted_manoeuvre_with_personality

class TestWeightedManoeuvreWithPhases(unittest.TestCase):

    def setUp(self):
        # Example wrestler setup
        self.wrestler = {
            "stamina": 80,
            "strike_accuracy": 12,
            "powerlifting": 15,
            "grapple_control": 10,
            "grip_strength": 8,
            "aerial_precision": 14,
            "mat_transitions": 9,
            "height": 72,  # 6 feet
            "weight": 220  # 220 pounds
        }

        self.wrestler.update({
            "id": 1,
            "confidence": 10,
            "risk_assessment": 8,
            "determination": 12,
            "focus": 9,
            "resilience": 11,
            "fan_engagement": 16,
            "promo_delivery": 14
        })

        self.opponent = {
            "stamina": 70,
            "strike_accuracy": 10,
            "powerlifting": 18,
            "grapple_control": 12,
            "grip_strength": 10,
            "aerial_precision": 8,
            "mat_transitions": 7,
            "height": 78,  # 6 feet 6 inches
            "weight": 260  # 260 pounds
        }

    def test_early_phase(self):
        turn = 5  # Early phase
        move = select_weighted_manoeuvre_with_personality(self.wrestler, self.opponent, turn)
        self.assertIsNotNone(move, "No move was selected in early phase.")

    def test_mid_phase(self):
        turn = 20  # Mid phase
        move = select_weighted_manoeuvre_with_personality(self.wrestler, self.opponent, turn)
        self.assertIsNotNone(move, "No move was selected in mid phase.")

    def test_late_phase(self):
        turn = 35  # Late phase
        move = select_weighted_manoeuvre_with_personality(self.wrestler, self.opponent, turn)
        self.assertIsNotNone(move, "No move was selected in late phase.")

if __name__ == "__main__":
    unittest.main()
