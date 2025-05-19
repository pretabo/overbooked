import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from match_engine_utils import select_weighted_manoeuvre

class TestWeightedManoeuvreSelection(unittest.TestCase):

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

    def test_select_weighted_manoeuvre(self):
        # Simulate turn 10
        turn = 10
        move = select_weighted_manoeuvre(self.wrestler, turn)

        # Assert that a move is returned
        self.assertIsNotNone(move, "No move was selected.")

        # Assert that the move has the expected structure
        self.assertEqual(len(move), 4, "Move should have 4 attributes: name, type, damage, difficulty.")
        self.assertIn(move[1], ["strike", "slam", "grapple", "aerial", "submission"], "Invalid move type.")

if __name__ == "__main__":
    unittest.main()
