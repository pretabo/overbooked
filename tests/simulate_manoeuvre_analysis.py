import random
from match_engine import simulate_match
from match_engine_utils import update_manoeuvre_stats
from match_engine_utils import update_wrestler_move_experience

# Configuration
MATCH_COUNT = 1000
PHASES = ["early", "mid", "late"]

# Data collection
move_usage = {phase: {} for phase in PHASES}
experience_effects = {}

# Dummy moves
dummy_finisher = {
    "name": "Sim Finish",
    "style": "slam",
    "damage": 10
}

dummy_signature = {
    "name": "Sim Sig",
    "type": "strike",
    "damage": 7,
    "difficulty": 5
}

# Simulate matches
def run_simulations():
    for _ in range(MATCH_COUNT):
        # Generate random wrestlers
        wrestler1 = {
            "id": 1,
            "name": "Wrestler 1",
            "stamina": 100,
            "strike_accuracy": random.randint(5, 15),
            "powerlifting": random.randint(5, 15),
            "grapple_control": random.randint(5, 15),
            "grip_strength": random.randint(5, 15),
            "aerial_precision": random.randint(5, 15),
            "mat_transitions": random.randint(5, 15),
            "confidence": random.randint(5, 15),
            "risk_assessment": random.randint(5, 15),
            "determination": random.randint(5, 15),
            "focus": random.randint(5, 15),
            "resilience": random.randint(5, 15),
            "fan_engagement": random.randint(5, 15),
            "promo_delivery": random.randint(5, 15),
            "height": random.randint(65, 80),
            "weight": random.randint(150, 300),
            "conditioning": random.randint(5, 15),
            "recovery_rate": random.randint(5, 15),
            "agility": random.randint(5, 15),
            "finisher": dummy_finisher,
            "signature_moves": [dummy_signature]
        }

        # Create a deep copy for wrestler2 with new ID and name
        wrestler2 = {**wrestler1, "id": 2, "name": "Wrestler 2"}

        # Add derived attributes
        for wrestler in (wrestler1, wrestler2):
            wrestler.update({
                "intelligence": (wrestler["risk_assessment"] + wrestler["mat_transitions"]) // 2,
                "endurance": (wrestler["conditioning"] + wrestler["recovery_rate"] + wrestler["determination"]) // 3,
                "strength": (wrestler["powerlifting"] + wrestler["grip_strength"]) // 2,
                "dexterity": (wrestler["agility"] + wrestler["aerial_precision"]) // 2,
                "charisma": (wrestler["fan_engagement"] + wrestler["confidence"] + wrestler["promo_delivery"]) // 3
            })

        # Simulate match
        result = simulate_match(wrestler1, wrestler2, log_function=lambda x: None, fast_mode=True)

        # Update experience log
        for move in result.get("used_manoeuvres", []):
            update_wrestler_move_experience(
                wrestler_id=move["wrestler_id"],
                move_name=move["move_name"],
                success=move["success"]
            )


        # Analyze moves by phase
        for phase in PHASES:
            for move in result.get("moves", {}).get(phase, []):
                move_type = move["type"]
                move_usage[phase][move_type] = move_usage[phase].get(move_type, 0) + 1

        # Analyze experience effects
        for move in result.get("moves", {}).get("all", []):
            move_type = move["type"]
            success = move["success"]
            if move_type not in experience_effects:
                experience_effects[move_type] = {"success": 0, "total": 0}
            experience_effects[move_type]["success"] += 1 if success else 0
            experience_effects[move_type]["total"] += 1

# Print results
def print_analysis():
    print("\n--- Move Usage by Phase ---")
    for phase, moves in move_usage.items():
        print(f"\n{phase.capitalize()} Phase:")
        for move_type, count in moves.items():
            print(f"  {move_type}: {count} times")

    print("\n--- Experience Effects ---")
    for move_type, data in experience_effects.items():
        success_rate = data["success"] / data["total"] * 100
        print(f"  {move_type}: {success_rate:.2f}% success rate ({data['total']} attempts)")

if __name__ == "__main__":
    run_simulations()
    print_analysis()
