import random
from datetime import datetime, timedelta

# Define wrestler archetypes
ARCHETYPES = {
    "Power Wrestler": {
        "physical": {"base": 16, "range": 4},  # Powerlifting, grip strength
        "aerial": {"base": 8, "range": 4},     # Agility, aerial precision
        "technical": {"base": 12, "range": 3}, # Chain wrestling, mat transitions
        "charisma": {"base": 10, "range": 6},  # Promo, fan engagement
        "mental": {"base": 12, "range": 3},    # Focus, resilience
    },
    "High Flyer": {
        "physical": {"base": 10, "range": 3},
        "aerial": {"base": 17, "range": 3},
        "technical": {"base": 12, "range": 3},
        "charisma": {"base": 13, "range": 4},
        "mental": {"base": 12, "range": 3},
    },
    "Technical Wrestler": {
        "physical": {"base": 12, "range": 3},
        "aerial": {"base": 11, "range": 3},
        "technical": {"base": 17, "range": 3},
        "charisma": {"base": 11, "range": 4},
        "mental": {"base": 15, "range": 3},
    },
    "Brawler": {
        "physical": {"base": 15, "range": 3},
        "aerial": {"base": 8, "range": 3},
        "technical": {"base": 10, "range": 4},
        "charisma": {"base": 12, "range": 5},
        "mental": {"base": 13, "range": 3},
    },
    "Showman": {
        "physical": {"base": 11, "range": 4},
        "aerial": {"base": 12, "range": 4},
        "technical": {"base": 12, "range": 3},
        "charisma": {"base": 18, "range": 2},
        "mental": {"base": 11, "range": 4},
    },
    "All-Rounder": {
        "physical": {"base": 13, "range": 2},
        "aerial": {"base": 13, "range": 2},
        "technical": {"base": 13, "range": 2},
        "charisma": {"base": 13, "range": 2},
        "mental": {"base": 13, "range": 2},
    }
}

def random_stat(base, variance):
    """Generate a random stat with some variance around the base value"""
    value = base + random.randint(-variance, variance)
    return max(5, min(20, value))  # Clamp between 5 and 20

def generate_random_wrestler(archetype=None):
    """Generate a random wrestler based on an archetype"""
    if not archetype:
        archetype = random.choice(list(ARCHETYPES.keys()))
    
    archetype_data = ARCHETYPES[archetype]
    
    # Generate random attributes based on archetype
    physical_base = archetype_data["physical"]["base"]
    physical_range = archetype_data["physical"]["range"]
    
    aerial_base = archetype_data["aerial"]["base"]
    aerial_range = archetype_data["aerial"]["range"]
    
    technical_base = archetype_data["technical"]["base"]
    technical_range = archetype_data["technical"]["range"]
    
    charisma_base = archetype_data["charisma"]["base"]
    charisma_range = archetype_data["charisma"]["range"]
    
    mental_base = archetype_data["mental"]["base"]
    mental_range = archetype_data["mental"]["range"]
    
    # Generate individual attributes
    attributes = {
        # Physical attributes
        "powerlifting": random_stat(physical_base, physical_range),
        "grapple_control": random_stat(physical_base - 1, physical_range),
        "grip_strength": random_stat(physical_base, physical_range),
        "agility": random_stat(aerial_base, aerial_range),
        "balance": random_stat(aerial_base - 1, aerial_range),
        "flexibility": random_stat(aerial_base - 2, aerial_range),
        "recovery_rate": random_stat(physical_base - 2, physical_range),
        "conditioning": random_stat(physical_base - 1, physical_range),
        
        # Technical attributes
        "chain_wrestling": random_stat(technical_base, technical_range),
        "mat_transitions": random_stat(technical_base, technical_range),
        "submission_technique": random_stat(technical_base - 1, technical_range),
        "strike_accuracy": random_stat(technical_base - 2, technical_range),
        "brawling_technique": random_stat(physical_base - 1, physical_range),
        "aerial_precision": random_stat(aerial_base, aerial_range),
        "counter_timing": random_stat(technical_base - 1, technical_range),
        "pressure_handling": random_stat(mental_base - 1, mental_range),
        
        # Charisma attributes
        "promo_delivery": random_stat(charisma_base, charisma_range),
        "fan_engagement": random_stat(charisma_base, charisma_range),
        "entrance_presence": random_stat(charisma_base - 1, charisma_range),
        "presence_under_fire": random_stat(charisma_base - 2, charisma_range),
        "confidence": random_stat(charisma_base - 1, charisma_range),
        
        # Mental attributes
        "focus": random_stat(mental_base, mental_range),
        "resilience": random_stat(mental_base, mental_range),
        "adaptability": random_stat(mental_base - 1, mental_range),
        "risk_assessment": random_stat(mental_base - 2, mental_range),
        "loyalty": random_stat(mental_base - 1, mental_range),
        "political_instinct": random_stat(mental_base - 2, mental_range),
        "determination": random_stat(mental_base, mental_range)
    }
    
    # Random reputation between 30-70
    reputation = random.randint(30, 70)
    
    # Generate random contract details
    current_date = datetime.now()
    expiry_date = current_date + timedelta(days=random.randint(730, 1460))  # 2-4 years
    contract_expiry = expiry_date.strftime('%Y-%m-%d')
    
    # Generate height and weight based on archetype
    if archetype == "Power Wrestler":
        height = random.randint(74, 82)  # 6'2" to 6'10"
        weight = random.randint(260, 350)
    elif archetype == "High Flyer":
        height = random.randint(66, 73)  # 5'6" to 6'1"
        weight = random.randint(190, 240)
    elif archetype == "Technical Wrestler":
        height = random.randint(70, 76)  # 5'10" to 6'4"
        weight = random.randint(220, 270)
    elif archetype == "Brawler":
        height = random.randint(72, 78)  # 6'0" to 6'6"
        weight = random.randint(240, 300)
    elif archetype == "Showman":
        height = random.randint(69, 75)  # 5'9" to 6'3"
        weight = random.randint(210, 260)
    else:  # All-Rounder
        height = random.randint(70, 76)  # 5'10" to 6'4"
        weight = random.randint(220, 270)
    
    # Generate random finisher based on archetype
    finisher_styles = {
        "Power Wrestler": ["slam", "slam", "slam", "strike"],
        "High Flyer": ["aerial", "aerial", "strike", "slam"],
        "Technical Wrestler": ["submission", "submission", "slam", "strike"],
        "Brawler": ["strike", "strike", "slam", "slam"],
        "Showman": ["strike", "slam", "aerial", "submission"],
        "All-Rounder": ["slam", "strike", "submission", "aerial"]
    }
    
    finisher_style = random.choice(finisher_styles[archetype])
    
    # Generate signature moves based on archetype
    signature_count = random.randint(2, 3)
    signature_moves = []
    
    for _ in range(signature_count):
        move_type = random.choice(finisher_styles[archetype])
        damage = random.randint(6, 8)
        difficulty = random.randint(5, 7)
        signature_moves.append({
            "type": move_type,
            "damage": damage,
            "difficulty": difficulty
        })
    
    return {
        "attributes": attributes,
        "reputation": reputation,
        "condition": 100,
        "contract_expiry": contract_expiry,
        "contract_value": 500000 + (reputation * 10000),
        "height": height,
        "weight": weight,
        "finisher_style": finisher_style,
        "finisher_damage": 10,
        "finisher_difficulty": 8,
        "signature_moves": signature_moves,
        "archetype": archetype
    }

def get_attributes_list(attributes):
    """Convert attributes dictionary to ordered list for database insertion"""
    return [
        attributes["powerlifting"],
        attributes["grapple_control"],
        attributes["grip_strength"],
        attributes["agility"],
        attributes["balance"],
        attributes["flexibility"],
        attributes["recovery_rate"],
        attributes["conditioning"],
        attributes["chain_wrestling"],
        attributes["mat_transitions"],
        attributes["submission_technique"],
        attributes["strike_accuracy"],
        attributes["brawling_technique"],
        attributes["aerial_precision"],
        attributes["counter_timing"],
        attributes["pressure_handling"],
        attributes["promo_delivery"],
        attributes["fan_engagement"],
        attributes["entrance_presence"],
        attributes["presence_under_fire"],
        attributes["confidence"],
        attributes["focus"],
        attributes["resilience"],
        attributes["adaptability"],
        attributes["risk_assessment"],
        attributes["loyalty"],
        attributes["political_instinct"],
        attributes["determination"]
    ]

def get_attribute_names():
    """Return list of attribute names in order"""
    return [
        "powerlifting", "grapple_control", "grip_strength",
        "agility", "balance", "flexibility", "recovery_rate", "conditioning",
        "chain_wrestling", "mat_transitions", "submission_technique", "strike_accuracy",
        "brawling_technique", "aerial_precision", "counter_timing", "pressure_handling",
        "promo_delivery", "fan_engagement", "entrance_presence", "presence_under_fire", "confidence",
        "focus", "resilience", "adaptability", "risk_assessment",
        "loyalty", "political_instinct", "determination"
    ] 