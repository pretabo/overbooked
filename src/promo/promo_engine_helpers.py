# promo_engine_helpers.py

import random

def extract_promo_stats(wrestler):
    return wrestler.get("attributes", {})

def normalize_confidence(stat):
    """Convert wrestler's base confidence (0-20) to initial promo confidence (0-100)."""
    base_confidence = 50
    confidence_mod = (stat - 10) * 2
    return min(100, max(20, base_confidence + confidence_mod))

def determine_reputation_tier(stats):
    reputation = stats.get("reputation", 10)
    if reputation < 6:
        return "jobber"
    elif reputation < 12:
        return "midcard"
    else:
        return "main_eventer"

def determine_max_promo_length(rep_score):
    if rep_score < 6:
        return 25
    elif rep_score < 12:
        return 35
    else:
        return 50

def should_start_end_phase(beat_number, max_beats, stats, momentum):
    """Determine if the promo should enter its end phase."""
    risk = stats.get("risk_taking", 10)
    focus = stats.get("focus", 10)
    
    # Base chance increases as we get closer to max length
    progress_ratio = beat_number / max_beats
    base_chance = progress_ratio * 0.4  # 0-40% chance based on progress
    
    # Risk takers are more likely to end early with high momentum
    momentum_factor = 0
    if momentum > 50:
        momentum_factor = ((momentum - 50) / 50) * (risk / 20)  # 0-50% extra chance based on momentum and risk
    
    # Focus reduces random endings
    focus_modifier = 1 - (focus / 20)  # Reduces chance by up to 50% based on focus
    
    # Combine factors
    end_chance = (base_chance + momentum_factor) * focus_modifier
    
    # Always end if we're very close to max length
    if beat_number >= max_beats - 3:
        return True
        
    # Random chance to end based on calculated probability
    return random.random() < end_chance

def get_momentum_gain(score, skill_level):
    """Calculate momentum gain based on performance."""
    # Base gain is smaller but more consistent
    if score < 40:
        base_gain = 1  # Even poor performances build some momentum
    elif score < 50:
        base_gain = 2  # Below average
    elif score < 60:
        base_gain = 3  # Average
    elif score < 70:
        base_gain = 4  # Good
    elif score < 80:
        base_gain = 5  # Excellent
    else:
        base_gain = 6  # Outstanding
    
    # Skill level provides a small bonus
    skill_factor = (skill_level / 20) ** 0.9  # Smoother curve
    
    # Bonus for exceeding expectations (increased impact)
    expected_score = 35 + (skill_level * 3)
    if score > expected_score:
        overperform_bonus = (score - expected_score) / 10  # Increased from /15 to /10
    else:
        overperform_bonus = 0
    
    # Calculate final gain with skill bonus and overperform bonus
    momentum_gain = (base_gain * (1 + skill_factor * 0.2)) + overperform_bonus
    
    # Extra bonus for exceptional scores
    if score >= 85:
        momentum_gain *= 1.5  # 50% bonus for exceptional performances
    
    return momentum_gain

def calculate_confidence_decay(stats):
    """Calculate confidence decay per beat."""
    resilience = stats.get("resilience", 10)
    determination = stats.get("determination", 10)
    
    # Base decay rate
    base_decay = -3.0
    
    # Mental stats reduce decay
    mental_factor = ((resilience + determination) / 40) ** 0.8
    
    # Calculate final decay
    return base_decay * (1 - mental_factor * 0.7)  # -3.0 to -0.9 range

def get_confidence_floor(stats):
    """Calculate minimum confidence level based on stats."""
    confidence_stat = stats.get("confidence", 10)
    resilience = stats.get("resilience", 10)
    determination = stats.get("determination", 10)
    
    # Base floor calculation with higher ranges
    if confidence_stat <= 7:  # Low confidence
        base_floor = 10 + (confidence_stat - 5) * 1.5  # 10-13 range
    elif confidence_stat <= 13:  # Average confidence
        base_floor = 15 + (confidence_stat - 7) * 2.0  # 15-27 range
    else:  # High confidence
        base_floor = 27 + (confidence_stat - 13) * 2.5  # 27-45 range
    
    # Mental stats provide additional floor (0-15 bonus)
    mental_bonus = ((resilience + determination) / 40) ** 0.7 * 15  # More aggressive scaling
    
    return max(5, min(45, base_floor + mental_bonus))

def calculate_confidence_shift(score_tuple, stats):
    """Calculate confidence change based on performance."""
    # Extract score from tuple
    score = score_tuple[0] if isinstance(score_tuple, tuple) else score_tuple
    
    # Get relevant stats
    resilience = stats.get("resilience", 10)
    determination = stats.get("determination", 10)
    promo_delivery = stats.get("promo_delivery", 10)
    
    # Calculate expected score range
    expected_low = 35 + (promo_delivery * 1.5)  # Lower bound
    expected_high = 45 + (promo_delivery * 2)  # Upper bound
    
    # Base shift calculation
    if score < expected_low:
        # Negative shift for underperforming
        base_shift = -15 + ((score - expected_low) / 3)
    elif score > expected_high:
        # Positive shift for overperforming
        base_shift = 8 + ((score - expected_high) / 4)
    else:
        # Small shift within expected range
        mid_point = (expected_low + expected_high) / 2
        base_shift = (score - mid_point) / 3
    
    # Mental stats affect shift magnitude with stronger impact
    mental_factor = ((resilience + determination) / 40) ** 0.7  # Less aggressive curve for smoother scaling
    
    # Apply mental factor with increased impact
    if base_shift < 0:
        # Mental stats help reduce negative shifts more significantly
        final_shift = base_shift * (1 - mental_factor * 1.0)  # Increased from 0.8 to 1.0
    else:
        # Mental stats enhance positive shifts more significantly
        final_shift = base_shift * (1 + mental_factor * 1.2)  # Increased from 0.6 to 1.2
    
    return final_shift

def apply_confidence_shift(current_confidence, shift, stats):
    """Apply confidence shift while respecting the minimum floor."""
    floor = get_confidence_floor(stats)
    new_confidence = current_confidence + shift
    
    # More aggressive recovery when near floor
    if new_confidence < floor:
        distance_from_floor = floor - new_confidence
        recovery_factor = 1 + (distance_from_floor / 20)  # Up to 3x recovery rate
        new_confidence = current_confidence + (shift * recovery_factor)
    
    return max(floor, min(100, new_confidence))

def calculate_exceptional_bonus(stats, current_score, momentum, confidence, beat_number, streak_info, exceptional_chance_mod=1.0):
    """Calculate chance and impact of exceptional performance."""
    # Base chance scales with skill and mental state
    promo_delivery = stats.get("promo_delivery", 10)
    confidence_stat = stats.get("confidence", 10)
    pressure_handling = stats.get("pressure_handling", 10)
    resilience = stats.get("resilience", 10)
    
    # Calculate skill modifier for thresholds
    skill_mod = (promo_delivery / 20) * 15  # 0-15 modifier based on skill
    
    # Calculate base chance (0.5-8% from skill)
    skill_chance = (promo_delivery / 20) ** 0.5  # More linear skill scaling
    base_chance = 0.5 + (skill_chance * 7.5)  # 0.5-8% base from skill
    
    # Calculate momentum factor (0.8-1.6x)
    momentum_factor = 0.8 + ((momentum / 100) * 0.8)  # Even stronger momentum impact
    
    # Calculate mental contribution (0-8%)
    mental_chance = ((confidence_stat + pressure_handling + resilience) / 60) ** 0.5  # More linear mental scaling
    mental_boost = mental_chance * 8.0  # 0-8% from mental stats
    
    # Calculate confidence boost (0-3%)
    confidence_ratio = (confidence - 40) / 60  # -0.67 to 1.0
    confidence_boost = max(0, confidence_ratio * 3.0)  # 0-3% from high confidence
    
    # Calculate final chance with mental stats affecting base chance
    mental_factor = ((confidence_stat + pressure_handling + resilience) / 60) ** 0.5  # More linear scaling
    base_with_mental = base_chance * (1 + mental_factor)  # Full mental influence on base
    
    # Apply momentum and add bonuses
    final_chance = (base_with_mental * momentum_factor) + (mental_boost * (1 + mental_factor * 0.7)) + confidence_boost
    
    # Apply chance modifier
    final_chance *= exceptional_chance_mod
    
    # Roll for exceptional performance
    if random.random() * 100 < final_chance:
        # Calculate boost amount (8-25 base boost)
        base_boost = 8 + (promo_delivery * 0.85)  # Increased skill scaling
        
        # Mental stats and conditions enhance boost
        mental_factor = ((confidence_stat + pressure_handling + resilience) / 60) ** 0.5  # More linear scaling
        condition_factor = ((momentum + confidence) / 200) ** 0.5  # More linear condition scaling
        
        # Calculate final boost with adjusted multipliers
        boost = base_boost * (1 + mental_factor * 0.7) * (1 + condition_factor * 0.5)
        
        # Score-based boost reduction
        if current_score > 70:
            reduction_curve = ((current_score - 70) / 30) ** 0.6  # Smoother reduction curve
            boost *= max(0.15, 1.0 - reduction_curve)  # More aggressive minimum
        
        # Calculate base boost for each type with mental scaling
        mental_bonus = (mental_factor * 0.3)  # 0-30% bonus from mental stats
        skill_bonus = (promo_delivery / 20)  # 0-100% bonus from skill
        base_boosts = {
            "crescendo": boost * (1.0 + skill_bonus * 2.5),  # 100-350% for crescendo
            "breakthrough": boost * (0.7 + mental_bonus * 1.5),  # 70-120% for breakthrough
            "perfect_moment": boost * (0.9 + skill_bonus * 1.2),  # 90-210% for perfect
            "crowd_pleaser": boost * (0.8 + skill_bonus * 0.6)  # 80-140% for crowd pleaser
        }
        
        # Determine type and apply type-specific boost
        if beat_number >= 3 and momentum >= (75 - skill_mod):  # Harder crescendo baseline, more skill impact
            type = "crescendo"
            momentum_cost = momentum * 0.5  # Reduced from 0.7
            boost = base_boosts["crescendo"]
        elif confidence <= (35 + skill_mod):  # Lower breakthrough threshold, more skill impact
            type = "breakthrough"
            momentum_cost = momentum * 0.2  # Reduced from 0.3
            boost = base_boosts["breakthrough"]
        elif confidence >= (75 - skill_mod) and momentum >= (55 - skill_mod):  # Harder perfect moment, more skill impact
            type = "perfect_moment"
            momentum_cost = momentum * 0.3  # Reduced from 0.5
            boost = base_boosts["perfect_moment"]
        else:
            type = "crowd_pleaser"
            momentum_cost = momentum * 0.25  # Reduced from 0.4
            boost = base_boosts["crowd_pleaser"]
        
        # Final score-based reduction
        if current_score > 70:
            reduction = ((current_score - 70) / 30) ** 0.5  # Smoother reduction curve
            boost *= max(0.2, 1.0 - reduction)  # Less aggressive minimum
        
        # Apply final boost cap based on current score
        max_boost = 40 - ((current_score - 50) / 50) * 25  # 40 at score 50, 15 at score 100
        boost = min(boost, max_boost)
        
        return {
            "boost": boost,
            "type": type,
            "momentum_cost": momentum_cost
        }
    
    return None

def roll_promo_score(stats, beat_number, momentum, confidence, crowd_reaction, streak_info=None):
    """Calculate promo score with balanced variance and achievable excellence."""
    promo_delivery = stats.get("promo_delivery", 10)
    confidence_stat = stats.get("confidence", 10)
    resilience = stats.get("resilience", 10)
    pressure_handling = stats.get("pressure_handling", 10)
    
    # Calculate mental profile with weighted importance
    mental_stats = {
        "confidence": confidence_stat * 1.0,  # Reduced confidence weight
        "resilience": resilience * 1.2,      # Increased resilience importance
        "pressure": pressure_handling * 1.0   # Baseline pressure handling
    }
    mental_average = sum(mental_stats.values()) / (1.0 + 1.2 + 1.0)
    
    # Base score calculation with wider ranges and smoother progression
    if promo_delivery <= 7:  # Weak (25-35)
        base = 25 + ((promo_delivery - 5) * 2.5)  # 2.5 points per level
    elif promo_delivery <= 13:  # Average (35-50)
        base = 35 + ((promo_delivery - 7) * 2.5)  # 2.5 points per level
    else:  # Strong/Elite (50-60)
        base = 50 + ((promo_delivery - 13) * 1.5)  # Further reduced scaling at high levels
    
    # Calculate effective skill with stronger mental influence
    mental_factor = (mental_average / 20) ** 0.7  # Slightly reduced mental impact
    effective_skill = (promo_delivery * 0.6) + (mental_average * 0.4 * mental_factor)  # More weight on skill
    
    # Calculate skill scaling with more balanced ranges
    if effective_skill <= 7:  # Weak
        skill_scale = 0.2 + ((effective_skill / 7) * 0.2)  # 0.2-0.4
    elif effective_skill <= 13:  # Average
        skill_scale = 0.4 + (((effective_skill - 7) / 6) * 0.2)  # 0.4-0.6
    else:  # Strong
        skill_scale = 0.6 + (((effective_skill - 13) / 7) * 0.15)  # 0.6-0.75
    
    # Calculate actual bonus based on inputs with balanced impact
    confidence_ratio = (confidence / 100) ** 0.8  # More dampening
    crowd_ratio = (crowd_reaction / 100) ** 0.9  # More dampening for crowd
    momentum_ratio = (momentum / 100) ** 0.85  # More dampening for momentum
    
    # Calculate current score with balanced multipliers
    current_score = base * (
        1.0 +  # Base
        (skill_scale * 0.25) +  # Skill contribution (max +25%)
        (confidence_ratio * 0.15) +  # Confidence contribution (max +15%)
        (crowd_ratio * 0.10) +  # Crowd contribution (max +10%)
        (momentum_ratio * 0.15)  # Momentum contribution (max +15%)
    )
    
    # Apply additional scaling for low skill levels
    if promo_delivery <= 10:
        # Increase influence of external factors for low skill wrestlers
        low_skill_factor = (10 - promo_delivery) / 10  # 0-1 scale based on how low skill is
        current_score *= (1.0 + (crowd_ratio * 0.10 * low_skill_factor) + (momentum_ratio * 0.10 * low_skill_factor))
    
    # Calculate mental stability (0.5-1.0 range)
    mental_stability = (resilience + pressure_handling) / 40  # 0.5-1.0 scale
    
    # Calculate base variance based on mental stability
    base_variance = 20 * (2.0 - mental_stability)  # Higher base variance (20-40 range)
    
    # Calculate final variance with stronger mental influence
    if current_score < 40:
        # More variance when struggling
        struggle_factor = (40 - current_score) / 40  # 0-1 scale based on how much they're struggling
        variance = base_variance * (1.0 + struggle_factor)  # Double variance when struggling
    elif current_score > 80:
        # More variance at very high scores
        high_score_factor = (current_score - 80) / 20  # 0-1 scale for scores 80-100
        variance = base_variance * (1.0 + high_score_factor)  # Double variance at high scores
    else:
        # Normal variance in middle range
        variance = base_variance
    
    # Apply randomness with score-based scaling
    randomness = random.uniform(-variance, variance)
    if current_score > 70:
        # Reduce randomness at high scores but not as aggressively
        score_factor = max(0.5, 1.0 - ((current_score - 70) / 40))  # Less aggressive reduction
        randomness *= score_factor
    
    # Check for exceptional performance with score-based chance reduction
    exceptional_chance_mod = 1.0
    if current_score > 70:
        exceptional_chance_mod = max(0.5, 1.0 - ((current_score - 70) / 40))  # Less aggressive reduction
    
    # Calculate final score before exceptional
    final_score = current_score + randomness
    
    # Get exceptional performance if any
    exceptional = calculate_exceptional_bonus(
        stats, final_score, momentum, confidence, 
        beat_number, streak_info,
        exceptional_chance_mod  # Pass the modifier to the function
    )
    
    # Apply exceptional boost if any
    if exceptional:
        final_score += exceptional["boost"]
    
    # Apply final score cap
    final_score = max(0, min(99, final_score))
    
    return final_score, exceptional

def determine_line_quality(stats, score):
    if score >= 98:
        return "perfect"
    elif score >= 85:
        return "excellent"
    elif score >= 70:
        return "good"
    elif score >= 40:
        return "neutral"
    elif score >= 20:
        return "bad"
    elif score >= 10:
        return "terrible"
    else:
        return "flop"

def generate_beginning_beat(stats, beat_number, momentum, confidence, crowd_reaction):
    """Generate opening beat with streak tracking."""
    score, exceptional = roll_promo_score(stats, beat_number, momentum, confidence, crowd_reaction)
    quality = determine_line_quality(stats, score)
    
    # Calculate momentum gain
    momentum_gain = get_momentum_gain(score, stats.get("promo_delivery", 10))
    
    # Initialize streak info
    streak_info = {"count": 0, "quality": 0, "last_score": score}
    
    # Calculate confidence decay
    confidence_decay = calculate_confidence_decay(stats)
    new_confidence = max(get_confidence_floor(stats), min(100, confidence + confidence_decay))
    
    beat_data = {
        "beat_number": beat_number,
        "commentary": f"Opening beat {beat_number}",
        "score": score,
        "line_quality": quality,
        "momentum_change": momentum_gain,
        "confidence_shift": confidence_decay,
        "momentum_meter": momentum,
        "confidence_level": confidence,
        "momentum": momentum + momentum_gain,
        "confidence": new_confidence,
        "streak_info": streak_info
    }
    
    if exceptional:
        beat_data["exceptional"] = {
            "type": exceptional["type"],
            "boost": exceptional["boost"]
        }
    
    return beat_data

def generate_regular_beat(stats, beat_number, momentum, confidence, crowd_reaction, streak_info=None):
    """Generate a regular beat with streak tracking."""
    score, exceptional = roll_promo_score(
        stats, beat_number, momentum, confidence, 
        crowd_reaction, streak_info
    )
    quality = determine_line_quality(stats, score)
    
    # Calculate base momentum gain
    momentum_gain = get_momentum_gain(score, stats.get("promo_delivery", 10))
    
    # Update streak info
    if streak_info is None:
        streak_info = {"count": 0, "quality": 0, "last_score": 0}
    
    if score > streak_info["last_score"]:
        streak_info["count"] += 1
        streak_info["quality"] += score
    else:
        streak_info["count"] = 0
        streak_info["quality"] = 0
    streak_info["last_score"] = score
    
    # Handle momentum for exceptional performances
    if exceptional:
        # Add a bonus to momentum gain for exceptional performances
        momentum_gain *= 1.5  # 50% bonus to momentum gain
    
    # Check for momentum cash-in
    new_confidence, new_momentum, cashed_in = maybe_cash_in_momentum(
        momentum + momentum_gain, confidence, stats, beat_number
    )
    
    if not cashed_in:
        # Apply confidence decay if we didn't cash in momentum
        confidence_decay = calculate_confidence_decay(stats)
        new_confidence = max(get_confidence_floor(stats), min(100, confidence + confidence_decay))
        new_momentum = momentum + momentum_gain
    
    beat_data = {
        "beat_number": beat_number,
        "commentary": f"Mid beat {beat_number}",
        "score": score,
        "line_quality": quality,
        "momentum_change": momentum_gain if not cashed_in else -momentum,
        "confidence_shift": new_confidence - confidence,
        "momentum_meter": momentum,
        "confidence_level": confidence,
        "momentum": new_momentum,
        "confidence": new_confidence,
        "cash_in_used": cashed_in,
        "streak_info": streak_info
    }
    
    if exceptional:
        beat_data["exceptional"] = exceptional
    
    return beat_data

def generate_end_beat(stats, beat_number, momentum, confidence, crowd_reaction, streak_info):
    """Generate end beat with streak and finale mechanics."""
    # End beats get +10 confidence and increased exceptional chances
    score, exceptional = roll_promo_score(
        stats, beat_number, momentum, confidence + 10, 
        crowd_reaction, streak_info
    )
    quality = determine_line_quality(stats, score)
    
    # Calculate momentum gain (reduced in end phase)
    momentum_gain = get_momentum_gain(score, stats.get("promo_delivery", 10)) * 0.5
    
    # Calculate confidence decay
    confidence_decay = calculate_confidence_decay(stats)
    new_confidence = max(get_confidence_floor(stats), min(100, confidence + confidence_decay))
    
    # Update streak info one last time
    if score > streak_info["last_score"]:
        streak_info["count"] += 1
        streak_info["quality"] += score
    
    beat_data = {
        "beat_number": beat_number,
        "commentary": f"End beat {beat_number}",
        "score": score,
        "line_quality": quality,
        "momentum_change": momentum_gain,
        "confidence_shift": confidence_decay,
        "momentum_meter": momentum,
        "confidence_level": confidence,
        "momentum": momentum + momentum_gain,
        "confidence": new_confidence,
        "streak_info": streak_info
    }
    
    if exceptional:
        beat_data["exceptional"] = exceptional
    
    return beat_data

def maybe_cash_in_momentum(momentum, confidence, stats, beat_number):
    """Decide whether to cash in momentum."""
    # Don't allow cash-ins with no momentum
    if momentum <= 0:
        return confidence, momentum, False
        
    pressure_handling = stats.get("pressure_handling", 10)
    risk_assessment = stats.get("risk_assessment", 10)
    
    # Higher threshold to prevent too frequent cash-ins
    base_threshold = 45 - ((pressure_handling + risk_assessment) / 4)  # 35-45 range
    
    # Adjust threshold based on conditions
    if confidence < 40:  # Struggling - more likely to cash in
        threshold = base_threshold - 15
    elif beat_number >= 4:  # Late in promo
        threshold = base_threshold - 10
    else:
        threshold = base_threshold
    
    # High pressure wrestlers are slightly more strategic
    if pressure_handling >= 12:
        threshold += 5
    
    # Only cash in if we have significant momentum and either:
    # - Confidence is low
    # - Momentum is very high
    # - Mid momentum but below average confidence
    should_cash_in = (
        momentum >= threshold and (
            confidence < 40 or  # Cash in when struggling
            momentum >= 75 or   # Cash in at very high momentum
            (confidence < 50 and momentum >= 60)  # Cash in at medium momentum if confidence is below average
        )
    )
    
    # Decision to cash in
    if should_cash_in:
        # Calculate confidence boost using the new formula
        conf_boost = calculate_cash_in_boost(momentum)
        
        # Calculate final confidence with boost
        new_confidence = min(100, confidence + conf_boost)
        return new_confidence, 0, True
    
    return confidence, momentum, False

def calculate_cash_in_boost(momentum: float) -> float:
    """Calculate confidence boost when cashing in momentum.
    
    Args:
        momentum (float): Current momentum value (0-100)
        
    Returns:
        float: Confidence boost value (10-50)
        
    Formula: base_boost + scaling_factor * (momentum ^ exponent)
    - Base boost of 10 for any cash-in
    - Exponential scaling (2.5) to reward higher momentum
    - ±5% random variation for volatility
    - Clamped between 10-50 total boost
    """
    # Constants
    BASE_BOOST = 10.0
    SCALING_FACTOR = 0.000126
    EXPONENT = 2.5
    MIN_BOOST = 10.0
    MAX_BOOST = 50.0
    VARIANCE_PCT = 0.05  # ±5% variation
    
    # Calculate base boost using the formula
    boost = BASE_BOOST + (SCALING_FACTOR * (momentum ** EXPONENT))
    
    # Add random variation (±5%)
    variance = boost * VARIANCE_PCT
    boost += random.uniform(-variance, variance)
    
    # Clamp the final value between MIN_BOOST and MAX_BOOST
    return max(MIN_BOOST, min(MAX_BOOST, boost))

def get_promo_line(tone, theme, phase, opponent=None):
    """Get a promo line based on tone, theme, and phase."""
    from src.promo.promo_lines import PROMO_LINES
    
    # Map tone to promo line bucket
    tone_map = {
        "boast": "boast",
        "insult": "insult",
        "callout": "callout",
        "challenge": "callout",
        "humble": "humble"
    }
    
    # Map theme to promo line bucket
    theme_map = {
        "legacy": "legacy",
        "dominance": "dominance",
        "betrayal": "betrayal",
        "power": "power",
        "comeback": "comeback",
        "respect": "respect"
    }
    
    # Map phase to promo line bucket
    phase_map = {
        "beginning": "opening",
        "opening": "opening",
        "middle": "middle",
        "end": "closing",
        "ending": "closing"
    }
    
    mapped_tone = tone_map.get(tone, "boast")
    mapped_theme = theme_map.get(theme, "legacy")
    mapped_phase = phase_map.get(phase, "middle")
    
    # Get lines for this combination
    lines = PROMO_LINES.get(mapped_phase, {}).get(mapped_tone, {}).get(mapped_theme, [])
    
    if not lines:
        # Fallback to generic lines if specific combination not found
        lines = PROMO_LINES.get(mapped_phase, {}).get(mapped_tone, {}).get("generic", [])
    
    if not lines:
        # Last resort fallback
        return "The wrestler cuts a passionate promo."
    
    # Choose a random line
    line = random.choice(lines)
    
    # If we have an opponent, try to use a line that references opponents
    if opponent and "opponent" in line:
        opponent_lines = [l for l in lines if "opponent" in l]
        if opponent_lines:
            line = random.choice(opponent_lines)
    
    # Replace opponent placeholder if available
    if opponent:
        opponent_name = opponent.get("name", "their opponent")
        line = line.replace("opponent", opponent_name)
    
    return line
