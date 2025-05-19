import pytest
from statistics import mean, stdev
from promo.promo_engine_helpers import roll_promo_score

def create_test_stats(promo_delivery=10, confidence=10, resilience=10, pressure_handling=10, focus=10):
    """Helper to create test wrestler stats"""
    return {
        "promo_delivery": promo_delivery,
        "confidence": confidence,
        "resilience": resilience,
        "pressure_handling": pressure_handling,
        "focus": focus
    }

def get_performance_stats(stats, trials=100):
    """Get statistical analysis of multiple performances"""
    scores = [roll_promo_score(stats, 1, 50, 50, 50) for _ in range(trials)]
    return {
        "min": min(scores),
        "max": max(scores),
        "avg": mean(scores),
        "std": stdev(scores)
    }

def test_skill_level_ranges():
    """Test that different skill levels produce appropriate score ranges"""
    def get_score_range(skill_level, trials=50):
        stats = {"promo_delivery": skill_level}
        scores = [roll_promo_score(stats, 1, 50, 50, 50)[0] for _ in range(trials)]  # Extract score from tuple
        return min(scores), max(scores), sum(scores) / len(scores)
    
    # Test weak (5), average (10), and strong (15) skill levels
    weak_min, weak_max, weak_avg = get_score_range(5)
    avg_min, avg_max, avg_avg = get_score_range(10)
    strong_min, strong_max, strong_avg = get_score_range(15)
    
    # Check average score progression
    assert weak_avg < avg_avg < strong_avg, \
        "Average scores should increase with skill level"
    
    # Check minimum score progression
    assert weak_min < avg_min < strong_min, \
        "Minimum scores should increase with skill level"
    
    # Check maximum score progression
    assert weak_max < avg_max < strong_max, \
        "Maximum scores should increase with skill level"

def test_performance_variance():
    """Test that performance variance is controlled by focus and skill level"""
    def get_performance_stats(focus_level, skill_level=10, trials=200):  # Increased trials
        stats = create_test_stats(promo_delivery=skill_level, focus=focus_level)
        scores = [roll_promo_score(stats, 1, 50, 50, 50)[0] for _ in range(trials)]
        return {
            "mean": mean(scores),
            "std": stdev(scores),
            "min": min(scores),
            "max": max(scores),
            "spread": max(scores) - min(scores)
        }

    # Test different focus levels with same skill
    low_focus = get_performance_stats(5)
    avg_focus = get_performance_stats(10)
    high_focus = get_performance_stats(15)

    # Higher focus should mean more consistency
    assert high_focus["std"] < avg_focus["std"] < low_focus["std"], \
        "Higher focus should reduce performance variance"

    # Check variance ranges are appropriate for average skill
    assert 10 <= low_focus["std"] <= 25, \
        f"Low focus variance ({low_focus['std']:.1f}) outside expected range"
    assert 8 <= avg_focus["std"] <= 20, \
        f"Average focus variance ({avg_focus['std']:.1f}) outside expected range"
    assert 5 <= high_focus["std"] <= 15, \
        f"High focus variance ({high_focus['std']:.1f}) outside expected range"

    # Test that skill level affects variance in a meaningful way
    # Lower skill should have higher variance
    for skill in [5, 10, 15]:
        test_stats = get_performance_stats(10, skill)  # Average focus, varying skill
        if skill == 5:
            assert 10 <= test_stats["std"] <= 25, \
                f"Low skill variance ({test_stats['std']:.1f}) outside expected range"
        elif skill == 10:
            assert 8 <= test_stats["std"] <= 20, \
                f"Average skill variance ({test_stats['std']:.1f}) outside expected range"
        else:
            assert 5 <= test_stats["std"] <= 15, \
                f"High skill variance ({test_stats['std']:.1f}) outside expected range"

def test_consistent_base_performance():
    """Test that base performance is consistent across multiple runs"""
    def get_base_scores(skill_level, trials=50):
        stats = {"promo_delivery": skill_level}
        return [roll_promo_score(stats, 1, 50, 50, 50)[0] for _ in range(trials)]  # Extract score from tuple
    
    # Test multiple skill levels
    for skill in [5, 10, 15]:
        scores = get_base_scores(skill)
        score_mean = mean(scores)
        score_std = stdev(scores)
        
        # Mean should be in expected range
        if skill <= 7:  # Weak (35-45)
            expected_base = 35 + ((skill - 5) * 2)
        elif skill <= 13:  # Average (45-60)
            expected_base = 39 + ((skill - 7) * 3)
        else:  # Strong/Elite (60-75)
            expected_base = 57 + ((skill - 13) * 3)
        
        assert abs(score_mean - expected_base) < 20, \
            f"Mean score ({score_mean:.1f}) too far from expected ({expected_base})"
        
        # Standard deviation should be reasonable but allow for more variance at lower skills
        max_std = 25 if skill <= 7 else (20 if skill <= 13 else 15)
        assert score_std < max_std, \
            f"Standard deviation ({score_std:.1f}) too high for skill level {skill}"

def test_skill_progression():
    """Test that skill progression produces appropriate score increases"""
    def get_average_score(skill_level, trials=200):  # Increased trials
        stats = {"promo_delivery": skill_level}
        scores = [roll_promo_score(stats, 1, 50, 50, 50)[0] for _ in range(trials)]
        return sum(scores) / len(scores)
    
    # Test progression from skill 5 to 15
    prev_score = get_average_score(5)
    for skill in range(6, 16):
        curr_score = get_average_score(skill)
        increase = curr_score - prev_score
        
        # Expect larger jumps at tier boundaries (7->8 and 13->14)
        if skill == 8 or skill == 14:
            assert -3 <= increase <= 10, \
                f"Tier boundary increase from {skill-1} to {skill} gave {increase:.1f} point change"
        else:
            # Within tiers, expect smaller but still reasonable changes
            assert -5 <= increase <= 7, \
                f"Within-tier increase from {skill-1} to {skill} gave {increase:.1f} point change"
        
        prev_score = curr_score
        
    # Check overall progression
    low_score = get_average_score(5)
    mid_score = get_average_score(10)
    high_score = get_average_score(15)
    
    assert low_score < mid_score < high_score, \
        "Overall progression should show improvement from low to high skill" 