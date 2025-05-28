import pytest
from promo.promo_engine import PromoEngine
import statistics

def create_test_wrestler(name, **stats):
    """Create a test wrestler with specified stats."""
    base_stats = {
        "promo_delivery": 10,
        "confidence": 10,
        "resilience": 10,
        "pressure_handling": 10,
        "risk_assessment": 10,
        "reputation": 10
    }
    base_stats.update(stats)
    return {"name": name, "attributes": base_stats}

def analyze_promo_performance(wrestler, trials=50):
    """Run multiple promos and analyze the results."""
    scores = []
    momentum_usage = []
    confidence_levels = []
    
    for _ in range(trials):
        engine = PromoEngine(wrestler=wrestler, crowd_reaction=50)
        result = engine.simulate()
        
        # Track scores
        scores.append(result["final_rating"])
        
        # Track momentum usage
        cash_ins = sum(1 for beat in result["beats"] if beat.get("cash_in_used", False))
        momentum_usage.append(cash_ins)
        
        # Track confidence levels
        confidence_levels.extend(beat["confidence_level"] for beat in result["beats"])
    
    return {
        "scores": {
            "min": min(scores),
            "max": max(scores),
            "avg": statistics.mean(scores),
            "std": statistics.stdev(scores)
        },
        "momentum": {
            "avg_cash_ins": statistics.mean(momentum_usage),
            "max_cash_ins": max(momentum_usage)
        },
        "confidence": {
            "min": min(confidence_levels),
            "max": max(confidence_levels),
            "avg": statistics.mean(confidence_levels)
        }
    }

def test_wrestler_configurations():
    """Test different wrestler configurations."""
    configs = {
        "weak_base": create_test_wrestler("Weak Base",
            promo_delivery=5, confidence=5, resilience=5,
            pressure_handling=5, risk_assessment=5),
        "weak_confident": create_test_wrestler("Weak Confident",
            promo_delivery=5, confidence=15, resilience=5,
            pressure_handling=5, risk_assessment=5),
        "weak_resilient": create_test_wrestler("Weak Resilient",
            promo_delivery=5, confidence=5, resilience=15,
            pressure_handling=5, risk_assessment=5),
        "weak_skilled": create_test_wrestler("Weak Skilled",
            promo_delivery=15, confidence=5, resilience=5,
            pressure_handling=5, risk_assessment=5),
        "average": create_test_wrestler("Average",
            promo_delivery=10, confidence=10, resilience=10,
            pressure_handling=10, risk_assessment=10),
        "strong": create_test_wrestler("Strong",
            promo_delivery=15, confidence=15, resilience=15,
            pressure_handling=15, risk_assessment=15)
    }
    
    results = {}
    for name, wrestler in configs.items():
        engine = PromoEngine(wrestler)
        engine.streak_info = {"count": 0, "quality": 0, "last_score": 0}  # Initialize streak info
        results[name] = engine.simulate()
    
    # Verify basic expectations
    assert results["strong"]["avg_score"] > results["average"]["avg_score"], \
        "Strong wrestler should outperform average"
    assert results["average"]["avg_score"] > results["weak_base"]["avg_score"], \
        "Average wrestler should outperform weak base"
    
    # Test mental stat effects
    assert results["weak_confident"]["avg_score"] > results["weak_base"]["avg_score"], \
        "High confidence should help weak wrestler"
    assert results["weak_resilient"]["avg_score"] > results["weak_base"]["avg_score"], \
        "High resilience should help weak wrestler"
    
    # Test skill vs mental balance
    skilled_avg = results["weak_skilled"]["avg_score"]
    confident_avg = results["weak_confident"]["avg_score"]
    assert abs(skilled_avg - confident_avg) < 10, \
        "Skill and mental stats should both be important"
    
    # Print analysis
    for name, result in results.items():
        print(f"\n{name.upper()} ANALYSIS:")
        print(f"Scores: {result['scores']}")
        print(f"Momentum usage: {result['momentum']}")
        print(f"Confidence levels: {result['confidence']}")
        
        # Basic assertions to ensure the system is working as intended
        if "weak" in name.lower():
            assert result["scores"]["avg"] < 50, f"{name} average score should be below 50"
            if "confident" in name.lower():
                assert result["confidence"]["avg"] > 40, f"{name} confidence should be above 40"
            if "resilient" in name.lower():
                assert result["confidence"]["min"] > 25, f"{name} min confidence should be above 25"
        elif "strong" in name.lower():
            assert result["scores"]["avg"] > 70, f"{name} average score should be above 70" 