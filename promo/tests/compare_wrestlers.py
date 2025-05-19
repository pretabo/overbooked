import sys
import os
import json
from statistics import mean, stdev
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from db.wrestler_test_data import TEST_WRESTLERS
from promo.promo_engine import PromoEngine

def find_wrestler(name):
    """Find a wrestler by name in the test data."""
    return next((w for w in TEST_WRESTLERS if w["name"] == name), None)

def analyze_promo_performance(beats):
    """Analyze detailed performance metrics from a promo."""
    scores = [b["score"] for b in beats]
    confidences = [b["confidence_level"] for b in beats]
    momentums = [b["momentum_meter"] for b in beats]
    
    return {
        "scores": {
            "min": min(scores),
            "max": max(scores),
            "avg": mean(scores),
            "std": stdev(scores) if len(scores) > 1 else 0
        },
        "confidence": {
            "min": min(confidences),
            "max": max(confidences),
            "avg": mean(confidences),
            "std": stdev(confidences) if len(confidences) > 1 else 0
        },
        "momentum": {
            "min": min(momentums),
            "max": max(momentums),
            "avg": mean(momentums),
            "std": stdev(momentums) if len(momentums) > 1 else 0
        },
        "exceptional_moves": sum(1 for b in beats if "exceptional" in b),
        "cash_ins": sum(1 for b in beats if b.get("cash_in_used", False)),
        "num_beats": len(beats)
    }

def compare_wrestlers(name1, name2, num_promos=10):
    """Compare two wrestlers over multiple promos."""
    w1 = find_wrestler(name1)
    w2 = find_wrestler(name2)
    
    if not w1 or not w2:
        print("Error: Could not find one or both wrestlers")
        return
    
    results = {name1: [], name2: []}
    
    for name, wrestler in [(name1, w1), (name2, w2)]:
        print(f"\nRunning {num_promos} promos for {name}")
        print("Key Stats:")
        print(f"Raw attributes: {wrestler['attributes']}")
        print(f"Promo Delivery: {wrestler['attributes'][16]}")
        print(f"Fan Engagement: {wrestler['attributes'][17]}")
        print(f"Entrance Presence: {wrestler['attributes'][18]}")
        print(f"Presence Under Fire: {wrestler['attributes'][19]}")
        print(f"Confidence: {wrestler['attributes'][20]}")
        print(f"Focus: {wrestler['attributes'][21]}")
        print(f"Resilience: {wrestler['attributes'][22]}")
        print(f"Adaptability: {wrestler['attributes'][23]}")
        print(f"Risk Assessment: {wrestler['attributes'][24]}")
        print(f"Determination: {wrestler['attributes'][27]}")
        print(f"Reputation: {wrestler['reputation']}")
        
        for i in range(num_promos):
            engine = PromoEngine({"attributes": {
                "promo_delivery": wrestler["attributes"][16],
                "fan_engagement": wrestler["attributes"][17],
                "entrance_presence": wrestler["attributes"][18],
                "presence_under_fire": wrestler["attributes"][19],
                "confidence": wrestler["attributes"][20],
                "focus": wrestler["attributes"][21],
                "resilience": wrestler["attributes"][22],
                "adaptability": wrestler["attributes"][23],
                "risk_assessment": wrestler["attributes"][24],
                "determination": wrestler["attributes"][27],
                "pressure_handling": wrestler["attributes"][19],  # Using presence_under_fire for pressure_handling
                "reputation": wrestler["reputation"]
            }})
            
            result = engine.simulate()
            analysis = analyze_promo_performance(result["beats"])
            analysis.update({
                "final_rating": result["final_rating"],
                "avg_score": result["avg_score"],
                "consistency_bonus": result["consistency_bonus"],
                "finish_bonus": result["finish_bonus"]
            })
            results[name].append(analysis)
    
    # Print comparison
    print("\nComparison Results:")
    print("=" * 50)
    
    for name in [name1, name2]:
        ratings = [r["final_rating"] for r in results[name]]
        scores = [r["avg_score"] for r in results[name]]
        consistency = [r["consistency_bonus"] for r in results[name]]
        finish = [r["finish_bonus"] for r in results[name]]
        exceptionals = [r["exceptional_moves"] for r in results[name]]
        cash_ins = [r["cash_ins"] for r in results[name]]
        
        print(f"\n{name}:")
        print(f"Final Ratings: {mean(ratings):.2f} ± {stdev(ratings):.2f}")
        print(f"Base Scores: {mean(scores):.2f} ± {stdev(scores):.2f}")
        print(f"Consistency Bonus: {mean(consistency):.2f} ± {stdev(consistency):.2f}")
        print(f"Finish Bonus: {mean(finish):.2f} ± {stdev(finish):.2f}")
        print(f"Exceptional Moves per Promo: {mean(exceptionals):.1f}")
        print(f"Momentum Cash-ins per Promo: {mean(cash_ins):.1f}")
        
        # Score distribution
        all_scores = []
        for r in results[name]:
            scores = r["scores"]
            all_scores.append(scores["min"])
            all_scores.append(scores["max"])
            all_scores.append(scores["avg"])
        
        ranges = [(0,40), (40,70), (70,85), (85,100)]
        print("\nScore Distribution:")
        for low, high in ranges:
            count = sum(1 for s in all_scores if low <= s < high)
            percentage = (count / len(all_scores)) * 100
            print(f"{low}-{high}: {percentage:.1f}%")

if __name__ == "__main__":
    compare_wrestlers("Benji Fellows", "Aaron Spiers", num_promos=20) 