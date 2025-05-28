import pytest
from promo.promo_engine_helpers import (
    roll_promo_score,
    get_momentum_gain,
    maybe_cash_in_momentum
)

def create_test_stats(promo_delivery=10, confidence=10, resilience=10, pressure_handling=10):
    """Helper to create test wrestler stats"""
    return {
        "promo_delivery": promo_delivery,
        "confidence": confidence,
        "resilience": resilience,
        "pressure_handling": pressure_handling
    }

def test_momentum_gain():
    """Test that momentum gain works correctly"""
    stats = create_test_stats(10)  # Average wrestler
    
    # Test momentum gain based on performance quality
    poor_gain = get_momentum_gain(30, stats["promo_delivery"])
    avg_gain = get_momentum_gain(55, stats["promo_delivery"])
    good_gain = get_momentum_gain(75, stats["promo_delivery"])
    
    assert poor_gain < avg_gain < good_gain, \
        "Better performances should generate more momentum"
    
    # Test relative performance bonus
    expected_score = stats["promo_delivery"] * 4
    overperform_gain = get_momentum_gain(expected_score + 10, stats["promo_delivery"])
    normal_gain = get_momentum_gain(expected_score, stats["promo_delivery"])
    
    assert overperform_gain > normal_gain, \
        "Exceeding expectations should give bonus momentum"

def test_momentum_cash_in():
    """Test momentum cash-in mechanics"""
    def simulate_cash_in(stats, trials=20):
        total_improvement = 0
        successful_cashes = 0
        
        for _ in range(trials):
            # Start with high momentum and medium confidence
            momentum = 80
            confidence = 50
            
            # Get baseline score
            base_score, _ = roll_promo_score(stats, 1, 0, confidence, 50)  # Extract score from tuple
            
            # Try to cash in momentum
            new_conf, new_mom, did_cash_in = maybe_cash_in_momentum(
                momentum, confidence, stats, 1
            )
            
            if did_cash_in:
                # Get score with cashed in momentum
                momentum_score, _ = roll_promo_score(stats, 1, new_mom, new_conf, 50)  # Extract score from tuple
                improvement = momentum_score - base_score
                total_improvement += improvement
                successful_cashes += 1
        
        return total_improvement / successful_cashes if successful_cashes > 0 else 0
    
    low_pressure = create_test_stats(pressure_handling=5)
    high_pressure = create_test_stats(pressure_handling=15)
    
    low_improvement = simulate_cash_in(low_pressure)
    high_improvement = simulate_cash_in(high_pressure)
    
    # High pressure handling should lead to more effective momentum usage
    assert high_improvement > low_improvement, \
        f"High pressure ({high_improvement:.1f}) should get more value from momentum than low pressure ({low_improvement:.1f})"

def test_momentum_strategy():
    """Test strategic momentum usage"""
    def simulate_promo(stats, strategy, beats=5):
        scores = []
        momentum = 50
        confidence = 50
        
        for beat in range(beats):
            # Early strategy: Cash in as soon as possible
            # Late strategy: Save for big moments
            should_cash_in = (
                (strategy == "early" and momentum >= 60) or
                (strategy == "late" and momentum >= 80) or
                (strategy == "adaptive" and (
                    momentum >= 90 or  # Always cash in at very high momentum
                    (momentum >= 70 and confidence <= 40) or  # Cash in when struggling
                    (momentum >= 60 and beat >= beats - 2)  # Cash in near the end
                ))
            )

            if should_cash_in:
                # Cash in momentum
                score, _ = roll_promo_score(stats, beat + 1, momentum, confidence, 50)
                momentum = 0  # Reset after cash-in
                confidence = min(100, confidence + 20)  # Boost confidence
            else:
                score, _ = roll_promo_score(stats, beat + 1, momentum, confidence, 50)
                # Gain momentum based on performance
                momentum = min(100, momentum + get_momentum_gain(score, stats["promo_delivery"]))
            
            scores.append(score)
        
        return sum(scores) / len(scores)
    
    stats = create_test_stats(10)
    
    # Test different strategies
    early_cash = simulate_promo(stats, "early")
    late_cash = simulate_promo(stats, "late")
    adaptive_cash = simulate_promo(stats, "adaptive")
    
    # Adaptive strategy should be most effective
    assert adaptive_cash >= early_cash, \
        f"Adaptive strategy ({adaptive_cash:.1f}) should be at least as good as early cash-in ({early_cash:.1f})"
    assert adaptive_cash >= late_cash, \
        f"Adaptive strategy ({adaptive_cash:.1f}) should be at least as good as late cash-in ({late_cash:.1f})"
    
    # Strategies should be reasonably balanced
    max_diff = max(adaptive_cash, early_cash, late_cash) - min(adaptive_cash, early_cash, late_cash)
    assert max_diff <= 15, \
        f"Strategy difference ({max_diff:.1f}) should not be too extreme"

def test_momentum_pressure_interaction():
    """Test how pressure handling affects momentum decisions"""
    low_pressure = create_test_stats(pressure_handling=5)
    high_pressure = create_test_stats(pressure_handling=15)
    
    def simulate_promo(stats, trials=10):
        cash_ins = 0
        for _ in range(trials):
            momentum = 50  # Start with some momentum
            confidence = 50
            
            # Simulate a 5-beat sequence
            for beat in range(5):
                score, _ = roll_promo_score(stats, beat + 1, momentum, confidence, 50)  # Extract score from tuple
                momentum_gain = get_momentum_gain(score, stats["promo_delivery"])
                
                # Check for cash-in
                new_conf, new_mom, did_cash_in = maybe_cash_in_momentum(
                    momentum + momentum_gain, confidence, stats, beat + 1
                )
                
                if did_cash_in:
                    cash_ins += 1
                    momentum = new_mom
                    confidence = new_conf
                else:
                    momentum = min(100, momentum + momentum_gain)
        
        return cash_ins
    
    # Run multiple trials to account for randomness
    low_cash_ins = [simulate_promo(low_pressure) for _ in range(5)]
    high_cash_ins = [simulate_promo(high_pressure) for _ in range(5)]
    
    avg_low = sum(low_cash_ins) / len(low_cash_ins)
    avg_high = sum(high_cash_ins) / len(high_cash_ins)
    
    # High pressure handling should lead to fewer but more strategic cash-ins
    assert avg_high < avg_low, \
        f"High pressure ({avg_high:.1f}) should cash in less often than low pressure ({avg_low:.1f})" 