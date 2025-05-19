import pytest
from promo.promo_engine_helpers import roll_promo_score

def analyze_wrestler_scores(skill_level, trials=1000):
    """Analyze score distribution for a given skill level"""
    stats = {"promo_delivery": skill_level}
    scores = [roll_promo_score(stats, 1, 50, 50, 50)[0] for _ in range(trials)]  # Extract score from tuple
    return {
        "min": min(scores),
        "max": max(scores),
        "avg": sum(scores) / len(scores),
        "std": (sum((x - (sum(scores) / len(scores))) ** 2 for x in scores) / len(scores)) ** 0.5
    }

def test_analyze_scores():
    """Print score analysis for different skill levels"""
    skill_levels = [5, 10, 15, 20]  # Weak, Average, Strong, Elite
    
    print("\nScore Analysis:")
    print("=" * 50)
    for skill in skill_levels:
        stats = analyze_wrestler_scores(skill)
        print(f"\nSkill Level {skill}:")
        print(f"  Average: {stats['avg']:.1f}")
        print(f"  Range: {stats['min']:.1f} - {stats['max']:.1f}")
        print(f"  Std Dev: {stats['std']:.1f}")
        
        # Basic assertions
        assert stats["min"] >= 0, "Scores should not be negative"
        assert stats["max"] <= 100, "Scores should not exceed 100"
        assert stats["std"] > 0, "Should have some variance" 