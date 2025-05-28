#!/usr/bin/env python3
"""
Debug script to log versus promo beat content to console for testing.
"""

import sys
import os
import random
import json
from promo.versus_promo_engine import VersusPromoEngine
from promo.commentary_engine import generate_commentary

def create_test_wrestler(name: str, archetype: str = "Regular"):
    """Create a test wrestler with specified archetype."""
    attribute_sets = {
        "Weak": {
            "promo_delivery": 5,
            "fan_engagement": 5,
            "entrance_presence": 5,
            "presence_under_fire": 5,
            "confidence": 5,
            "reputation": 5,
            "focus": 5,
            "determination": 5
        },
        "Regular": {
            "promo_delivery": 10,
            "fan_engagement": 10,
            "entrance_presence": 10,
            "presence_under_fire": 10,
            "confidence": 10,
            "reputation": 10,
            "focus": 10,
            "determination": 10
        },
        "Talented": {
            "promo_delivery": 15,
            "fan_engagement": 15,
            "entrance_presence": 15,
            "presence_under_fire": 15,
            "confidence": 15,
            "reputation": 15,
            "focus": 15,
            "determination": 15
        }
    }
    return {
        "id": random.randint(1000, 9999),
        "name": name,
        "attributes": attribute_sets[archetype]
    }

def main():
    """Run a versus promo and log each beat's content to console."""
    print("\n========== VERSUS PROMO DEBUG ==========\n")
    
    # Create test wrestlers
    wrestler1 = create_test_wrestler("Edge", "Talented")
    wrestler2 = create_test_wrestler("Grandmaster Sexay", "Regular")
    
    # Run the versus promo
    engine = VersusPromoEngine(wrestler1, wrestler2)
    result = engine.simulate()
    
    # Display the raw beat data
    print(f"Total beats: {len(result['beats'])}")
    print("=" * 40)
    
    # Process and display each beat with its raw structure
    for i, beat in enumerate(result["beats"]):
        print(f"\n----- BEAT #{i+1} -----")
        print(f"Raw beat data:")
        
        # Format beat data for better readability
        formatted_beat = json.dumps(beat, indent=2, default=str)
        print(formatted_beat)
        
        # Generate commentary for the beat
        commentary = generate_commentary(beat)
        print(f"\nGenerated commentary:")
        print(json.dumps(commentary, indent=2, default=str))
        
        print("-" * 40)
    
    # Display final scores
    print("\nFinal Scores:")
    print(json.dumps(result["final_scores"], indent=2))

if __name__ == "__main__":
    main() 