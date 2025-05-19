import sys
import os
import random
from collections import defaultdict
import statistics
from typing import Dict, List, Any

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
        "reputation": 23,
        "risk_taking": 24
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

def analyze_promo_lengths(wrestler: Dict[str, Any], num_promos: int = 30) -> Dict[str, Any]:
    """Run multiple promos and analyze their lengths."""
    lengths = []
    phase_transitions = defaultdict(list)  # Track when phases change
    
    converted_wrestler = convert_wrestler_format(wrestler)
    
    for _ in range(num_promos):
        engine = PromoEngine(wrestler=converted_wrestler)
        result = engine.simulate()
        
        # Record total length
        total_beats = len(result['beats'])
        lengths.append(total_beats)
        
        # Track phase changes
        current_phase = None
        for i, beat in enumerate(result['beats'], 1):
            phase = None
            if i <= 3:
                phase = "beginning"
            elif beat.get("commentary", "").startswith("End beat"):
                phase = "end"
            else:
                phase = "middle"
                
            if phase != current_phase:
                phase_transitions[phase].append(i)
                current_phase = phase
    
    # Calculate statistics
    stats = {
        "count": len(lengths),
        "mean_length": statistics.mean(lengths),
        "median_length": statistics.median(lengths),
        "std_dev": statistics.stdev(lengths),
        "min_length": min(lengths),
        "max_length": max(lengths),
        "length_distribution": defaultdict(int)
    }
    
    # Calculate length distribution
    for length in lengths:
        stats["length_distribution"][length] += 1
    
    # Calculate phase transition averages
    stats["phase_transitions"] = {
        phase: {
            "mean": statistics.mean(beats),
            "min": min(beats),
            "max": max(beats)
        }
        for phase, beats in phase_transitions.items()
    }
    
    return stats

def print_length_analysis(name: str, stats: Dict[str, Any]):
    """Pretty print the length analysis."""
    print(f"\n{name}")
    print("=" * len(name))
    print(f"Promo Length Analysis ({stats['count']} promos):")
    print(f"Mean Length: {stats['mean_length']:.1f} beats")
    print(f"Median Length: {stats['median_length']:.1f} beats")
    print(f"Standard Deviation: {stats['std_dev']:.1f} beats")
    print(f"Range: {stats['min_length']} - {stats['max_length']} beats")
    
    print("\nLength Distribution:")
    max_count = max(stats["length_distribution"].values())
    for length in sorted(stats["length_distribution"].keys()):
        count = stats["length_distribution"][length]
        percentage = (count / stats["count"]) * 100
        bar = "█" * int((count / max_count) * 20)  # Scale bar to max 20 chars
        print(f"{length:2d} beats: {percentage:5.1f}% {bar} ({count})")
    
    print("\nPhase Transitions:")
    for phase, data in stats["phase_transitions"].items():
        print(f"{phase.title():9} phase: {data['mean']:.1f} beats (range: {data['min']}-{data['max']})")

def run_length_tests():
    """Run length analysis tests for multiple wrestlers."""
    print("\nRunning promo length analysis...")
    
    # Test different types of wrestlers
    test_cases = [
        TEST_WRESTLERS[0],  # First wrestler
        TEST_WRESTLERS[1],  # Second wrestler
        TEST_WRESTLERS[2],  # Third wrestler
        TEST_WRESTLERS[3],  # Fourth wrestler
        TEST_WRESTLERS[4]   # Fifth wrestler
    ]
    
    for wrestler in test_cases:
        stats = analyze_promo_lengths(wrestler)
        print_length_analysis(wrestler["name"], stats)

if __name__ == "__main__":
    random.seed(42)  # For reproducible results
    run_length_tests() 