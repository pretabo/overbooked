import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from db.wrestler_test_data import TEST_WRESTLERS
from promo.promo_engine import PromoEngine

def convert_stats(wrestler):
    """Convert wrestler attributes to stats dictionary."""
    attrs = wrestler["attributes"]
    return {
        "promo_delivery": attrs[16],
        "fan_engagement": attrs[17],
        "entrance_presence": attrs[18],
        "presence_under_fire": attrs[19],
        "confidence": attrs[20],
        "focus": attrs[21],
        "resilience": attrs[22],
        "adaptability": attrs[23],
        "risk_assessment": attrs[24],
        "pressure_handling": attrs[25],
        "reputation": 10  # Default value
    }

def analyze_cash_ins(wrestler_name, trials=20):
    """Analyze cash-in patterns for a specific wrestler."""
    wrestler = next((w for w in TEST_WRESTLERS if w["name"] == wrestler_name), None)
    if not wrestler:
        return None
    
    # Convert wrestler data to proper format
    stats = convert_stats(wrestler)
    
    total_cash_ins = 0
    cash_in_beats = []
    promo_lengths = []
    
    for _ in range(trials):
        engine = PromoEngine(wrestler=stats, crowd_reaction=50)
        result = engine.simulate()
        
        # Count cash-ins and record when they happen
        promo_cash_ins = []
        for beat in result["beats"]:
            if beat.get("cash_in_used", False):
                promo_cash_ins.append(beat["beat_number"])
        
        total_cash_ins += len(promo_cash_ins)
        cash_in_beats.extend(promo_cash_ins)
        promo_lengths.append(len(result["beats"]))
    
    avg_promo_length = sum(promo_lengths) / len(promo_lengths)
    avg_cash_ins = total_cash_ins / trials
    
    print(f"\nAnalysis for {wrestler_name}:")
    print(f"Average cash-ins per promo: {avg_cash_ins:.1f}")
    print(f"Average promo length: {avg_promo_length:.1f} beats")
    if cash_in_beats:
        print(f"Cash-in beat numbers: {sorted(cash_in_beats)}")
        print(f"Most common cash-in beats: {sorted(set(cash_in_beats), key=cash_in_beats.count, reverse=True)[:3]}")

# Test with specific wrestlers
analyze_cash_ins("Benji Fellows")
analyze_cash_ins("Aaron Spiers") 