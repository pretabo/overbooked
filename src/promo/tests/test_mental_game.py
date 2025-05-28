import pytest
from statistics import mean, stdev
from .test_helpers import create_test_stats
from ..promo_engine_helpers import (
    roll_promo_score, calculate_confidence_decay,
    get_confidence_floor, calculate_confidence_shift,
    apply_confidence_shift
)

def create_test_stats(promo_delivery=10, confidence=10, resilience=10, pressure_handling=10):
    """Helper to create test wrestler stats"""
    return {
        "promo_delivery": promo_delivery,
        "confidence": confidence,
        "resilience": resilience,
        "pressure_handling": pressure_handling
    }

def test_confidence_decay():
    """Test that confidence decay works correctly"""
    # Test different resilience levels
    low_res = create_test_stats(resilience=5)
    high_res = create_test_stats(resilience=15)
    
    low_decay = calculate_confidence_decay(low_res)
    high_decay = calculate_confidence_decay(high_res)
    
    # Higher resilience should mean slower decay (less negative)
    assert low_decay < high_decay, "Higher resilience should mean slower confidence decay"
    
    # Test decay impact on performance
    scores_low = []
    scores_high = []
    confidence_low = 100
    confidence_high = 100
    
    # Run multiple trials to account for variance
    trials = 5
    low_changes = []
    high_changes = []
    
    for _ in range(trials):
        scores_low = []
        scores_high = []
        confidence_low = 100
        confidence_high = 100
        
        for _ in range(5):  # Simulate 5 beats
            score_low, _ = roll_promo_score(low_res, 1, 50, confidence_low, 50)
            score_high, _ = roll_promo_score(high_res, 1, 50, confidence_high, 50)
            scores_low.append(score_low)
            scores_high.append(score_high)
            confidence_low = max(get_confidence_floor(low_res), confidence_low + low_decay)
            confidence_high = max(get_confidence_floor(high_res), confidence_high + high_decay)
        
        # Track score changes (positive means improvement, negative means decline)
        low_changes.append(scores_low[-1] - scores_low[0])
        high_changes.append(scores_high[-1] - scores_high[0])
    
    # Calculate average changes
    avg_low_change = sum(low_changes) / len(low_changes)
    avg_high_change = sum(high_changes) / len(high_changes)
    
    # Low resilience should show score decline, high resilience might show improvement
    assert avg_low_change < 0, \
        f"Low resilience ({avg_low_change:.1f}) should show declining scores"
    assert avg_high_change > avg_low_change, \
        f"High resilience ({avg_high_change:.1f}) should perform better than low resilience ({avg_low_change:.1f})"

def test_mental_stability():
    """Test that mental stats affect performance appropriately"""
    unstable = create_test_stats(confidence=5, resilience=5, pressure_handling=5)
    stable = create_test_stats(confidence=15, resilience=15, pressure_handling=15)

    def get_performance_stats(stats, trials=50):
        scores = [roll_promo_score(stats, 1, 50, 50, 50)[0] for _ in range(trials)]
        return {
            "mean": mean(scores),
            "std": stdev(scores),
            "min": min(scores),
            "max": max(scores)
        }

    unstable_stats = get_performance_stats(unstable)
    stable_stats = get_performance_stats(stable)

    # Stable wrestlers should have better average performance
    assert stable_stats["mean"] > unstable_stats["mean"], \
        "Stable wrestlers should perform better on average"

    # Stable wrestlers should have a higher performance floor
    assert stable_stats["min"] > unstable_stats["min"], \
        "Stable wrestlers should have a higher minimum performance"

    # Stable wrestlers can still have variance, but it should be more controlled
    assert 0.5 <= stable_stats["std"] / unstable_stats["std"] <= 1.5, \
        "Stable wrestlers should have reasonable variance"

    # Stable wrestlers should have better peak performance
    assert stable_stats["max"] > unstable_stats["max"], \
        "Stable wrestlers should be capable of better peaks"

def test_confidence_floor():
    """Test that confidence has appropriate minimum levels based on stats"""
    test_cases = [
        (5, 12.5),   # Low confidence: 12.5-20 range
        (10, 20),    # Average confidence: 20-30 range
        (15, 27.5),  # High confidence: 27.5-40 range
    ]
    
    for conf_stat, min_expected in test_cases:
        stats = create_test_stats(confidence=conf_stat)
        floor = get_confidence_floor(stats)
        
        # Floor should be within reasonable range based on confidence stat
        assert min_expected <= floor <= min_expected * 1.5, \
            f"Confidence floor ({floor}) should be proportional to confidence stat {conf_stat}"
        
        # Test relative ordering of floors
        if conf_stat > 5:
            lower_stats = create_test_stats(confidence=conf_stat - 5)
            lower_floor = get_confidence_floor(lower_stats)
            assert floor > lower_floor, \
                f"Higher confidence ({conf_stat}) should have higher floor than lower confidence ({conf_stat - 5})"

def test_mental_recovery():
    """Test recovery from poor performances"""
    def simulate_recovery(stats, initial_confidence=30, beats=5, trials=10):
        all_scores = []
        for _ in range(trials):
            scores = []
            confidence = initial_confidence
            
            for _ in range(beats):
                score, _ = roll_promo_score(stats, 1, 50, confidence, 50)
                scores.append(score)
                # Simulate some confidence recovery
                confidence = min(100, confidence + 10)
            
            all_scores.append(scores)
        return all_scores
    
    good_mental = create_test_stats(confidence=15, resilience=15)
    poor_mental = create_test_stats(confidence=5, resilience=5)
    
    good_recoveries = simulate_recovery(good_mental)
    poor_recoveries = simulate_recovery(poor_mental)
    
    # Calculate average score changes
    good_changes = [scores[-1] - scores[0] for scores in good_recoveries]
    poor_changes = [scores[-1] - scores[0] for scores in poor_recoveries]
    
    avg_good_change = sum(good_changes) / len(good_changes)
    avg_poor_change = sum(poor_changes) / len(poor_changes)
    
    # Good mental stats should recover better than poor mental stats
    assert avg_good_change > avg_poor_change, \
        f"Good mental ({avg_good_change:.1f}) should recover better than poor mental ({avg_poor_change:.1f})"
    
    # At least some good mental trials should show improvement
    good_improvements = sum(1 for change in good_changes if change > 0)
    assert good_improvements >= len(good_changes) * 0.3, \
        f"Good mental should show improvement in at least 30% of trials (got {good_improvements}/{len(good_changes)})" 