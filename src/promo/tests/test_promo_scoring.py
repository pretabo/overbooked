import pytest
from promo.promo_engine_helpers import roll_promo_score
import random
from statistics import mean, stdev

@pytest.fixture
def mock_random():
    """Control randomness for testing"""
    random.seed(42)
    yield
    random.seed()

def create_test_stats(promo_delivery=10, focus=10):
    """Helper to create test wrestler stats"""
    return {
        "promo_delivery": promo_delivery,
        "focus": focus
    }

def test_base_score_range():
    """Test that base scores are properly scaled within expected ranges"""
    test_cases = [
        (5, 35),   # Weak wrestler (~35-40)
        (10, 55),  # Average wrestler (~55-60)
        (15, 75),  # Strong wrestler (~70-75)
        (20, 90),  # Elite wrestler (~90-95)
    ]
    
    for delivery, expected in test_cases:
        stats = create_test_stats(delivery)
        # Use neutral values for other parameters to isolate base score
        score, _ = roll_promo_score(stats, 1, 50, 50, 50)  # Extract score from tuple
        # Allow for some variance due to randomness
        assert abs(score - expected) < 20, \
            f"Base score for {delivery} skill should be close to {expected}"

def test_tiered_skill_scaling():
    """Test that skill scaling works correctly for different tiers"""
    def get_performance_stats(stats, trials=50):
        # Test both base performance and performance with bonuses
        base_scores = [roll_promo_score(stats, 1, 0, 50, 50)[0] for _ in range(trials)]
        bonus_scores = [roll_promo_score(stats, 1, 100, 100, 100)[0] for _ in range(trials)]
        
        return {
            "base_avg": mean(base_scores),
            "bonus_avg": mean(bonus_scores),
            "base_std": stdev(base_scores),
            "bonus_std": stdev(bonus_scores),
            "scaling": (mean(bonus_scores) - mean(base_scores)) / 100  # Normalize to get scaling factor
        }
    
    weak_stats = create_test_stats(5)
    avg_stats = create_test_stats(10)
    strong_stats = create_test_stats(15)
    
    weak = get_performance_stats(weak_stats)
    avg = get_performance_stats(avg_stats)
    strong = get_performance_stats(strong_stats)
    
    # Base performance should show clear progression
    assert strong["base_avg"] > avg["base_avg"] > weak["base_avg"], \
        "Base performance should increase with skill"
    
    # Each tier should have meaningful but not extreme differences
    weak_to_avg = avg["base_avg"] - weak["base_avg"]
    avg_to_strong = strong["base_avg"] - avg["base_avg"]
    
    assert 5 <= weak_to_avg <= 15, \
        f"Progression from weak to average ({weak_to_avg:.1f}) should be moderate"
    assert 5 <= avg_to_strong <= 15, \
        f"Progression from average to strong ({avg_to_strong:.1f}) should be moderate"
    
    # Scaling should improve with skill level
    assert 0.3 <= weak["scaling"] <= 0.6, \
        f"Weak scaling ({weak['scaling']:.2f}) outside expected range"
    assert 0.4 <= avg["scaling"] <= 0.7, \
        f"Average scaling ({avg['scaling']:.2f}) outside expected range"
    assert 0.5 <= strong["scaling"] <= 0.8, \
        f"Strong scaling ({strong['scaling']:.2f}) outside expected range"

def test_bonus_potential():
    """Test bonus potential and interaction between different bonus sources"""
    stats = create_test_stats(15)  # Use strong wrestler to test bonus ceiling
    
    def get_bonus_impact(base_score, **kwargs):
        # Get score with specific bonus active
        bonus_score, _ = roll_promo_score(stats, 1, 
            kwargs.get("momentum", 0),
            kwargs.get("confidence", 50),
            kwargs.get("crowd", 50)
        )
        return bonus_score - base_score
    
    # Get baseline score
    base_score, _ = roll_promo_score(stats, 1, 0, 50, 50)
    
    # Test individual bonuses
    conf_bonus = get_bonus_impact(base_score, confidence=100)
    crowd_bonus = get_bonus_impact(base_score, crowd=100)
    momentum_bonus = get_bonus_impact(base_score, momentum=100)
    
    # Individual bonuses should be meaningful but not overwhelming
    assert 5 <= conf_bonus <= 20, \
        f"Confidence bonus ({conf_bonus:.1f}) outside expected range"
    assert 5 <= crowd_bonus <= 15, \
        f"Crowd bonus ({crowd_bonus:.1f}) outside expected range"
    assert 5 <= momentum_bonus <= 15, \
        f"Momentum bonus ({momentum_bonus:.1f}) outside expected range"
    
    # Test combined bonuses
    all_bonus_score, _ = roll_promo_score(stats, 1, 100, 100, 100)
    total_bonus = all_bonus_score - base_score
    
    # Combined effect should be less than sum of individual bonuses
    individual_sum = conf_bonus + crowd_bonus + momentum_bonus
    assert total_bonus < individual_sum, \
        "Combined bonuses should have diminishing returns"
    
    # But combined effect should still be significant
    assert 15 <= total_bonus <= 40, \
        f"Total bonus potential ({total_bonus:.1f}) outside expected range"

def test_progressive_variance(mock_random):
    """Test that variance is controlled by focus and conditions"""
    # Test different focus levels
    low_focus = create_test_stats(focus=5)
    high_focus = create_test_stats(focus=15)

    def get_score_distribution(stats, conditions, trials=50):
        """Get score distribution under specific conditions
        conditions = (confidence, crowd, momentum)"""
        scores = [roll_promo_score(stats, 1, conditions[2], conditions[0], conditions[1])[0] 
                 for _ in range(trials)]
        return {
            "mean": mean(scores),
            "std": stdev(scores),
            "min": min(scores),
            "max": max(scores),
            "spread": max(scores) - min(scores)
        }

    # Test different conditions
    poor_cond = (30, 30, 30)    # (confidence, crowd, momentum)
    avg_cond = (50, 50, 50)
    good_cond = (70, 70, 70)

    # Test low focus wrestler
    low_focus_poor = get_score_distribution(low_focus, poor_cond)
    low_focus_avg = get_score_distribution(low_focus, avg_cond)
    low_focus_good = get_score_distribution(low_focus, good_cond)

    # Test high focus wrestler
    high_focus_poor = get_score_distribution(high_focus, poor_cond)
    high_focus_avg = get_score_distribution(high_focus, avg_cond)
    high_focus_good = get_score_distribution(high_focus, good_cond)

    # High focus should always have less variance than low focus
    for high, low in [(high_focus_poor, low_focus_poor), 
                      (high_focus_avg, low_focus_avg),
                      (high_focus_good, low_focus_good)]:
        assert high["std"] < low["std"], \
            f"High focus ({high['std']:.1f}) should have less variance than low focus ({low['std']:.1f})"

    # Better conditions should improve average performance for both
    for dist in [low_focus_poor, low_focus_avg, low_focus_good,
                 high_focus_poor, high_focus_avg, high_focus_good]:
        assert dist["spread"] >= 20, \
            f"Should maintain good performance spread ({dist['spread']:.1f})"

    # Variance ranges should be appropriate for focus levels
    for dist in [low_focus_poor, low_focus_avg, low_focus_good]:
        assert 12 <= dist["std"] <= 20, \
            f"Low focus variance ({dist['std']:.1f}) outside expected range"

    for dist in [high_focus_poor, high_focus_avg, high_focus_good]:
        assert 4 <= dist["std"] <= 10, \
            f"High focus variance ({dist['std']:.1f}) outside expected range"

    # Better conditions should improve minimum performance
    assert low_focus_good["min"] > low_focus_poor["min"], \
        "Better conditions should raise performance floor for low focus"
    assert high_focus_good["min"] > high_focus_poor["min"], \
        "Better conditions should raise performance floor for high focus"

def test_lightning_in_bottle(mock_random):
    """Test the special bonus chance mechanic"""
    weak_stats = create_test_stats(5)
    strong_stats = create_test_stats(15)
    
    def count_exceptional_scores(stats, trials=100):
        scores = [roll_promo_score(stats, 1, 50, 50, 50)[0] for _ in range(trials)]  # Extract score from tuple
        baseline = sum(scores) / len(scores)
        return sum(1 for score in scores if score > baseline + 15)
    
    weak_exceptions = count_exceptional_scores(weak_stats)
    strong_exceptions = count_exceptional_scores(strong_stats)
    
    # Should get roughly 5% exceptional performances
    assert 2 <= weak_exceptions <= 8, "Weak wrestlers should get some exceptional performances"
    assert 2 <= strong_exceptions <= 8, "Strong wrestlers should get some exceptional performances"
    assert weak_exceptions >= strong_exceptions, "Weak wrestlers should get larger bonuses"

def test_score_distribution():
    """Integration test to verify overall score distribution"""
    def get_score_distribution(stats, trials=100):
        scores = [roll_promo_score(stats, 1, 50, 50, 50)[0] for _ in range(trials)]  # Extract score from tuple
        return {
            "min": min(scores),
            "max": max(scores),
            "avg": sum(scores) / len(scores)
        }
    
    weak_dist = get_score_distribution(create_test_stats(5))
    avg_dist = get_score_distribution(create_test_stats(10))
    strong_dist = get_score_distribution(create_test_stats(15))
    
    # Check average score progression
    assert weak_dist["avg"] < avg_dist["avg"] < strong_dist["avg"], \
        "Average scores should increase with skill"
    
    # Check score ranges
    assert 30 <= weak_dist["avg"] <= 50, \
        f"Weak average ({weak_dist['avg']:.1f}) outside expected range"
    assert 50 <= avg_dist["avg"] <= 70, \
        f"Average average ({avg_dist['avg']:.1f}) outside expected range"
    assert 70 <= strong_dist["avg"] <= 90, \
        f"Strong average ({strong_dist['avg']:.1f}) outside expected range" 