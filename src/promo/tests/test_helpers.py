def create_test_stats(promo_delivery=10, confidence=10, resilience=10, pressure_handling=10, focus=10):
    """Helper to create test wrestler stats"""
    return {
        "promo_delivery": promo_delivery,
        "confidence": confidence,
        "resilience": resilience,
        "pressure_handling": pressure_handling,
        "focus": focus
    }

def create_test_wrestler(name, promo_delivery=10, confidence=10, resilience=10, pressure_handling=10, determination=10, risk_assessment=10):
    """Create a test wrestler with the given stats."""
    return {
        "name": name,
        "stats": create_test_stats(
            promo_delivery=promo_delivery,
            confidence=confidence,
            resilience=resilience,
            pressure_handling=pressure_handling,
            focus=10
        )
    } 