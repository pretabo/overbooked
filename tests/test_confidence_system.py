import sys
import os
import random
from collections import defaultdict

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from promo.promo_engine import PromoEngine

def create_test_wrestler(promo_delivery, determination, name="Test Wrestler"):
    """Create a test wrestler with specific stats."""
    return {
        "name": name,
        "attributes": {
            "promo_delivery": promo_delivery,
            "determination": determination,
            "confidence": 10,
            "reputation": 10,
            "charisma": 10,
            "fan_engagement": 10
        }
    }

def analyze_confidence_patterns(beats):
    """Analyze confidence patterns from a promo."""
    confidence_stats = {
        "min": float('inf'),
        "max": float('-inf'),
        "avg": 0,
        "below_floor_count": 0,
        "recovery_count": 0  # Times confidence increased after dropping
    }
    
    prev_confidence = None
    total = 0
    in_dip = False
    
    for beat in beats:
        conf = beat["confidence"]
        confidence_stats["min"] = min(confidence_stats["min"], conf)
        confidence_stats["max"] = max(confidence_stats["max"], conf)
        total += conf
        
        if prev_confidence is not None:
            if prev_confidence > conf:
                in_dip = True
            elif in_dip and conf > prev_confidence:
                confidence_stats["recovery_count"] += 1
                in_dip = False
        
        prev_confidence = conf
    
    confidence_stats["avg"] = total / len(beats)
    return confidence_stats

def run_confidence_tests():
    """Run a series of tests on the confidence system."""
    
    # Test cases
    test_cases = [
        ("Weak Wrestler", 6, 8),      # Low skill, low determination
        ("Weak Determined", 6, 15),   # Low skill, high determination
        ("Average Wrestler", 10, 10),  # Average across the board
        ("Skilled Timid", 15, 6),     # High skill, low determination
        ("Elite Wrestler", 15, 15),   # High skill, high determination
    ]
    
    results = {}
    
    # Run multiple promos for each test case
    for name, promo_delivery, determination in test_cases:
        print(f"\nTesting {name}...")
        print(f"Promo Delivery: {promo_delivery}, Determination: {determination}")
        
        aggregated_stats = defaultdict(list)
        
        for _ in range(10):  # Run 10 promos per test case
            wrestler = create_test_wrestler(promo_delivery, determination, name)
            engine = PromoEngine(wrestler)
            result = engine.simulate()
            
            confidence_stats = analyze_confidence_patterns(result["beats"])
            
            for key, value in confidence_stats.items():
                aggregated_stats[key].append(value)
        
        # Calculate averages
        results[name] = {
            "min_confidence": sum(aggregated_stats["min"]) / 10,
            "max_confidence": sum(aggregated_stats["max"]) / 10,
            "avg_confidence": sum(aggregated_stats["avg"]) / 10,
            "recovery_rate": sum(aggregated_stats["recovery_count"]) / 10
        }
        
        print(f"Results for {name}:")
        print(f"Min Confidence: {results[name]['min_confidence']:.2f}")
        print(f"Max Confidence: {results[name]['max_confidence']:.2f}")
        print(f"Avg Confidence: {results[name]['avg_confidence']:.2f}")
        print(f"Average Recoveries: {results[name]['recovery_rate']:.2f}")

if __name__ == "__main__":
    random.seed(42)  # For reproducible results
    run_confidence_tests() 