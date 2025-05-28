import pytest
from statistics import mean, stdev
from .test_helpers import create_test_stats
from ..promo_engine_helpers import roll_promo_score
from collections import defaultdict

def analyze_skill_level(skill_level, trials=1000):
    """Analyze performance patterns for a specific skill level"""
    stats = create_test_stats(promo_delivery=skill_level)
    scores = [roll_promo_score(stats, 1, 50, 50, 50)[0] for _ in range(trials)]
    
    # Create histogram data
    buckets = defaultdict(int)
    bucket_size = 5  # 5-point buckets
    for score in scores:
        bucket = (score // bucket_size) * bucket_size
        buckets[bucket] += 1
    
    # Calculate exceptional performance frequency
    exceptional_count = sum(1 for s in scores if s > 70)
    exceptional_ratio = (exceptional_count / trials) * 100
    
    # Find any score caps (repeated max values)
    sorted_scores = sorted(scores)
    potential_caps = []
    for i in range(len(sorted_scores)-5):
        if len(set(sorted_scores[i:i+5])) == 1:  # 5 identical scores
            potential_caps.append(sorted_scores[i])
    
    return {
        "mean": mean(scores),
        "std": stdev(scores),
        "min": min(scores),
        "max": max(scores),
        "histogram": {k: (v / trials) * 100 for k, v in sorted(buckets.items())},
        "exceptional_ratio": exceptional_ratio,
        "score_caps": potential_caps,
        "bottom_5": sorted_scores[:5],
        "top_5": sorted_scores[-5:]
    }

def print_histogram(histogram, title):
    """Print an ASCII histogram"""
    print(f"\n{title}")
    print("-" * 80)
    max_bar = 50  # Maximum bar length
    max_percent = max(histogram.values())
    
    for bucket, percent in sorted(histogram.items()):
        bar_length = int((percent / max_percent) * max_bar)
        print(f"{bucket:3.0f}-{bucket+5:<3.0f} | {'#' * bar_length} ({percent:.1f}%)")

def test_skill_distributions():
    """Analyze score distributions across different skill levels"""
    skill_levels = [5, 8, 10, 12, 15]  # Weak, Above Weak, Average, Below Strong, Strong
    
    print("\nSkill Level Distribution Analysis")
    print("=" * 80)
    
    for skill in skill_levels:
        stats = analyze_skill_level(skill)
        
        print(f"\nSkill Level {skill}:")
        print("-" * 40)
        print(f"Mean Score: {stats['mean']:.1f}")
        print(f"Std Dev: {stats['std']:.1f}")
        print(f"Range: {stats['min']:.1f} - {stats['max']:.1f}")
        print(f"Exceptional Rate: {stats['exceptional_ratio']:.1f}%")
        if stats['score_caps']:
            print(f"Score Caps Found: {stats['score_caps']}")
        print(f"Bottom 5 Scores: {[f'{s:.1f}' for s in stats['bottom_5']]}")
        print(f"Top 5 Scores: {[f'{s:.1f}' for s in stats['top_5']]}")
        
        print_histogram(stats['histogram'], "Score Distribution") 