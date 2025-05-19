import sys
import os
import random
from collections import defaultdict
import json
from typing import Dict, List, Any
import statistics

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from promo.promo_engine import PromoEngine
from db.wrestler_test_data import TEST_WRESTLERS

def extract_promo_relevant_stats(wrestler: Dict[str, Any]) -> Dict[str, int]:
    """Extract stats relevant to promos from a wrestler's attributes."""
    STAT_INDICES = {
        "promo_delivery": 16,
        "charisma": 17,
        "fan_engagement": 18,
        "presence_under_fire": 19,
        "confidence": 20,
        "determination": 21,
        "focus": 22,
        "reputation": 23
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

def analyze_score_distribution(scores: List[float]) -> Dict[str, Any]:
    """Analyze the distribution of promo scores."""
    if not scores:
        return {}
    
    # Basic statistics
    stats = {
        "count": len(scores),
        "mean": statistics.mean(scores),
        "median": statistics.median(scores),
        "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
        "min": min(scores),
        "max": max(scores)
    }
    
    # Score ranges
    ranges = {
        "0-20": 0,
        "21-40": 0,
        "41-60": 0,
        "61-80": 0,
        "81-90": 0,
        "91-95": 0,
        "96-100": 0
    }
    
    for score in scores:
        if score <= 20: ranges["0-20"] += 1
        elif score <= 40: ranges["21-40"] += 1
        elif score <= 60: ranges["41-60"] += 1
        elif score <= 80: ranges["61-80"] += 1
        elif score <= 90: ranges["81-90"] += 1
        elif score <= 95: ranges["91-95"] += 1
        else: ranges["96-100"] += 1
    
    # Convert to percentages
    stats["ranges"] = {k: (v / len(scores)) * 100 for k, v in ranges.items()}
    
    return stats

def run_distribution_tests(num_promos: int = 50) -> None:
    """Run many promos for each wrestler and analyze score distributions."""
    
    print(f"\nRunning {num_promos} promos for each wrestler...\n")
    print("=" * 80)
    
    for wrestler in TEST_WRESTLERS[:5]:  # Test first 5 wrestlers
        name = wrestler["name"]
        stats = extract_promo_relevant_stats(wrestler)
        
        print(f"\n{name}")
        print("-" * len(name))
        print("Stats:")
        for stat, value in stats.items():
            print(f"{stat:20}: {value}")
        
        # Run promos
        scores = []
        for _ in range(num_promos):
            engine = PromoEngine(convert_wrestler_format(wrestler))
            result = engine.simulate()
            scores.append(result["final_rating"])
        
        # Analyze distribution
        analysis = analyze_score_distribution(scores)
        
        print("\nScore Distribution:")
        print(f"Mean: {analysis['mean']:.2f}")
        print(f"Median: {analysis['median']:.2f}")
        print(f"Std Dev: {analysis['std_dev']:.2f}")
        print(f"Range: {analysis['min']:.2f} - {analysis['max']:.2f}")
        
        print("\nScore Ranges (% of promos):")
        for range_name, percentage in analysis["ranges"].items():
            bar = "█" * int(percentage / 2)  # Visual bar where each █ represents 2%
            print(f"{range_name:8}: {percentage:5.1f}% {bar}")
        
        print("\nRaw Scores (sorted):")
        sorted_scores = sorted(scores)
        # Print 5 scores per line
        for i in range(0, len(sorted_scores), 5):
            line = sorted_scores[i:i+5]
            print(" ".join(f"{score:5.1f}" for score in line))
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    random.seed(42)  # For reproducible results
    run_distribution_tests() 