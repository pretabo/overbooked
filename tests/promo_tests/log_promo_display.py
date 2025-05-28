#!/usr/bin/env python3
"""
Script to log versus promo display output to a file.
This helps us verify the formatting is consistent.
"""

import random
import sys
from promo.versus_promo_engine import VersusPromoEngine
from promo.custom_commentary_engine import fixed_generate_commentary

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

def format_versus_promo_for_display(versus_result, wrestler1, wrestler2):
    """Format a versus promo result into a structure for display."""
    display_beats = []
    
    # Add intro beat - explicitly mark as intro
    intro_beat = {
        "phase": "opening",
        "momentum": 0,
        "confidence": 50,
        "is_first_beat": True,
        "score": 0,
        "promo_line": f"{wrestler1['name']} and {wrestler2['name']} face off in the ring, microphones in hand.",
        "is_intro": True,
        "versus_mode": True
    }
    display_beats.append(intro_beat)
    
    # Process all the actual promo beats
    for beat in versus_result["beats"]:
        if "wrestler" not in beat or "promo_line" not in beat or beat.get("promo_line") is None:
            continue
            
        # Skip any summary lines or intro lines (we'll add our own)
        if isinstance(beat.get("promo_line"), str) and ("summary" in beat.get("promo_line", "").lower() or "face off" in beat.get("promo_line", "").lower()):
            continue
            
        # Determine momentum and confidence
        momentum = beat.get("momentum", 0)
        confidence = beat.get("confidence", 50)
        
        # Determine if this is wrestler1 or wrestler2 speaking
        is_wrestler1 = (beat.get("wrestler") == wrestler1)
        current_wrestler = wrestler1 if is_wrestler1 else wrestler2
        opponent = wrestler2 if is_wrestler1 else wrestler1
        
        # Create the display beat
        display_beat = {
            "phase": beat.get("phase", "middle"),
            "momentum": momentum,
            "confidence": confidence,
            "score": beat.get("score", 50),
            "promo_line": beat.get("promo_line", "..."),
            "wrestler": current_wrestler,
            "versus_mode": True,
            "opponent": opponent,
            "is_versus_beat": True,
            "wrestler_color": "#66CCFF" if is_wrestler1 else "#FF9966"
        }
        
        display_beats.append(display_beat)
    
    # Add summary beat - explicitly mark as summary
    scores = versus_result["final_scores"]
    winner_text = ""
    if scores['wrestler1_score'] > scores['wrestler2_score'] + 5:
        winner_text = f"{wrestler1['name']} won the verbal battle!"
    elif scores['wrestler2_score'] > scores['wrestler1_score'] + 5:
        winner_text = f"{wrestler2['name']} won the verbal battle!"
    else:
        winner_text = "The exchange was fairly even."
        
    summary_text = f"Versus Promo Complete. {wrestler1['name']}: {scores['wrestler1_score']:.1f} | {wrestler2['name']}: {scores['wrestler2_score']:.1f} | {winner_text}"
    
    summary_beat = {
        "phase": "ending",
        "momentum": 0,
        "confidence": 50,
        "is_last_beat": True,
        "score": versus_result["final_scores"]["overall_score"],
        "promo_line": summary_text,
        "final_quality": "good",  # Placeholder quality
        "is_summary": True,
        "versus_mode": True
    }
    display_beats.append(summary_beat)
    
    return display_beats

def format_beat_for_display(beat, commentary):
    """Format a beat for display with consistent formatting."""
    output = ""
    
    # Check if this is a special beat (intro or summary)
    if commentary.get("is_intro", False) or commentary.get("is_summary", False):
        output += f"{commentary['promo_line']}\n\n"
        return output
    
    # Get wrestler info and format the beat
    wrestler_name = beat.get("wrestler", {}).get("name", "Wrestler")
    promo_line = commentary["promo_line"]
    commentary_line = commentary.get("commentary_line", "")
    momentum = beat.get("momentum", 0)
    confidence = beat.get("confidence", 50)
    
    # Format according to the requested style
    output += f"{wrestler_name}: \n"
    output += f"'{promo_line}'. \n"
    
    if commentary_line:
        output += f"{commentary_line} \n"
    
    output += f"⚡ {momentum:.1f} | 💪 {confidence:.1f} \n\n"
    
    return output

def main():
    """Run a versus promo and log the display output to a file."""
    # Create test wrestlers
    wrestler1 = create_test_wrestler("Edge", "Talented")
    wrestler2 = create_test_wrestler("Grandmaster Sexay", "Regular")
    
    # Run the versus promo
    engine = VersusPromoEngine(wrestler1, wrestler2)
    result = engine.simulate()
    
    # Format the versus promo for display
    display_beats = format_versus_promo_for_display(result, wrestler1, wrestler2)
    
    # Format each beat and write to file
    with open("promo_display_log.txt", "w") as f:
        f.write(f"{wrestler1['name']} vs {wrestler2['name']}\n")
        f.write("=" * 40 + "\n\n")
        
        for beat in display_beats:
            commentary = fixed_generate_commentary(beat)
            formatted_beat = format_beat_for_display(beat, commentary)
            f.write(formatted_beat)
        
        # Write final scores
        scores = result["final_scores"]
        f.write("\nFinal Scores:\n")
        f.write(f"{wrestler1['name']}: {scores['wrestler1_score']:.1f}\n")
        f.write(f"{wrestler2['name']}: {scores['wrestler2_score']:.1f}\n")
        f.write(f"Overall Score: {scores['overall_score']:.1f}\n")
        
        # Determine winner
        if scores['wrestler1_score'] > scores['wrestler2_score'] + 5:
            f.write(f"\nWinner: {wrestler1['name']}\n")
        elif scores['wrestler2_score'] > scores['wrestler1_score'] + 5:
            f.write(f"\nWinner: {wrestler2['name']}\n")
        else:
            f.write("\nResult: The exchange was fairly even.\n")
    
    print(f"Promo display output logged to promo_display_log.txt")
    
    # Also print to console
    with open("promo_display_log.txt", "r") as f:
        print(f.read())

if __name__ == "__main__":
    main() 