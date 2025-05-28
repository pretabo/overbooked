#!/usr/bin/env python3
"""
Test script for the versus promo system with consistent formatting.
"""

import sys
import os
import random
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

def format_promo_beat(beat, commentary):
    """Format a promo beat for display with consistent styling."""
    # Check if this is a special beat (intro or summary)
    if commentary.get("is_intro", False) or commentary.get("is_summary", False):
        return commentary["promo_line"]
    
    # Get wrestler info and format the beat
    wrestler_name = beat.get("wrestler", {}).get("name", "Wrestler")
    promo_line = commentary["promo_line"]
    commentary_line = commentary.get("commentary_line", "")
    momentum = beat.get("momentum", 0)
    confidence = beat.get("confidence", 50)
    
    # Format according to the requested style
    formatted_beat = f"{wrestler_name}: \n"
    formatted_beat += f"'{promo_line}'. \n"
    
    if commentary_line:
        formatted_beat += f"{commentary_line} \n"
    
    formatted_beat += f"⚡ {momentum:.1f} | 💪 {confidence:.1f} \n"
    
    return formatted_beat

def main():
    """Run a versus promo with consistent formatting."""
    print("\n========== VERSUS PROMO TEST ==========\n")
    
    # Create test wrestlers
    wrestler1 = create_test_wrestler("Aaron Spiers", "Talented")
    wrestler2 = create_test_wrestler("D-Lo Brown", "Regular")
    
    # Run the versus promo
    engine = VersusPromoEngine(wrestler1, wrestler2)
    result = engine.simulate()
    
    # Display the results with consistent formatting
    print(f"{wrestler1['name']} vs {wrestler2['name']}")
    print("=" * 40)
    print()
    
    # Process and display each beat
    for beat in result["beats"]:
        # Get commentary for the beat
        commentary = generate_commentary(beat)
        
        # Check if this is a special beat (intro or summary)
        if commentary.get("is_intro", False):
            print(f"{commentary['promo_line']}\n")
            continue
        
        if commentary.get("is_summary", False):
            print(f"\n{commentary['promo_line']}")
            continue
        
        # Display the beat with consistent formatting
        formatted_beat = format_promo_beat(beat, commentary)
        print(formatted_beat)
    
    # Display final scores
    scores = result["final_scores"]
    print("\nFinal Scores:")
    print(f"{wrestler1['name']}: {scores['wrestler1_score']:.1f}")
    print(f"{wrestler2['name']}: {scores['wrestler2_score']:.1f}")
    print(f"Overall Score: {scores['overall_score']:.1f}")
    
    # Determine winner
    if scores['wrestler1_score'] > scores['wrestler2_score'] + 5:
        print(f"\nWinner: {wrestler1['name']}")
    elif scores['wrestler2_score'] > scores['wrestler1_score'] + 5:
        print(f"\nWinner: {wrestler2['name']}")
    else:
        print("\nResult: The exchange was fairly even.")

if __name__ == "__main__":
    main() 