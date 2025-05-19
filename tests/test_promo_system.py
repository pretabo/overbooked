import sys
import os
import random
from collections import defaultdict
import json
from typing import Dict, List, Any

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from promo.promo_engine import PromoEngine
from db.wrestler_test_data import TEST_WRESTLERS

def extract_promo_relevant_stats(wrestler: Dict[str, Any]) -> Dict[str, int]:
    """Extract stats relevant to promos from a wrestler's attributes."""
    # Attribute indices based on the data structure
    STAT_INDICES = {
        "promo_delivery": 16,      # Promo Delivery
        "charisma": 17,           # Charisma
        "fan_engagement": 18,     # Fan Engagement
        "presence_under_fire": 19, # Presence Under Fire
        "confidence": 20,         # Confidence
        "determination": 21,      # Determination
        "focus": 22,             # Focus
        "reputation": 23         # Reputation
    }
    
    return {
        stat_name: wrestler["attributes"][idx]
        for stat_name, idx in STAT_INDICES.items()
    }

def convert_wrestler_format(wrestler: Dict[str, Any]) -> Dict[str, Any]:
    """Convert wrestler data to the format expected by the promo engine."""
    stats = extract_promo_relevant_stats(wrestler)
    return {
        "name": wrestler["name"],
        "attributes": stats
    }

def analyze_promo_performance(beats: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze detailed performance metrics from a promo."""
    analysis = {
        "confidence": {
            "min": float('inf'),
            "max": float('-inf'),
            "avg": 0,
            "dips": 0,
            "recoveries": 0
        },
        "momentum": {
            "min": float('inf'),
            "max": float('-inf'),
            "avg": 0,
            "cash_ins": 0
        },
        "scores": {
            "min": float('inf'),
            "max": float('-inf'),
            "avg": 0,
            "below_40": 0,
            "above_70": 0
        },
        "total_beats": len(beats)
    }
    
    prev_confidence = None
    in_dip = False
    total_confidence = 0
    total_momentum = 0
    total_score = 0
    
    for beat in beats:
        # Confidence analysis
        conf = beat["confidence"]
        analysis["confidence"]["min"] = min(analysis["confidence"]["min"], conf)
        analysis["confidence"]["max"] = max(analysis["confidence"]["max"], conf)
        total_confidence += conf
        
        if prev_confidence is not None:
            if prev_confidence > conf:
                in_dip = True
                analysis["confidence"]["dips"] += 1
            elif in_dip and conf > prev_confidence:
                analysis["confidence"]["recoveries"] += 1
                in_dip = False
        prev_confidence = conf
        
        # Momentum analysis
        mom = beat["momentum"]
        analysis["momentum"]["min"] = min(analysis["momentum"]["min"], mom)
        analysis["momentum"]["max"] = max(analysis["momentum"]["max"], mom)
        total_momentum += mom
        
        if beat.get("cash_in_used", False):
            analysis["momentum"]["cash_ins"] += 1
        
        # Score analysis
        score = beat["score"]
        analysis["scores"]["min"] = min(analysis["scores"]["min"], score)
        analysis["scores"]["max"] = max(analysis["scores"]["max"], score)
        total_score += score
        
        if score < 40:
            analysis["scores"]["below_40"] += 1
        if score > 70:
            analysis["scores"]["above_70"] += 1
    
    # Calculate averages
    analysis["confidence"]["avg"] = total_confidence / len(beats)
    analysis["momentum"]["avg"] = total_momentum / len(beats)
    analysis["scores"]["avg"] = total_score / len(beats)
    
    return analysis

def run_promo_tests(num_promos: int = 5) -> None:
    """Run comprehensive promo tests with real wrestler data."""
    results = defaultdict(list)
    
    print(f"\nRunning {num_promos} promos for each wrestler...")
    
    for wrestler in TEST_WRESTLERS[:5]:  # Test first 5 wrestlers
        name = wrestler["name"]
        stats = extract_promo_relevant_stats(wrestler)
        print(f"\nTesting {name}")
        print("Stats:", json.dumps(stats, indent=2))
        
        # Convert wrestler to expected format
        engine_wrestler = convert_wrestler_format(wrestler)
        
        for i in range(num_promos):
            engine = PromoEngine(engine_wrestler)
            result = engine.simulate()
            
            analysis = analyze_promo_performance(result["beats"])
            analysis["final_rating"] = result["final_rating"]
            results[name].append(analysis)
        
        # Calculate and display averages for this wrestler
        avg_results = {
            "final_ratings": [],
            "confidence_avg": [],
            "momentum_avg": [],
            "score_avg": [],
            "recoveries": [],
            "cash_ins": []
        }
        
        for run in results[name]:
            avg_results["final_ratings"].append(run["final_rating"])
            avg_results["confidence_avg"].append(run["confidence"]["avg"])
            avg_results["momentum_avg"].append(run["momentum"]["avg"])
            avg_results["score_avg"].append(run["scores"]["avg"])
            avg_results["recoveries"].append(run["confidence"]["recoveries"])
            avg_results["cash_ins"].append(run["momentum"]["cash_ins"])
        
        print("\nResults:")
        print(f"Final Rating: {sum(avg_results['final_ratings']) / len(avg_results['final_ratings']):.2f}")
        print(f"Avg Confidence: {sum(avg_results['confidence_avg']) / len(avg_results['confidence_avg']):.2f}")
        print(f"Avg Momentum: {sum(avg_results['momentum_avg']) / len(avg_results['momentum_avg']):.2f}")
        print(f"Avg Score: {sum(avg_results['score_avg']) / len(avg_results['score_avg']):.2f}")
        print(f"Avg Recoveries: {sum(avg_results['recoveries']) / len(avg_results['recoveries']):.2f}")
        print(f"Avg Cash-ins: {sum(avg_results['cash_ins']) / len(avg_results['cash_ins']):.2f}")
        
        # Show a detailed breakdown of one random promo
        print("\nDetailed Example Promo:")
        example = random.choice(results[name])
        print(json.dumps(example, indent=2))

if __name__ == "__main__":
    random.seed(42)  # For reproducible results
    run_promo_tests() 