from statistics import mean

# Map each high-level stat to its contributing substats
STAT_MAP = {
    "strength": [
        "powerlifting", "grapple_control", "grip_strength", "brawling_technique"
    ],
    "dexterity": [
        "agility", "balance", "flexibility", "aerial_precision",
        "strike_accuracy", "counter_timing"
    ],
    "endurance": [
        "recovery_rate", "conditioning", "resilience", "determination"
    ],
    "intelligence": [
        "chain_wrestling", "mat_transitions", "submission_technique",
        "pressure_handling", "focus", "adaptability", "risk_assessment",
        "political_instinct"
    ],
    "charisma": [
        "promo_delivery", "fan_engagement", "entrance_presence",
        "presence_under_fire", "confidence"
    ]
}

# Grading scale (out of 20)
GRADE_SCALE = [
    (18, "S", "#ffd700"),   # S: Gold
    (16, "A", "#26A55B"),   # A: Dark Green
    (13, "B", "#68F3A2"),   # B: Light Green
    (10, "C", "#F5A340"),   # C: Orange
    (7,  "D", "#FF7373"),   # D: Light Red
    (0,  "F", "#E70000")    # F: Red
]

def get_wrestler_attr(wrestler, attr, default=None):
    """
    Safely get wrestler attribute regardless of data structure
    
    Args:
        wrestler: Wrestler object or dictionary
        attr: Attribute name to retrieve
        default: Default value if attribute is not found
        
    Returns:
        The attribute value or default
    """
    # First try direct attribute access
    if hasattr(wrestler, attr):
        return getattr(wrestler, attr)
    
    # Try dictionary access
    elif isinstance(wrestler, dict) and attr in wrestler:
        return wrestler[attr]
    
    # Try attributes dictionary
    elif hasattr(wrestler, "attributes") and isinstance(wrestler.attributes, dict):
        if attr in wrestler.attributes:
            return wrestler.attributes[attr]
    
    # Try nested attributes dictionary
    elif isinstance(wrestler, dict) and "attributes" in wrestler:
        if isinstance(wrestler["attributes"], dict) and attr in wrestler["attributes"]:
            return wrestler["attributes"][attr]
    
    # Special case for stats that need calculation
    if attr == "strength":
        return calculate_strength(wrestler)
    elif attr == "dexterity":
        return calculate_dexterity(wrestler)
    elif attr == "endurance":
        return calculate_endurance(wrestler)
    elif attr == "intelligence":
        return calculate_intelligence(wrestler)
    elif attr == "charisma":
        return calculate_charisma(wrestler)
    
    return default

def get_grade_and_colour(score):
    """
    Get letter grade and color based on numeric score
    
    Args:
        score: Numeric score to convert to grade
        
    Returns:
        Tuple of (grade, color_hex)
    """
    for threshold, grade, colour in GRADE_SCALE:
        if score >= threshold:
            return grade, colour
    return "F", "#888888"

def get_star_rating(value, max_value=20):
    """
    Convert a numerical value to a star rating string
    
    Args:
        value: Numerical value to convert
        max_value: Maximum possible value (default: 20)
        
    Returns:
        String with star rating (e.g., "★★★☆☆")
    """
    # Normalize value based on typical ranges
    if max_value == 100:  # For stamina which is 0-100
        normalized = (value / 100) * 5
    elif value > 50:  # For reputation or other higher-scale values
        normalized = min(5, (value / 100) * 5)
    else:  # For standard attributes (0-20)
        normalized = (value / 20) * 5
    
    # Round to nearest half-star
    rounded = round(normalized * 2) / 2
    
    # Generate star string
    full_stars = int(rounded)
    half_star = (rounded - full_stars) >= 0.5
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    
    return "★" * full_stars + ("½" if half_star else "") + "☆" * empty_stars

def calculate_high_level_stats_with_grades(stats):
    """
    Calculate high-level stats with grades from detailed attributes
    
    Args:
        stats: Dictionary of attribute values
        
    Returns:
        Dictionary with high-level stats, including value, grade, color and stars
    """
    output = {}

    for category, substats in STAT_MAP.items():
        values = [stats.get(s, 0) for s in substats]
        avg = round(mean(values)) if values else 0
        grade, colour = get_grade_and_colour(avg)
        stars = get_star_rating(avg)

        output[category] = {
            "value": avg,
            "grade": grade,
            "colour": colour,
            "stars": stars
        }

    return output

def calculate_strength(wrestler):
    """
    Calculate wrestler's strength based on physical attributes
    
    Args:
        wrestler: Wrestler object or dictionary
        
    Returns:
        Integer strength value
    """
    # Get physical attributes safely
    powerlifting = _get_substat(wrestler, "powerlifting", 10)
    grapple_control = _get_substat(wrestler, "grapple_control", 10)
    grip_strength = _get_substat(wrestler, "grip_strength", 10)
    brawling_technique = _get_substat(wrestler, "brawling_technique", 10)
    
    # Calculate strength as weighted average
    values = [powerlifting, grapple_control, grip_strength, brawling_technique]
    return round(mean(values)) if values else 10

def calculate_dexterity(wrestler):
    """
    Calculate wrestler's dexterity based on agility and technique attributes
    
    Args:
        wrestler: Wrestler object or dictionary
        
    Returns:
        Integer dexterity value
    """
    # Get dexterity-related attributes safely
    agility = _get_substat(wrestler, "agility", 10)
    balance = _get_substat(wrestler, "balance", 10)
    flexibility = _get_substat(wrestler, "flexibility", 10)
    aerial_precision = _get_substat(wrestler, "aerial_precision", 10)
    strike_accuracy = _get_substat(wrestler, "strike_accuracy", 10)
    counter_timing = _get_substat(wrestler, "counter_timing", 10)
    
    # Calculate dexterity as weighted average
    values = [agility, balance, flexibility, aerial_precision, strike_accuracy, counter_timing]
    return round(mean(values)) if values else 10

def calculate_endurance(wrestler):
    """
    Calculate wrestler's endurance based on stamina and resilience attributes
    
    Args:
        wrestler: Wrestler object or dictionary
        
    Returns:
        Integer endurance value
    """
    # Get endurance-related attributes safely
    recovery_rate = _get_substat(wrestler, "recovery_rate", 10)
    conditioning = _get_substat(wrestler, "conditioning", 10)
    resilience = _get_substat(wrestler, "resilience", 10)
    determination = _get_substat(wrestler, "determination", 10)
    
    # Calculate endurance as weighted average
    values = [recovery_rate, conditioning, resilience, determination]
    return round(mean(values)) if values else 10

def calculate_intelligence(wrestler):
    """
    Calculate wrestler's intelligence based on mental and technical attributes
    
    Args:
        wrestler: Wrestler object or dictionary
        
    Returns:
        Integer intelligence value
    """
    # Get primary mental attributes that affect intelligence
    focus = _get_substat(wrestler, "focus", 10)
    risk_assessment = _get_substat(wrestler, "risk_assessment", 10)
    adaptability = _get_substat(wrestler, "adaptability", 10)
    
    # Get technical attributes that contribute to ring IQ
    chain_wrestling = _get_substat(wrestler, "chain_wrestling", 10)
    mat_transitions = _get_substat(wrestler, "mat_transitions", 10)
    submission_technique = _get_substat(wrestler, "submission_technique", 10)
    pressure_handling = _get_substat(wrestler, "pressure_handling", 10)
    
    # Calculate intelligence - prioritize the mental attributes
    primary_mental = [focus, risk_assessment, adaptability]
    technical = [chain_wrestling, mat_transitions, submission_technique, pressure_handling]
    
    # Weighted average - 60% mental, 40% technical
    primary_avg = mean(primary_mental) if primary_mental else 10
    technical_avg = mean(technical) if technical else 10
    
    return round(primary_avg * 0.6 + technical_avg * 0.4)

def calculate_charisma(wrestler):
    """
    Calculate wrestler's charisma based on performance and presence attributes
    
    Args:
        wrestler: Wrestler object or dictionary
        
    Returns:
        Integer charisma value
    """
    # Get charisma-related attributes safely
    promo_delivery = _get_substat(wrestler, "promo_delivery", 10)
    fan_engagement = _get_substat(wrestler, "fan_engagement", 10)
    entrance_presence = _get_substat(wrestler, "entrance_presence", 10)
    presence_under_fire = _get_substat(wrestler, "presence_under_fire", 10)
    confidence = _get_substat(wrestler, "confidence", 10)
    
    # Calculate charisma as weighted average
    values = [promo_delivery, fan_engagement, entrance_presence, presence_under_fire, confidence]
    return round(mean(values)) if values else 10

def calculate_psychology_rating(wrestler):
    """
    Calculate a wrestler's psychological strength and match IQ
    
    Args:
        wrestler: Wrestler object or dictionary
        
    Returns:
        Integer psychology rating
    """
    # Get mental attributes
    focus = _get_substat(wrestler, "focus", 10)
    resilience = _get_substat(wrestler, "resilience", 10)
    adaptability = _get_substat(wrestler, "adaptability", 10)
    risk_assessment = _get_substat(wrestler, "risk_assessment", 10)
    determination = _get_substat(wrestler, "determination", 10)
    
    # Calculate psychology rating (0-20 scale)
    psychology = (focus * 0.25 + resilience * 0.25 + adaptability * 0.2 + 
                 risk_assessment * 0.15 + determination * 0.15)
    
    return min(20, max(1, psychology))

def calculate_offense_rating(wrestler):
    """
    Calculate a wrestler's offensive capability
    
    Args:
        wrestler: Wrestler object or dictionary
        
    Returns:
        Integer offense rating
    """
    # Get attributes
    power = _get_substat(wrestler, "powerlifting", 10)
    grapple = _get_substat(wrestler, "grapple_control", 10)
    strike = _get_substat(wrestler, "strike_accuracy", 10)
    aerial = _get_substat(wrestler, "aerial_precision", 10)
    brawling = _get_substat(wrestler, "brawling_technique", 10)
    
    # Calculate offense rating (0-20 scale)
    offense = (power * 0.25 + grapple * 0.2 + strike * 0.2 + 
              aerial * 0.15 + brawling * 0.2)
    
    return min(20, max(1, offense))

def calculate_defense_rating(wrestler):
    """
    Calculate a wrestler's defensive capability
    
    Args:
        wrestler: Wrestler object or dictionary
        
    Returns:
        Integer defense rating
    """
    # Get attributes
    counter = _get_substat(wrestler, "counter_timing", 10)
    agility = _get_substat(wrestler, "agility", 10)
    balance = _get_substat(wrestler, "balance", 10)
    recovery = _get_substat(wrestler, "recovery_rate", 10)
    
    # Calculate defense rating (0-20 scale)
    defense = (counter * 0.3 + agility * 0.25 + balance * 0.25 + 
              recovery * 0.2)
    
    return min(20, max(1, defense))

def calculate_overall_rating(wrestler):
    """
    Calculate wrestler's overall rating based on all main stats
    
    Args:
        wrestler: Wrestler object or dictionary
        
    Returns:
        Integer overall rating
    """
    # Get primary stats
    strength = calculate_strength(wrestler)
    dexterity = calculate_dexterity(wrestler)
    endurance = calculate_endurance(wrestler)
    intelligence = calculate_intelligence(wrestler)
    charisma = calculate_charisma(wrestler)
    
    # Calculate overall as average of five main stats
    return round((strength + dexterity + endurance + intelligence + charisma) / 5)

def _get_substat(wrestler, attr, default=10):
    """
    Helper method to get substat attributes safely
    
    Args:
        wrestler: Wrestler object or dictionary
        attr: Substat attribute name
        default: Default value if not found
        
    Returns:
        Integer attribute value
    """
    # Handle different data structures
    if hasattr(wrestler, "get_attribute"):
        try:
            return wrestler.get_attribute(attr)
        except:
            pass
    
    if hasattr(wrestler, "attributes") and isinstance(wrestler.attributes, dict):
        if attr in wrestler.attributes:
            return wrestler.attributes[attr]
    
    if isinstance(wrestler, dict):
        if "attributes" in wrestler and isinstance(wrestler["attributes"], dict):
            if attr in wrestler["attributes"]:
                return wrestler["attributes"][attr]
        elif attr in wrestler:
            return wrestler[attr]
    
    return default 