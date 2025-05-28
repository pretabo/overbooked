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

def get_grade_and_colour(score):
    for threshold, grade, colour in GRADE_SCALE:
        if score >= threshold:
            return grade, colour
    return "F", "#888888"

def calculate_high_level_stats_with_grades(stats):
    output = {}

    for category, substats in STAT_MAP.items():
        values = [stats.get(s, 0) for s in substats]
        avg = round(mean(values)) if values else 0
        grade, colour = get_grade_and_colour(avg)

        output[category] = {
            "value": avg,
            "grade": grade,
            "colour": colour
        }

    return output
