import pytest
from statistics import mean
from .test_helpers import create_test_stats
from ..promo_engine_helpers import roll_promo_score

def create_test_stats(promo_delivery=10, confidence=10, resilience=10, pressure_handling=10):
    """Helper to create test wrestler stats"""
    return {
        "promo_delivery": promo_delivery,
        "confidence": confidence,
        "resilience": resilience,
        "pressure_handling": pressure_handling
    }

def test_lightning_in_bottle():
    """Test the lightning in a bottle mechanic"""
    def count_exceptional(stats, trials=100):
        exceptional_count = 0
        for _ in range(trials):
            score, exceptional = roll_promo_score(stats, 1, 50, 50, 50)  # Extract both score and exceptional info
            if exceptional:  # Check if we got an exceptional performance
                exceptional_count += 1
        return exceptional_count
    
    weak_stats = create_test_stats(5)
    strong_stats = create_test_stats(15)
    
    weak_count = count_exceptional(weak_stats)
    strong_count = count_exceptional(strong_stats)
    
    # Both should get some exceptional performances
    assert weak_count > 0, "Weak wrestlers should get some exceptional performances"
    assert strong_count > 0, "Strong wrestlers should get some exceptional performances"
    
    # Strong wrestlers should get more exceptional performances
    assert strong_count > weak_count, \
        f"Strong ({strong_count}) should get more exceptional performances than weak ({weak_count})"

def test_momentum_exceptional():
    """Test momentum's effect on exceptional performances"""
    def test_momentum_level(momentum, trials=100):
        stats = create_test_stats(10)  # Average wrestler
        exceptional_count = 0
        exceptional_quality = 0
        
        for _ in range(trials):
            _, exceptional = roll_promo_score(stats, 1, momentum, 50, 50)
            if exceptional:
                exceptional_count += 1
                exceptional_quality += exceptional["boost"]
        
        return exceptional_count, exceptional_quality / (exceptional_count or 1)
    
    low_count, low_quality = test_momentum_level(20)
    high_count, high_quality = test_momentum_level(80)
    
    # Higher momentum should increase exceptional chances moderately
    assert high_count >= low_count, \
        f"High momentum ({high_count}) should not reduce exceptional chances vs low ({low_count})"
    
    # The increase should be noticeable but not extreme
    increase_factor = high_count / (low_count or 1)
    assert 1.0 <= increase_factor <= 2.0, \
        f"Momentum effect on exceptional chance ({increase_factor:.1f}x) should be moderate"
    
    # Higher momentum should improve exceptional quality
    if high_count > 0 and low_count > 0:
        assert high_quality > low_quality, \
            f"High momentum ({high_quality:.1f}) should improve exceptional quality vs low ({low_quality:.1f})"

def test_confidence_exceptional():
    """Test confidence's effect on exceptional performances"""
    def test_confidence_level(confidence, trials=100):
        stats = create_test_stats(10)  # Average wrestler
        exceptional_count = 0
        exceptional_quality = 0
        regular_scores = []
        exceptional_scores = []

        for _ in range(trials):
            score, exceptional = roll_promo_score(stats, 1, 50, confidence, 50)
            if exceptional:
                exceptional_count += 1
                exceptional_quality += exceptional["boost"]
                exceptional_scores.append(score)
            else:
                regular_scores.append(score)

        return {
            "count": exceptional_count,
            "quality": exceptional_quality / (exceptional_count or 1),
            "regular_avg": mean(regular_scores) if regular_scores else 0,
            "exceptional_avg": mean(exceptional_scores) if exceptional_scores else 0
        }

    low = test_confidence_level(30)
    high = test_confidence_level(70)

    # Higher confidence should not drastically change exceptional frequency
    count_ratio = high["count"] / (low["count"] or 1)
    assert 0.5 <= count_ratio <= 2.0, \
        f"Confidence effect on frequency ({count_ratio:.1f}x) should be moderate"

    # Higher confidence should improve regular performance
    assert high["regular_avg"] > low["regular_avg"], \
        f"High confidence ({high['regular_avg']:.1f}) should improve regular performance vs low ({low['regular_avg']:.1f})"

    # Exceptional moments should be more impactful with high confidence
    if high["count"] > 0 and low["count"] > 0:
        high_impact = high["exceptional_avg"] - high["regular_avg"]
        low_impact = low["exceptional_avg"] - low["regular_avg"]
        assert high_impact > low_impact, \
            f"High confidence should increase exceptional impact"

def test_mental_exceptional():
    """Test mental stats' effect on exceptional performances"""
    def test_mental_level(mental_stats, trials=100):
        exceptional_types = {"crescendo": 0, "breakthrough": 0, "perfect_moment": 0, "crowd_pleaser": 0}
        
        for _ in range(trials):
            _, exceptional = roll_promo_score(mental_stats, 1, 50, 50, 50)  # Extract exceptional info
            if exceptional:
                exceptional_types[exceptional["type"]] += 1
        
        return exceptional_types
    
    weak_mental = create_test_stats(confidence=5, resilience=5, pressure_handling=5)
    strong_mental = create_test_stats(confidence=15, resilience=15, pressure_handling=15)
    
    weak_types = test_mental_level(weak_mental)
    strong_types = test_mental_level(strong_mental)
    
    # Strong mental should get more varied exceptional types
    weak_variety = sum(1 for count in weak_types.values() if count > 0)
    strong_variety = sum(1 for count in strong_types.values() if count > 0)
    
    assert strong_variety >= weak_variety, \
        f"Strong mental ({strong_variety}) should access more exceptional types than weak ({weak_variety})" 