
import sys
import os
import random
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from promo.promo_engine import PromoEngine

# --- Config ---
PROMO_COUNT = 10000
BEATS = 35

# --- Data Collection ---
promo_results = []
momentum_flow = [0 for _ in range(BEATS)]
interruption_count = 0
interruption_by_relationship = {"hostile": 0, "neutral": 0, "friendly": 0}

type_counts = {
    "Self-Promo": 0,
    "Call Out": 0,
    "Friendly Promo": 0,
    "Storyline Build": 0
}
type_ratings = {k: [] for k in type_counts.keys()}
archetype_ratings = {
    "Weak": [],
    "Regular": [],
    "Talented": []
}

archetype_momentum = {
    "Weak": [0 for _ in range(BEATS)],
    "Regular": [0 for _ in range(BEATS)],
    "Talented": [0 for _ in range(BEATS)],
}
archetype_counts = {
    "Weak": 0,
    "Regular": 0,
    "Talented": 0,
}
archetype_confidence = {
    "Weak": [0 for _ in range(BEATS)],
    "Regular": [0 for _ in range(BEATS)],
    "Talented": [0 for _ in range(BEATS)],
}
archetype_scores = {
    "Weak": [0 for _ in range(BEATS)],
    "Regular": [0 for _ in range(BEATS)],
    "Talented": [0 for _ in range(BEATS)],
}

interrupted_ratings = []
non_interrupted_ratings = []
ending_beats_by_archetype = {"Weak": [], "Regular": [], "Talented": []}
event_crowd_timeline = []

active_promos_by_archetype_and_beat = {
    "Weak": [0 for _ in range(BEATS)],
    "Regular": [0 for _ in range(BEATS)],
    "Talented": [0 for _ in range(BEATS)],
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
            "reputation": random.randint(3, 6)
        },
        "Regular": {
            "promo_delivery": random.randint(8, 12),
            "fan_engagement": random.randint(8, 12),
            "entrance_presence": random.randint(8, 12),
            "presence_under_fire": random.randint(8, 12),
            "confidence": random.randint(8, 12),
            "reputation": random.randint(8, 12)
        },
        "Talented": {
            "promo_delivery": random.randint(15, 20),
            "fan_engagement": random.randint(15, 20),
            "entrance_presence": random.randint(15, 20),
            "presence_under_fire": random.randint(15, 20),
            "confidence": random.randint(15, 20),
            "reputation": random.randint(15, 20)
        },
    }
    attributes = attribute_sets[archetype]
    return {"id": id or random.randint(1000, 9999), "name": name, "attributes": attributes}

def classify_relationship():
    roll = random.random()
    if roll < 0.25:
        return "hostile"
    elif roll < 0.5:
        return "friendly"
    else:
        return "neutral"

def run_simulations():
    global interruption_count
    event_crowd_reaction = 50.0

    for _ in range(PROMO_COUNT):
        archetype = random.choice(["Weak", "Regular", "Talented"])
        wrestler = generate_test_wrestler("Main", archetype=archetype)
        opponent = generate_test_wrestler("Target", archetype=random.choice(["Regular", "Talented"]))
        promo_type = random.choice(list(type_counts.keys()))
        relationship_type = classify_relationship()

        engine = PromoEngine(
            wrestler=wrestler,
            # opponent=opponent,
            # promo_type=promo_type,
            # setting="in-ring",
            crowd_reaction=event_crowd_reaction,
        )
        result = engine.simulate()
        event_crowd_reaction = result.get("crowd_reaction", event_crowd_reaction)

        promo_results.append({
            "score": result["final_rating"],
            "archetype": archetype,
            "interrupted": result["interrupted"],
            "promo_type": promo_type
        })

        type_counts[promo_type] += 1
        type_ratings[promo_type].append(result["final_rating"])
        archetype_ratings[archetype].append(result["final_rating"])
        ending_beats_by_archetype[archetype].append(len(result["beats"]))

        for i, beat in enumerate(result["beats"]):
            if i >= BEATS:
                continue
            archetype_momentum[archetype][i] += beat["momentum"]
            archetype_confidence[archetype][i] += beat["confidence"]
            archetype_scores[archetype][i] += beat["score"]
            active_promos_by_archetype_and_beat[archetype][i] += 1
            momentum_flow[i] += beat["momentum"]

        if result["interrupted"]:
            interruption_count += 1
            interrupted_ratings.append(result["final_rating"])
            interruption_by_relationship[relationship_type] += 1
        else:
            non_interrupted_ratings.append(result["final_rating"])

        event_crowd_timeline.append(event_crowd_reaction)

def print_analysis():
    avg_rating = sum(p["score"] for p in promo_results) / len(promo_results)
    interruption_rate = (interruption_count / PROMO_COUNT) * 100
    print("\n--- Promo Simulation Summary ---")
    print(f"Promos Simulated: {PROMO_COUNT}")
    print(f"Average Promo Rating: {avg_rating:.2f}")
    print(f"Interruption Rate: {interruption_rate:.2f}%")

    print("\n--- Breakdown by Promo Type ---")
    for t, count in type_counts.items():
        avg = sum(type_ratings[t]) / count if count else 0
        print(f"{t}: {avg:.2f} rating ({count} promos)")

    print("\n--- Interruption Breakdown by Relationship ---")
    for rel, count in interruption_by_relationship.items():
        print(f"{rel.title()}: {count} interruptions")

    print("\n--- Archetype Breakdown ---")
    for arch in ["Weak", "Regular", "Talented"]:
        scores = archetype_ratings[arch]
        if scores:
            avg = sum(scores) / len(scores)
            print(f"{arch}: {avg:.2f} rating ({len(scores)} promos)")

def print_beat_by_beat_summary():
    print("\n--- Beat-by-Beat Summary ---")
    for i in range(BEATS):
        print(f"Beat {i+1}")
        for arch in ["Weak", "Regular", "Talented"]:
            active = active_promos_by_archetype_and_beat[arch][i]
            if active > 0:
                mom = archetype_momentum[arch][i] / active
                conf = archetype_confidence[arch][i] / active
                score = archetype_scores[arch][i] / active
                print(f"{arch:<9}| Active: {active:>4} | Momentum: {mom:>5.2f} | Confidence: {conf:>5.2f} | Score: {score:>5.2f}")
            else:
                print(f"{arch:<9}| No active promos")

# --- Run ---
if __name__ == "__main__":
    run_simulations()
    print_analysis()
    print_beat_by_beat_summary()
