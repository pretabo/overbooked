from statistics import mean, stdev
from promo.promo_engine_helpers import roll_promo_score
from collections import defaultdict
import math

def normal_distribution_value(x, mu, sigma):
    """Calculate the expected frequency for a normal distribution"""
    return (1 / (sigma * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((x - mu) / sigma) ** 2)

def analyze_base_scores(skill_level, trials=500):
    """Get detailed stats for a given skill level"""
    stats = {"promo_delivery": skill_level}
    scores = [roll_promo_score(stats, 1, 50, 50, 50)[0] for _ in range(trials)]
    
    # Basic stats
    avg = mean(scores)
    std = stdev(scores)
    
    basic_stats = {
        "min": min(scores),
        "max": max(scores),
        "avg": avg,
        "std": std
    }
    
    # Score distribution in 5-point buckets
    buckets = defaultdict(int)
    for score in scores:
        bucket = int((score // 5) * 5)
        buckets[bucket] += 1
    
    # Calculate percentages and expected normal distribution
    distribution = {}
    for bucket, count in sorted(buckets.items()):
        percentage = (count/trials)*100
        # Calculate expected percentage for this bucket in a normal distribution
        bucket_mid = bucket + 2.5
        expected = normal_distribution_value(bucket_mid, avg, std) * 5 * 100  # Scale to percentage
        distribution[bucket] = {
            "actual": percentage,
            "expected": expected
        }
    
    basic_stats["distribution"] = distribution
    
    # Calculate scores within standard deviations
    within_1_sd = sum(1 for s in scores if abs(s - avg) <= std)
    within_2_sd = sum(1 for s in scores if abs(s - avg) <= 2*std)
    within_3_sd = sum(1 for s in scores if abs(s - avg) <= 3*std)
    
    basic_stats["within_1_sd"] = (within_1_sd/trials)*100
    basic_stats["within_2_sd"] = (within_2_sd/trials)*100
    basic_stats["within_3_sd"] = (within_3_sd/trials)*100
    
    # Calculate frequency of high scores
    high_scores = sum(1 for s in scores if s >= 85)
    very_high_scores = sum(1 for s in scores if s >= 95)
    perfect_scores = sum(1 for s in scores if s >= 99)
    basic_stats["high_score_freq"] = (high_scores/trials)*100
    basic_stats["very_high_score_freq"] = (very_high_scores/trials)*100
    basic_stats["perfect_score_freq"] = (perfect_scores/trials)*100
    
    return basic_stats

# Expected targets for each skill level
TARGETS = {
    # Jobber (3-5)
    3: {"avg": 35, "std": 6, "high": 0, "perfect": 0, "desc": "Complete Rookie"},
    5: {"avg": 40, "std": 7, "high": 0, "perfect": 0, "desc": "Improving Rookie"},
    
    # Lower Card (7-9)
    7: {"avg": 45, "std": 8, "high": 0.5, "perfect": 0, "desc": "Lower Card"},
    9: {"avg": 50, "std": 9, "high": 1, "perfect": 0, "desc": "Rising Talent"},
    
    # Mid Card (11-13)
    11: {"avg": 60, "std": 10, "high": 3, "perfect": 0, "desc": "Solid Midcarder"},
    13: {"avg": 65, "std": 11, "high": 5, "perfect": 0.1, "desc": "Upper Midcard"},
    
    # Main Event (15-17)
    15: {"avg": 70, "std": 12, "high": 8, "perfect": 0.3, "desc": "Main Eventer"},
    17: {"avg": 75, "std": 12, "high": 12, "perfect": 0.5, "desc": "Top Star"},
    
    # Elite (19-20)
    19: {"avg": 80, "std": 11, "high": 15, "perfect": 1, "desc": "Elite Performer"},
    20: {"avg": 85, "std": 10, "high": 20, "perfect": 2, "desc": "All-Time Great"}
}

# Test all skill levels
skill_levels = sorted(TARGETS.keys())
print("\nDetailed Score Distribution Analysis")
print("=" * 70)

for skill in skill_levels:
    target = TARGETS[skill]
    stats = analyze_base_scores(skill)
    print(f"\nSkill Level {skill} - {target['desc']}:")
    print(f"  Average Score: {stats['avg']:.1f} (Target: {target['avg']})")
    print(f"  Standard Dev: {stats['std']:.1f} (Target: {target['std']})")
    print(f"  Range: {stats['min']:.1f} - {stats['max']:.1f}")
    print(f"  Within 1 SD: {stats['within_1_sd']:.1f}% (Target: ~68%)")
    print(f"  Within 2 SD: {stats['within_2_sd']:.1f}% (Target: ~95%)")
    print(f"  Within 3 SD: {stats['within_3_sd']:.1f}% (Target: ~99.7%)")
    print(f"  Exceptional (≥85): {stats['high_score_freq']:.1f}% (Target: {target['high']}%)")
    print(f"  Perfect/Near-Perfect (≥99): {stats['perfect_score_freq']:.1f}% (Target: {target['perfect']}%)")
    
    print("\n  Score Distribution (Actual vs Expected):")
    print("  " + "-" * 60)
    for score, data in stats["distribution"].items():
        actual_bar = "#" * int(data["actual"])
        expected_bar = "." * int(data["expected"])
        print(f"  {score:3.0f}-{score+4:<3.0f} | {actual_bar}{'':.<20} ({data['actual']:.1f}%)")
        print(f"         | {expected_bar} ({data['expected']:.1f}%)")

def test_momentum_influence():
    """Test that momentum properly influences base scores."""
    def get_score_stats(skill_level, momentum, trials=100):
        stats = {"promo_delivery": skill_level}
        scores = [roll_promo_score(stats, 1, momentum, 50, 50)[0] for _ in range(trials)]
        return mean(scores)
    
    # Test different skill levels with varying momentum
    for skill in [5, 10, 15]:
        low_momentum = get_score_stats(skill, 20)
        normal_momentum = get_score_stats(skill, 50)
        high_momentum = get_score_stats(skill, 80)
        
        # Scores should increase with momentum
        momentum_effect = (high_momentum - low_momentum) / normal_momentum * 100
        
        # Effect should be noticeable but not overwhelming (5-15% range)
        assert 5 <= momentum_effect <= 15, \
            f"Momentum effect ({momentum_effect:.1f}%) should be moderate for skill {skill}"
        
        # Verify progression
        assert low_momentum < normal_momentum < high_momentum, \
            f"Scores should increase with momentum for skill {skill}"

def test_crowd_influence():
    """Test that crowd reaction properly influences base scores."""
    def get_score_stats(skill_level, crowd, trials=100):
        stats = {"promo_delivery": skill_level}
        scores = [roll_promo_score(stats, 1, 50, 50, crowd)[0] for _ in range(trials)]
        return mean(scores)
    
    # Test different skill levels with varying crowd reactions
    for skill in [5, 10, 15]:
        dead_crowd = get_score_stats(skill, 20)
        normal_crowd = get_score_stats(skill, 50)
        hot_crowd = get_score_stats(skill, 80)
        
        # Scores should increase with crowd reaction
        crowd_effect = (hot_crowd - dead_crowd) / normal_crowd * 100
        
        # Effect should be modest (3-10% range)
        assert 3 <= crowd_effect <= 10, \
            f"Crowd effect ({crowd_effect:.1f}%) should be modest for skill {skill}"
        
        # Verify progression
        assert dead_crowd < normal_crowd < hot_crowd, \
            f"Scores should increase with crowd reaction for skill {skill}"

def test_combined_influences():
    """Test that momentum, crowd, and confidence work together appropriately."""
    def get_score_stats(conditions, trials=100):
        stats = {"promo_delivery": 10}  # Use average wrestler
        scores = [roll_promo_score(
            stats, 
            1, 
            conditions["momentum"], 
            conditions["confidence"], 
            conditions["crowd"]
        )[0] for _ in range(trials)]
        return mean(scores)
    
    # Test various combinations
    worst_case = get_score_stats({"momentum": 20, "confidence": 20, "crowd": 20})
    neutral_case = get_score_stats({"momentum": 50, "confidence": 50, "crowd": 50})
    best_case = get_score_stats({"momentum": 80, "confidence": 80, "crowd": 80})
    
    # Calculate total effect range
    total_effect = (best_case - worst_case) / neutral_case * 100
    
    # Combined effect should be significant but not overwhelming (20-40% range)
    assert 20 <= total_effect <= 40, \
        f"Combined condition effect ({total_effect:.1f}%) should be balanced"
    
    # Test mixed conditions
    high_momentum_only = get_score_stats({"momentum": 80, "confidence": 50, "crowd": 50})
    high_confidence_only = get_score_stats({"momentum": 50, "confidence": 80, "crowd": 50})
    high_crowd_only = get_score_stats({"momentum": 50, "confidence": 50, "crowd": 80})
    
    # Individual effects should be smaller than combined
    assert (high_momentum_only - neutral_case) < (best_case - neutral_case), \
        "Combined boost should be larger than single factor"
    assert (high_confidence_only - neutral_case) < (best_case - neutral_case), \
        "Combined boost should be larger than single factor"
    assert (high_crowd_only - neutral_case) < (best_case - neutral_case), \
        "Combined boost should be larger than single factor" 