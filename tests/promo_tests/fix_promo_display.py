#!/usr/bin/env python3
"""
Script to fix and test the versus promo formatting.
This script provides a consistent display format for all beats.
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

def fixed_generate_commentary(beat):
    """Enhanced version of generate_commentary that properly identifies beat types."""
    
    # Default values
    commentary = {
        'commentary_line': '',
        'score': beat.get('score', 50),
        'promo_line': beat.get('promo_line', ''),
        'is_intro': False,
        'is_summary': False,
        'is_cash_in': '🌟' in beat.get('promo_line', '')
    }
    
    # Only mark as intro if it's specifically an intro or has is_first_beat=True
    if beat.get('is_intro', False) or (beat.get('is_first_beat', False) and not beat.get('wrestler')):
        commentary['is_intro'] = True
        return commentary
        
    # Only mark as summary if it's specifically a summary or has is_last_beat=True
    if beat.get('is_summary', False) or (beat.get('is_last_beat', False) and not beat.get('wrestler')):
        commentary['is_summary'] = True
        return commentary
    
    # Get the score to determine commentary quality
    score = beat.get('score', 50)
    
    # Generate commentary based on score and phase
    phase = beat.get('phase', 'middle')
    
    # Commentary pool by score range
    commentary_pool = {
        'great': [
            "That was a devastating verbal assault!",
            "The audience is going wild for that exchange!",
            "What a brilliant counter-point!",
            "That's how you dominate a verbal confrontation!"
        ],
        'good': [
            "Strong response in this back-and-forth.",
            "The crowd is loving this exchange.",
            "That landed perfectly in this war of words.",
            "Gaining the upper hand in this verbal duel."
        ],
        'average': [
            "This back-and-forth continues.",
            "The verbal jousting continues.",
            "Trading words in the center of the ring.",
            "Neither one backing down in this exchange."
        ],
        'poor': [
            "That response didn't quite land.",
            "Losing ground in this exchange.",
            "The crowd expected a stronger comeback.",
            "Struggling to find the right words."
        ],
        'bad': [
            "Completely outmatched in this exchange.",
            "That verbal jab missed by a mile.",
            "The audience is cringing at that response.",
            "Dropping the ball in this confrontation."
        ]
    }
    
    # Determine quality category based on score
    if score >= 85:
        quality = 'great'
    elif score >= 70:
        quality = 'good'
    elif score >= 50:
        quality = 'average'
    elif score >= 30:
        quality = 'poor'
    else:
        quality = 'bad'
    
    # Select a random commentary line from the appropriate pool
    commentary['commentary_line'] = random.choice(commentary_pool[quality])
    
    return commentary

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
    print("\n========== VERSUS PROMO TEST (FIXED) ==========\n")
    
    # Create test wrestlers
    wrestler1 = create_test_wrestler("Edge", "Talented")
    wrestler2 = create_test_wrestler("Grandmaster Sexay", "Regular")
    
    # Run the versus promo
    engine = VersusPromoEngine(wrestler1, wrestler2)
    result = engine.simulate()
    
    # Display the results with consistent formatting
    print(f"{wrestler1['name']} vs {wrestler2['name']}")
    print("=" * 40)
    print()
    
    # Process and display each beat
    for i, beat in enumerate(result["beats"]):
        # Get commentary for the beat using our fixed function
        commentary = fixed_generate_commentary(beat)
        
        # Skip beats without wrestlers that aren't intro or summary
        if not beat.get("wrestler") and not commentary.get("is_intro") and not commentary.get("is_summary"):
            continue
        
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