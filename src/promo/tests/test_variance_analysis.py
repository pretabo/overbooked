import pytest
from statistics import mean, stdev
from .test_helpers import create_test_stats
from ..promo_engine_helpers import roll_promo_score
from collections import defaultdict

def analyze_variance(focus_level, skill_level, trials=1000):  # Increased trials for better distribution
    """Analyze variance patterns for a specific focus/skill combination"""
    stats = create_test_stats(promo_delivery=skill_level, focus=focus_level)
    scores = [roll_promo_score(stats, 1, 50, 50, 50)[0] for _ in range(trials)]
    
    # Create histogram data
    buckets = defaultdict(int)
    bucket_size = 5  # 5-point buckets
    for score in scores:
        bucket = (score // bucket_size) * bucket_size
        buckets[bucket] += 1
    
    # Convert to percentage
    total = len(scores)
    histogram = {k: (v / total) * 100 for k, v in sorted(buckets.items())}
    
    return {
        "mean": mean(scores),
        "std": stdev(scores),
        "min": min(scores),
        "max": max(scores),
        "spread": max(scores) - min(scores),
        "histogram": histogram,
        "scores": sorted(scores)[:5] + ['...'] + sorted(scores)[-5:]  # Show extremes
    }

def print_histogram(histogram, title):
    """Print an ASCII histogram"""
    print(f"\n{title}")
    print("-" * 80)
    max_bar = 50  # Maximum bar length
    max_percent = max(histogram.values())
    
    for bucket, percent in histogram.items():
        bar_length = int((percent / max_percent) * max_bar)
        print(f"{bucket:3.0f}-{bucket+5:<3.0f} | {'#' * bar_length} ({percent:.1f}%)")

def test_detailed_variance_analysis():
    """Detailed analysis of variance patterns"""
    focus_levels = [5, 10, 15]  # Low, Medium, High focus
    skill_levels = [5, 10, 15]  # Low, Medium, High skill
    
    print("\nDetailed Variance Analysis:")
    print("=" * 80)
    
    for focus in focus_levels:
        print(f"\nFocus Level {focus}:")
        print("-" * 40)
        
        for skill in skill_levels:
            stats = analyze_variance(focus, skill)
            print(f"\nSkill Level {skill}:")
            print(f"  Mean Score: {stats['mean']:.1f}")
            print(f"  Std Dev: {stats['std']:.1f}")
            print(f"  Range: {stats['min']:.1f} - {stats['max']:.1f} (spread: {stats['spread']:.1f})")
            print_histogram(stats['histogram'], f"Score Distribution (Focus {focus}, Skill {skill})")
            
            # Basic assertions for debugging
            if focus == 5:  # Low focus
                assert 12 <= stats['std'] <= 20, f"Low focus variance ({stats['std']:.1f}) outside expected range"
            elif focus == 10:  # Medium focus
                assert 8 <= stats['std'] <= 15, f"Medium focus variance ({stats['std']:.1f}) outside expected range"
            else:  # High focus
                assert 4 <= stats['std'] <= 10, f"High focus variance ({stats['std']:.1f}) outside expected range"
                
            # Test for rough normality
            # In a normal distribution:
            # ~68% of values should be within 1 standard deviation
            # ~95% of values should be within 2 standard deviations
            within_1_std = sum(1 for s in stats['scores'] if abs(s - stats['mean']) <= stats['std'])
            within_2_std = sum(1 for s in stats['scores'] if abs(s - stats['mean']) <= 2 * stats['std'])
            
            # Allow some wiggle room in the percentages
            assert 0.60 <= within_1_std/len(stats['scores']) <= 0.75, \
                f"Distribution may not be normal (68% expected within 1 std dev)"
            assert 0.90 <= within_2_std/len(stats['scores']) <= 0.98, \
                f"Distribution may not be normal (95% expected within 2 std dev)"

def test_low_skill_scores():
    """Show 100 raw scores for a low focus, low skill wrestler"""
    stats = create_test_stats(promo_delivery=5, focus=5)
    scores = [roll_promo_score(stats, 1, 50, 50, 50)[0] for _ in range(100)]
    scores.sort()
    
    print("\nLow Skill (5), Low Focus (5) - 100 Promo Scores")
    print("=" * 80)
    print("\nStatistics:")
    print(f"Mean: {mean(scores):.1f}")
    print(f"Std Dev: {stdev(scores):.1f}")
    print(f"Range: {min(scores):.1f} - {max(scores):.1f}")
    print("\nAll Scores (sorted):")
    
    # Print scores in rows of 5 for readability
    for i in range(0, len(scores), 5):
        row = scores[i:i+5]
        print(f"{i+1:3d}-{i+5:3d}: " + " ".join(f"{score:6.1f}" for score in row)) 