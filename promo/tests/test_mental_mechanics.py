import pytest
from statistics import mean, stdev
from promo.promo_engine_helpers import (
    roll_promo_score,
    calculate_confidence_shift,
    apply_confidence_shift
)
from collections import defaultdict

def create_test_stats(**kwargs):
    """Create test stats with defaults."""
    base_stats = {
        "promo_delivery": 10,
        "confidence": 10,
        "resilience": 10,
        "pressure_handling": 10,
        "determination": 10
    }
    base_stats.update(kwargs)
    return base_stats

def test_mental_effectiveness():
    """Test that mental stats properly affect performance."""
    weak_mental = create_test_stats(confidence=5, resilience=5, pressure_handling=5)
    strong_mental = create_test_stats(confidence=15, resilience=15, pressure_handling=15)
    
    def get_performance_stats(stats, trials=50):
        scores = []
        for confidence in [30, 50, 70]:  # Test different confidence levels
            batch_scores = [
                roll_promo_score(stats, 1, 50, confidence, 50)[0]  # Extract score from tuple
                for _ in range(trials)
            ]
            scores.extend(batch_scores)
        return {
            "avg": mean(scores),
            "std": stdev(scores)
        }
    
    weak_stats = get_performance_stats(weak_mental)
    strong_stats = get_performance_stats(strong_mental)
    
    # Strong mental stats should lead to better average performance
    assert strong_stats["avg"] > weak_stats["avg"], \
        f"Strong mental ({strong_stats['avg']:.1f}) should outperform weak mental ({weak_stats['avg']:.1f})"
    
    # Strong mental stats should have less variance
    assert strong_stats["std"] < weak_stats["std"], \
        f"Strong mental ({strong_stats['std']:.1f}) should be more consistent than weak mental ({weak_stats['std']:.1f})"

def test_confidence_recovery():
    """Test the enhanced confidence recovery system."""
    weak_mental = create_test_stats(determination=5, resilience=5)
    strong_mental = create_test_stats(determination=15, resilience=15)
    
    def simulate_recovery(stats, initial_confidence=25, beats=5):
        confidence = initial_confidence
        shifts = []
        
        for _ in range(beats):
            score, _ = roll_promo_score(stats, 1, 50, confidence, 50)  # Extract score from tuple
            shift = calculate_confidence_shift(score, stats)
            confidence = apply_confidence_shift(confidence, shift, stats)
            shifts.append(confidence - initial_confidence)
        
        return max(shifts)  # Return maximum recovery amount
    
    # Test multiple times to account for randomness
    weak_recoveries = [simulate_recovery(weak_mental) for _ in range(10)]
    strong_recoveries = [simulate_recovery(strong_mental) for _ in range(10)]
    
    avg_weak = mean(weak_recoveries)
    avg_strong = mean(strong_recoveries)
    
    assert avg_strong > avg_weak * 1.3, \
        f"Strong mental ({avg_strong:.1f}) should recover significantly better than weak mental ({avg_weak:.1f})"

def test_mental_stability():
    """Test the enhanced variance and stability system."""
    unstable = create_test_stats(confidence=5, resilience=5, pressure_handling=5)
    stable = create_test_stats(confidence=15, resilience=15, pressure_handling=15)
    
    def measure_stability(stats, base_confidence=50, trials=50):
        scores = []
        for _ in range(trials):
            score, _ = roll_promo_score(stats, 1, 50, base_confidence, 50)  # Extract score from tuple
            scores.append(score)
        return stdev(scores)
    
    # Test stability at different performance levels
    def test_level(confidence):
        unstable_var = measure_stability(unstable, confidence)
        stable_var = measure_stability(stable, confidence)
        return unstable_var, stable_var
    
    # Test low, medium, and high confidence scenarios
    low_u, low_s = test_level(30)
    mid_u, mid_s = test_level(50)
    high_u, high_s = test_level(70)
    
    # Stable wrestlers should always have less variance
    assert low_s < low_u, "Stable should have less variance at low confidence"
    assert mid_s < mid_u, "Stable should have less variance at medium confidence"
    assert high_s < high_u, "Stable should have less variance at high confidence"
    
    # Variance difference should be most pronounced at extremes
    low_diff = low_u - low_s
    mid_diff = mid_u - mid_s
    assert low_diff > mid_diff, "Mental stability should matter more in difficult situations"

def test_exceptional_performances():
    """Test the enhanced lightning in a bottle system."""
    weak_mental = create_test_stats(confidence=5, resilience=5, pressure_handling=5)
    strong_mental = create_test_stats(confidence=15, resilience=15, pressure_handling=15)
    
    def count_exceptional(stats, trials=100):
        exceptional_count = 0
        exceptional_quality = 0
        all_scores = []
        
        for _ in range(trials):
            score, exceptional = roll_promo_score(stats, 1, 50, 50, 50)
            all_scores.append(score)
            if exceptional:  # Track when we get exceptional triggers
                exceptional_count += 1
                exceptional_quality += exceptional["boost"]
            if score > 85:  # Also track high scores
                exceptional_count += 1
                exceptional_quality += score - 85
        
        return exceptional_count, exceptional_quality / (exceptional_count or 1), mean(all_scores)
    
    # Run multiple trials
    weak_counts = [count_exceptional(weak_mental) for _ in range(5)]
    strong_counts = [count_exceptional(strong_mental) for _ in range(5)]
    
    # Average results
    weak_freq = mean(count for count, _, _ in weak_counts)
    weak_quality = mean(quality for _, quality, _ in weak_counts)
    weak_avg = mean(avg for _, _, avg in weak_counts)
    strong_freq = mean(count for count, _, _ in strong_counts)
    strong_quality = mean(quality for _, quality, _ in strong_counts)
    strong_avg = mean(avg for _, _, avg in strong_counts)
    
    print(f"\nWeak mental stats:")
    print(f"  Average score: {weak_avg:.1f}")
    print(f"  Exceptional frequency: {weak_freq:.1f}%")
    print(f"  Average boost: {weak_quality:.1f}")
    print(f"\nStrong mental stats:")
    print(f"  Average score: {strong_avg:.1f}")
    print(f"  Exceptional frequency: {strong_freq:.1f}%")
    print(f"  Average boost: {strong_quality:.1f}")
    
    # Strong mental should have more frequent and better exceptional performances
    assert strong_freq > weak_freq * 1.2, \
        f"Strong mental ({strong_freq:.1f}) should have more exceptional performances than weak mental ({weak_freq:.1f})"
    assert strong_quality > weak_quality if weak_quality > 0 else True, \
        f"Strong mental ({strong_quality:.1f}) should have better exceptional performances than weak mental ({weak_quality:.1f})"

def test_confidence_floor():
    """Test the dynamic confidence floor system."""
    weak_mental = create_test_stats(determination=5, resilience=5, promo_delivery=7)
    strong_mental = create_test_stats(determination=15, resilience=15, promo_delivery=7)
    
    def find_minimum_confidence(stats, trials=50):
        confidence = 50
        min_seen = 100
        
        for _ in range(trials):
            score = roll_promo_score(stats, 1, 0, confidence, 50)
            shift = calculate_confidence_shift(score, stats)
            confidence = apply_confidence_shift(confidence, shift, stats)
            min_seen = min(min_seen, confidence)
        
        return min_seen
    
    weak_floor = find_minimum_confidence(weak_mental)
    strong_floor = find_minimum_confidence(strong_mental)
    
    assert strong_floor > weak_floor + 5, \
        f"Strong mental ({strong_floor:.1f}) should have significantly higher floor than weak mental ({weak_floor:.1f})"

def test_mental_stability_variance():
    """Test that mental stats properly affect score variance."""
    def get_variance_stats(stats, trials=100):
        scores = [roll_promo_score(stats, 1, 50, 50, 50)[0] for _ in range(trials)]
        return {
            "std": stdev(scores),
            "range": max(scores) - min(scores)
        }
    
    # Test low vs high mental stats
    low_mental = create_test_stats(
        promo_delivery=10,
        confidence=5,
        resilience=5,
        pressure_handling=5
    )
    high_mental = create_test_stats(
        promo_delivery=10,
        confidence=15,
        resilience=15,
        pressure_handling=15
    )
    
    # Run multiple trials to ensure consistency
    low_trials = [get_variance_stats(low_mental) for _ in range(5)]
    high_trials = [get_variance_stats(high_mental) for _ in range(5)]
    
    # Average results
    low_std = mean(trial["std"] for trial in low_trials)
    high_std = mean(trial["std"] for trial in high_trials)
    low_range = mean(trial["range"] for trial in low_trials)
    high_range = mean(trial["range"] for trial in high_trials)
    
    # High mental stats should reduce variance
    assert high_std < low_std * 0.8, \
        f"High mental ({high_std:.1f}) should have less variance than low mental ({low_std:.1f})"
    assert high_range < low_range * 0.8, \
        f"High mental ({high_range:.1f}) should have smaller range than low mental ({low_range:.1f})"

def test_confidence_floor_mechanics():
    """Test that confidence floor mechanics work properly."""
    def get_floor_stats(stats, trials=50):
        current_confidence = 50
        floors = []
        for _ in range(trials):
            # Simulate a bad performance
            score = 30  # Consistently poor score
            shift = calculate_confidence_shift(score, stats)
            new_confidence = apply_confidence_shift(current_confidence, shift, stats)
            floors.append(new_confidence)
            current_confidence = new_confidence
        return min(floors)  # Should hit the floor
    
    # Test different mental stat combinations
    low_mental = create_test_stats(confidence=5, resilience=5, determination=5)
    mid_mental = create_test_stats(confidence=10, resilience=10, determination=10)
    high_mental = create_test_stats(confidence=15, resilience=15, determination=15)
    
    low_floor = get_floor_stats(low_mental)
    mid_floor = get_floor_stats(mid_mental)
    high_floor = get_floor_stats(high_mental)
    
    # Check floor progression
    assert low_floor < mid_floor < high_floor, \
        f"Confidence floors should increase with mental stats: {low_floor:.1f} < {mid_floor:.1f} < {high_floor:.1f}"
    
    # Check floor ranges
    assert 10 <= low_floor <= 20, f"Low mental floor ({low_floor:.1f}) outside expected range"
    assert 20 <= mid_floor <= 35, f"Mid mental floor ({mid_floor:.1f}) outside expected range"
    assert 30 <= high_floor <= 45, f"High mental floor ({high_floor:.1f}) outside expected range"

def test_exceptional_moment_types():
    """Test distribution and effectiveness of different exceptional moment types."""
    def count_moment_types(stats, trials=200):
        types = defaultdict(list)
        for _ in range(trials):
            # Test different conditions
            high_momentum = roll_promo_score(stats, 3, 80, 60, 50)[1]  # For crescendo
            low_confidence = roll_promo_score(stats, 2, 50, 30, 50)[1]  # For breakthrough
            perfect_setup = roll_promo_score(stats, 2, 60, 80, 50)[1]  # For perfect moment
            normal = roll_promo_score(stats, 2, 50, 50, 50)[1]  # For crowd pleaser
            
            # Record boost amounts for each type
            if high_momentum:
                types["crescendo"].append(high_momentum["boost"])
            if low_confidence:
                types["breakthrough"].append(low_confidence["boost"])
            if perfect_setup:
                types["perfect_moment"].append(perfect_setup["boost"])
            if normal:
                types["crowd_pleaser"].append(normal["boost"])
        
        return {
            type_name: {
                "count": len(boosts),
                "avg_boost": mean(boosts) if boosts else 0
            }
            for type_name, boosts in types.items()
        }
    
    # Test with different skill levels
    low_skill = create_test_stats(promo_delivery=7)
    high_skill = create_test_stats(promo_delivery=15)
    
    low_results = count_moment_types(low_skill)
    high_results = count_moment_types(high_skill)
    
    # High skill should get more varied types
    low_types = sum(1 for r in low_results.values() if r["count"] > 0)
    high_types = sum(1 for r in high_results.values() if r["count"] > 0)
    assert high_types >= low_types, \
        f"High skill ({high_types}) should access more moment types than low skill ({low_types})"
    
    # Check boost scaling
    for type_name in ["crescendo", "perfect_moment", "breakthrough", "crowd_pleaser"]:
        if low_results[type_name]["count"] > 0 and high_results[type_name]["count"] > 0:
            assert high_results[type_name]["avg_boost"] > low_results[type_name]["avg_boost"], \
                f"{type_name} boosts should scale with skill"

def test_exceptional_boost_scaling():
    """Test that exceptional boosts scale appropriately with current score."""
    def get_boost_at_score(stats, base_score, trials=50):
        boosts = []
        for _ in range(trials):
            # Force an exceptional performance by manipulating conditions
            score, exceptional = roll_promo_score(stats, 1, 100, 100, 50)
            if exceptional:
                boosts.append(exceptional["boost"])
        return mean(boosts) if boosts else 0
    
    stats = create_test_stats(promo_delivery=15)  # Use high skill to ensure exceptional triggers
    
    # Test boost scaling at different score levels
    low_score_boost = get_boost_at_score(stats, 50)
    mid_score_boost = get_boost_at_score(stats, 70)
    high_score_boost = get_boost_at_score(stats, 85)
    
    # Boosts should decrease as base score increases
    assert low_score_boost > mid_score_boost > high_score_boost, \
        f"Boosts should decrease with score: {low_score_boost:.1f} > {mid_score_boost:.1f} > {high_score_boost:.1f}" 