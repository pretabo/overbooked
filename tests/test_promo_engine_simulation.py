import sys
import os
import random
import json
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from promo.promo_engine import PromoEngine

# --- Config ---
PROMO_COUNT = 100
BEATS = 35

# --- Storage ---
promo_results = []
full_promo_data = []
momentum_cash_ins = {
    "Weak": {"total_beats": 0, "cash_ins": 0, "pre_cash_scores": [], "post_cash_scores": [], "cash_in_sequences": []},
    "Regular": {"total_beats": 0, "cash_ins": 0, "pre_cash_scores": [], "post_cash_scores": [], "cash_in_sequences": []},
    "Talented": {"total_beats": 0, "cash_ins": 0, "pre_cash_scores": [], "post_cash_scores": [], "cash_in_sequences": []}
}

# --- Helpers ---
def generate_test_wrestler(name, archetype="Regular", id=None):
    attribute_sets = {
        "Weak": {
            "promo_delivery": random.randint(3, 6),
            "fan_engagement": random.randint(3, 6),
            "entrance_presence": random.randint(3, 6),
            "presence_under_fire": random.randint(3, 6),
            "confidence": random.randint(3, 6),
            "reputation": random.randint(3, 6),
            "focus": random.randint(3, 6),
            "determination": random.randint(3, 6)
        },
        "Regular": {
            "promo_delivery": random.randint(8, 12),
            "fan_engagement": random.randint(8, 12),
            "entrance_presence": random.randint(8, 12),
            "presence_under_fire": random.randint(8, 12),
            "confidence": random.randint(8, 12),
            "reputation": random.randint(8, 12),
            "focus": random.randint(8, 12),
            "determination": random.randint(8, 12)
        },
        "Talented": {
            "promo_delivery": random.randint(15, 20),
            "fan_engagement": random.randint(15, 20),
            "entrance_presence": random.randint(15, 20),
            "presence_under_fire": random.randint(15, 20),
            "confidence": random.randint(15, 20),
            "reputation": random.randint(15, 20),
            "focus": random.randint(15, 20),
            "determination": random.randint(15, 20)
        },
    }
    attributes = attribute_sets[archetype]
    return {"id": id or random.randint(1000, 9999), "name": name, "attributes": attributes}

# --- Simulation ---
def run_simulations():
    event_crowd_reaction = 50.0

    for i in range(PROMO_COUNT):
        archetype = random.choice(["Weak", "Regular", "Talented"])
        wrestler = generate_test_wrestler("Main", archetype=archetype)
        opponent = generate_test_wrestler("Target", archetype=random.choice(["Regular", "Talented"]))
        promo_type = random.choice(["Self-Promo", "Call Out", "Friendly Promo", "Storyline Build"])

        engine = PromoEngine(
            wrestler=wrestler,
            crowd_reaction=event_crowd_reaction
        )
        result = engine.simulate()
        event_crowd_reaction = result.get("crowd_reaction", event_crowd_reaction)

        # Track scores around cash-ins
        for beat_idx, beat in enumerate(result["beats"]):
            if beat.get("cash_in_used", False):
                # Get 5 beats before and after cash-in
                start_idx = max(0, beat_idx - 5)
                end_idx = min(len(result["beats"]), beat_idx + 6)
                sequence = result["beats"][start_idx:end_idx]
                
                if "cash_in_sequences" not in momentum_cash_ins[archetype]:
                    momentum_cash_ins[archetype]["cash_in_sequences"] = []
                
                sequence_data = []
                for seq_beat in sequence:
                    sequence_data.append({
                        "beat_number": seq_beat["beat_number"],
                        "score": seq_beat["score"],
                        "momentum": seq_beat.get("momentum", 0),
                        "momentum_change": seq_beat.get("momentum_change", 0),
                        "confidence": seq_beat.get("confidence", 0),
                        "is_cash_in": seq_beat.get("cash_in_used", False)
                    })
                
                momentum_cash_ins[archetype]["cash_in_sequences"].append(sequence_data)

        # Track momentum cash-ins
        cash_in_count = sum(1 for beat in result["beats"] if beat.get("cash_in_used", False))
        momentum_cash_ins[archetype]["cash_ins"] += cash_in_count
        momentum_cash_ins[archetype]["total_beats"] += len(result["beats"])

        promo_results.append({
            "score": result["final_rating"],
            "length": len(result["beats"]),
            "archetype": archetype,
            "cash_ins": cash_in_count
        })

        full_promo_data.append({
            "promo_id": i + 1,
            "archetype": archetype,
            "final_rating": result["final_rating"],
            "length": len(result["beats"]),
            "beats": result["beats"],
            "cash_ins": cash_in_count
        })

# --- Summary ---
def print_summary():
    print("\n--- Promo Simulation Summary ---")
    print(f"Total Promos Simulated: {len(promo_results)}")
    avg_score = np.mean([p["score"] for p in promo_results])
    avg_length = np.mean([p["length"] for p in promo_results])
    total_cash_ins = sum(p["cash_ins"] for p in promo_results)
    print(f"Average Promo Rating: {avg_score:.2f}")
    print(f"Average Promo Length: {avg_length:.2f} beats")
    print(f"Total Momentum Cash-ins: {total_cash_ins}")
    print(f"Average Cash-ins per Promo: {total_cash_ins/len(promo_results):.2f}")

    print("\n--- Archetype Breakdown ---")
    for archetype in ["Weak", "Regular", "Talented"]:
        scores = [p["score"] for p in promo_results if p["archetype"] == archetype]
        cash_in_data = momentum_cash_ins[archetype]
        if scores:
            cash_in_rate = (cash_in_data["cash_ins"] / cash_in_data["total_beats"]) * 100 if cash_in_data["total_beats"] > 0 else 0
            print(f"\n{archetype}:")
            print(f"  Avg Score: {np.mean(scores):.2f} | Min {min(scores):.2f} | Max {max(scores):.2f}")
            print(f"  Cash-in Rate: {cash_in_rate:.2f}% ({cash_in_data['cash_ins']} cash-ins in {cash_in_data['total_beats']} beats)")
            
            if cash_in_data.get("cash_in_sequences"):
                print("\n  Example Cash-in Sequences:")
                # Show 3 random sequences
                sequences = random.sample(cash_in_data["cash_in_sequences"], min(3, len(cash_in_data["cash_in_sequences"])))
                for seq_num, sequence in enumerate(sequences, 1):
                    print(f"\n    Sequence {seq_num}:")
                    print("    Beat  Score  Momentum  M.Change  Confidence")
                    print("    ----  -----  --------  --------  ----------")
                    for beat in sequence:
                        cash_marker = "*" if beat["is_cash_in"] else " "
                        print(f"    {beat['beat_number']:3d}{cash_marker} {beat['score']:5.1f}  {beat['momentum']:8.1f}  {beat['momentum_change']:8.1f}  {beat['confidence']:10.1f}")
            
            print(f"\n  Count: {len(scores)}")

# --- Run ---
if __name__ == "__main__":
    run_simulations()
    print_summary()

    with open("promo_simulation_output.json", "w") as f:
        json.dump(full_promo_data, f, indent=2)
    print("\nSaved simulation results to promo_simulation_output.json")
