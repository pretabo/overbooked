"""
Test module for the Versus Promo system.
This tests the ability of two wrestlers to engage in a promo battle.
"""

import sys
import os
import random
from collections import defaultdict
import json
import statistics
from typing import Dict, List, Any

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from promo.versus_promo_engine import VersusPromoEngine
from db.wrestler_test_data import TEST_WRESTLERS

def create_test_wrestler(name: str, archetype: str = "Regular") -> Dict[str, Any]:
    """Create a test wrestler with specified archetype."""
    attribute_sets = {
        "Weak": {
            "promo_delivery": random.randint(3, 6),
            "fan_engagement": random.randint(3, 6),
            "entrance_presence": random.randint(3, 6),
            "presence_under_fire": random.randint(3, 6),
            "confidence": random.randint(3, 6),
            "reputation": random.randint(3, 6),
            "focus": random.randint(3, 6),
            "determination": random.randint(3, 6)
        },
        "Regular": {
            "promo_delivery": random.randint(8, 12),
            "fan_engagement": random.randint(8, 12),
            "entrance_presence": random.randint(8, 12),
            "presence_under_fire": random.randint(8, 12),
            "confidence": random.randint(8, 12),
            "reputation": random.randint(8, 12),
            "focus": random.randint(8, 12),
            "determination": random.randint(8, 12)
        },
        "Talented": {
            "promo_delivery": random.randint(15, 20),
            "fan_engagement": random.randint(15, 20),
            "entrance_presence": random.randint(15, 20),
            "presence_under_fire": random.randint(15, 20),
            "confidence": random.randint(15, 20),
            "reputation": random.randint(15, 20),
            "focus": random.randint(15, 20),
            "determination": random.randint(15, 20)
        }
    }
    return {
        "id": random.randint(1000, 9999),
        "name": name,
        "attributes": attribute_sets[archetype]
    }

def analyze_versus_promo_performance(result: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the performance of a versus promo."""
    beats = result["beats"]
    final_scores = result["final_scores"]
    
    # Track individual wrestler performance
    wrestler1_beats = [b for b in beats if b.get("wrestler") == result["wrestler1"]]
    wrestler2_beats = [b for b in beats if b.get("wrestler") == result["wrestler2"]]
    
    # Filter out None values when calculating statistics
    wrestler1_scores = [b.get("score", 0) for b in wrestler1_beats if b.get("score") is not None]
    wrestler1_momentum = [b.get("momentum", 0) for b in wrestler1_beats if b.get("momentum") is not None]
    wrestler1_confidence = [b.get("confidence", 0) for b in wrestler1_beats if b.get("confidence") is not None]
    
    wrestler2_scores = [b.get("score", 0) for b in wrestler2_beats if b.get("score") is not None]
    wrestler2_momentum = [b.get("momentum", 0) for b in wrestler2_beats if b.get("momentum") is not None]
    wrestler2_confidence = [b.get("confidence", 0) for b in wrestler2_beats if b.get("confidence") is not None]
    
    return {
        "wrestler1": {
            "score": final_scores["wrestler1_score"],
            "beats": len(wrestler1_beats),
            "avg_score": statistics.mean(wrestler1_scores) if wrestler1_scores else 0,
            "momentum": statistics.mean(wrestler1_momentum) if wrestler1_momentum else 0,
            "confidence": statistics.mean(wrestler1_confidence) if wrestler1_confidence else 0
        },
        "wrestler2": {
            "score": final_scores["wrestler2_score"],
            "beats": len(wrestler2_beats),
            "avg_score": statistics.mean(wrestler2_scores) if wrestler2_scores else 0,
            "momentum": statistics.mean(wrestler2_momentum) if wrestler2_momentum else 0,
            "confidence": statistics.mean(wrestler2_confidence) if wrestler2_confidence else 0
        },
        "overall": {
            "score": final_scores["overall_score"],
            "competition_bonus": final_scores["competition_bonus"],
            "quality_bonus": final_scores["quality_bonus"]
        },
        "beats": beats  # Store the actual beats for detailed analysis
    }

def run_versus_promo_tests(num_promos: int = 5) -> None:
    """Run comprehensive tests for the versus promo system."""
    print(f"\nRunning {num_promos} versus promos...")
    
    # Test different wrestler combinations
    test_cases = [
        ("Weak vs Weak", "Weak", "Weak"),
        ("Weak vs Regular", "Weak", "Regular"),
        ("Weak vs Talented", "Weak", "Talented"),
        ("Regular vs Regular", "Regular", "Regular"),
        ("Regular vs Talented", "Regular", "Talented"),
        ("Talented vs Talented", "Talented", "Talented")
    ]
    
    results = defaultdict(list)
    
    for case_name, archetype1, archetype2 in test_cases:
        print(f"\nTesting {case_name}...")
        
        for i in range(num_promos):
            wrestler1 = create_test_wrestler(f"Wrestler A ({archetype1})", archetype1)
            wrestler2 = create_test_wrestler(f"Wrestler B ({archetype2})", archetype2)
            
            engine = VersusPromoEngine(wrestler1, wrestler2)
            result = engine.simulate()
            
            analysis = analyze_versus_promo_performance(result)
            results[case_name].append(analysis)
        
        # Calculate and display averages
        avg_results = {
            "wrestler1_score": [],
            "wrestler2_score": [],
            "overall_score": [],
            "competition_bonus": [],
            "quality_bonus": []
        }
        
        for run in results[case_name]:
            avg_results["wrestler1_score"].append(run["wrestler1"]["score"])
            avg_results["wrestler2_score"].append(run["wrestler2"]["score"])
            avg_results["overall_score"].append(run["overall"]["score"])
            avg_results["competition_bonus"].append(run["overall"]["competition_bonus"])
            avg_results["quality_bonus"].append(run["overall"]["quality_bonus"])
        
        print(f"\nResults for {case_name}:")
        print(f"Wrestler 1 Avg Score: {statistics.mean(avg_results['wrestler1_score']):.2f}")
        print(f"Wrestler 2 Avg Score: {statistics.mean(avg_results['wrestler2_score']):.2f}")
        print(f"Overall Avg Score: {statistics.mean(avg_results['overall_score']):.2f}")
        print(f"Avg Competition Bonus: {statistics.mean(avg_results['competition_bonus']):.2f}")
        print(f"Avg Quality Bonus: {statistics.mean(avg_results['quality_bonus']):.2f}")
        
        # Print some example promo lines
        print("\nExample Promo Lines:")
        last_result = results[case_name][-1]
        for beat in [b for b in last_result["beats"] if b.get("promo_line") and b.get("wrestler")]:
            # Only print the first 3 beats with a wrestler and promo line
            if beat.get("wrestler") and beat.get("promo_line"):
                wrestler_name = beat["wrestler"].get("name", "Unknown Wrestler")
                print(f"{wrestler_name}: {beat['promo_line']}")
            if len([b for b in last_result["beats"] if b.get("promo_line") and b.get("wrestler") and b in last_result["beats"][:last_result["beats"].index(beat)+1]]) >= 3:
                break
        
        # Print the summary line
        for beat in last_result["beats"]:
            if beat.get("is_last_beat") and beat.get("promo_line"):
                print(f"\nSummary: {beat['promo_line']}")
                break

def test_versus_promo_mechanics() -> bool:
    """Test specific mechanics of the versus promo system."""
    print("\nTesting versus promo mechanics...")
    
    all_passed = True
    
    # Test 1: Equal wrestlers should have close scores
    wrestler1 = create_test_wrestler("Equal Wrestler 1", "Regular")
    wrestler2 = create_test_wrestler("Equal Wrestler 2", "Regular")
    
    engine = VersusPromoEngine(wrestler1, wrestler2)
    result = engine.simulate()
    
    score_diff = abs(result["final_scores"]["wrestler1_score"] - 
                    result["final_scores"]["wrestler2_score"])
    if score_diff <= 15:
        print("✓ Test 1 passed: Equal wrestlers have relatively close scores")
    else:
        print(f"✗ Test 1 failed: Equal wrestlers had score difference of {score_diff}")
        all_passed = False
    
    # Test 2: Talented wrestler should outperform weak wrestler
    strong_wrestler = create_test_wrestler("Strong Wrestler", "Talented")
    weak_wrestler = create_test_wrestler("Weak Wrestler", "Weak")
    
    engine = VersusPromoEngine(strong_wrestler, weak_wrestler)
    result = engine.simulate()
    
    if result["final_scores"]["wrestler1_score"] > result["final_scores"]["wrestler2_score"]:
        print("✓ Test 2 passed: Talented wrestler outperformed weak wrestler")
    else:
        print("✗ Test 2 failed: Talented wrestler did not outperform weak wrestler")
        all_passed = False
    
    # Test 3: Competition bonus should be higher for close matches
    close_engine = VersusPromoEngine(wrestler1, wrestler2)
    close_result = close_engine.simulate()
    
    one_sided_engine = VersusPromoEngine(strong_wrestler, weak_wrestler)
    one_sided_result = one_sided_engine.simulate()
    
    if close_result["final_scores"]["competition_bonus"] >= one_sided_result["final_scores"]["competition_bonus"]:
        print("✓ Test 3 passed: Close matches received higher competition bonus")
    else:
        print("✗ Test 3 failed: Close matches did not receive higher competition bonus")
        all_passed = False
    
    # Test 4: Check for personalized promo lines
    test_engine = VersusPromoEngine(wrestler1, wrestler2)
    test_result = test_engine.simulate()
    
    personalized_lines = 0
    for beat in test_result["beats"]:
        if beat.get("promo_line") and (wrestler1["name"] in beat.get("promo_line", "") or wrestler2["name"] in beat.get("promo_line", "")):
            personalized_lines += 1
    
    if personalized_lines > 0:
        print(f"✓ Test 4 passed: Found {personalized_lines} personalized promo lines")
    else:
        print("✗ Test 4 failed: No personalized promo lines found")
        all_passed = False
    
    if all_passed:
        print("\nAll mechanics tests passed!")
    else:
        print("\nSome mechanics tests failed. See details above.")
    
    return all_passed

if __name__ == "__main__":
    run_versus_promo_tests()
    test_versus_promo_mechanics() 