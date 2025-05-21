import random
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from match_engine import simulate_match
import time
time.sleep = lambda x: None  # disable sleep for speed

# === Test Config ===
MATCH_COUNT = 100  # Run 10,000 matches
WRESTLER_QUALITY = "mixed"  # options: "low", "high", "mixed"


# -------------------------
# Test Wrestler Builder
# -------------------------
import random


def build_test_wrestlers(quality):
    def random_stat(quality):
        if quality == "high":
            return random.randint(14, 18)
        elif quality == "low":
            return random.randint(5, 9)
        else:  # mixed
            return random.randint(5, 18)

    def wrestler(name):
        attributes = {
            "powerlifting": random_stat(quality),
            "grapple_control": random_stat(quality),
            "grip_strength": random_stat(quality),
            "agility": random_stat(quality),
            "balance": random_stat(quality),
            "flexibility": random_stat(quality),
            "recovery_rate": random_stat(quality),
            "conditioning": random_stat(quality),
            "chain_wrestling": random_stat(quality),
            "mat_transitions": random_stat(quality),
            "submission_technique": random_stat(quality),
            "strike_accuracy": random_stat(quality),
            "brawling_technique": random_stat(quality),
            "aerial_precision": random_stat(quality),
            "counter_timing": random_stat(quality),
            "pressure_handling": random_stat(quality),
            "promo_delivery": random_stat(quality),
            "fan_engagement": random_stat(quality),
            "entrance_presence": random_stat(quality),
            "presence_under_fire": random_stat(quality),
            "confidence": random_stat(quality),
            "focus": random_stat(quality),
            "resilience": random_stat(quality),
            "adaptability": random_stat(quality),
            "risk_assessment": random_stat(quality),
            "loyalty": random_stat(quality),
            "political_instinct": random_stat(quality),
            "determination": random_stat(quality)
        }

        derived = {
            "strength": (attributes["powerlifting"] + attributes["grip_strength"]) // 2,
            "dexterity": (attributes["agility"] + attributes["aerial_precision"]) // 2,
            "intelligence": (attributes["risk_assessment"] + attributes["mat_transitions"]) // 2,
            "endurance": (attributes["conditioning"] + attributes["recovery_rate"] + attributes["determination"]) // 3,
            "charisma": (attributes["fan_engagement"] + attributes["confidence"] + attributes["presence_under_fire"]) // 3
        }

        return {
            "name": name,
            **derived,
            **attributes,
            "stamina": 100,
            "momentum": False,
            "damage_taken": 0,
            "signature_moves": [
                {"name": "Snap Suplex", "type": "slam", "damage": 8, "difficulty": 4},
                {"name": "Springboard Elbow", "type": "strike", "damage": 7, "difficulty": 3},
                {"name": "Rolling Senton", "type": "aerial", "damage": 9, "difficulty": 5}
            ],
            "finisher": {"name": "Finisher", "style": "slam", "damage": 10}
        }

    return [wrestler(f"Wrestler {i+1}") for i in range(20)]

# -------------------------
# Helper: classify into buckets
# -------------------------
def classify_quality(quality):
    if quality >= 99:
        return "five_star"
    elif quality >= 90:
        return "90_to_98"
    elif quality >= 80:
        return "80_to_89"
    elif quality >= 70:
        return "70_to_79"
    elif quality >= 60:
        return "60_to_69"
    elif quality >= 50:
        return "50_to_59"
    elif quality >= 40:
        return "40_to_49"
    elif quality >= 30:
        return "30_to_39"
    else:
        return "under_30"

# -------------------------
# Main Test
# -------------------------
def test_average_quality_over_many_matches():
    wrestlers = build_test_wrestlers(WRESTLER_QUALITY)
    match_count = MATCH_COUNT
    
    top_matches = []

    total_quality = 0
    total_drama = 0
    total_false_finishes = 0
    total_sig_moves = 0
    total_turns = 0
    total_stamina_drain = 0
    total_crowd_energy = 0
    total_reversals = 0

    execution_totals = {
        "botched": 0,
        "okay": 0,
        "great": 0,
        "fantastic": 0,
        "perfect": 0
    }

    buckets = {
        "under_30": 0,
        "30_to_39": 0,
        "40_to_49": 0,
        "50_to_59": 0,
        "60_to_69": 0,
        "70_to_79": 0,
        "80_to_89": 0,
        "90_to_98": 0,
        "five_star": 0
    }

    for _ in range(match_count):
        w1 = random.choice(wrestlers).copy()
        w2 = random.choice(wrestlers).copy()

        result = simulate_match(w1, w2, log_function=lambda x: None, fast_mode=True)

        quality = result["quality"]
        total_quality += quality
        total_drama += result.get("drama_score", 0)
        total_false_finishes += result.get("false_finishes", 0)
        total_sig_moves += result.get("sig_moves_landed", 0)
        total_crowd_energy += result.get("crowd_energy", 50)
        total_turns += result.get("turns", 0)
        total_reversals += result.get("reversals", {}).get(w1["name"], 0) + result.get("reversals", {}).get(w2["name"], 0)

        for key in execution_totals:
            execution_totals[key] += result["execution_summary"].get(key, 0)

        bucket = classify_quality(quality)
        buckets[bucket] += 1

        s1 = result["stamina_drain"][w1["name"]]
        s2 = result["stamina_drain"][w2["name"]]
        total_stamina_drain += (s1 + s2) / 2
        
        top_matches.append({
            "w1": w1["name"],
            "w2": w2["name"],
            "quality": result["quality"],
            "drama": result["drama_score"]
        })


    # Averages
    avg_quality = total_quality / match_count
    avg_drama = total_drama / match_count
    avg_false = total_false_finishes / match_count
    avg_signatures = total_sig_moves / match_count
    avg_turns = total_turns / match_count
    avg_stamina = total_stamina_drain / match_count
    avg_crowd = total_crowd_energy / match_count
    avg_reversals = total_reversals / match_count

    # Output
    print(f"\n--- Match Simulation Results ---")
    print(f"Matches Simulated: {match_count}")
    print(f"Average Match Quality: {avg_quality:.2f}")
    print(f"Average Drama Score: {avg_drama:.2f}")
    print(f"Average False Finishes: {avg_false:.2f}")
    print(f"Average Signatures Landed: {avg_signatures:.2f}")
    print(f"Average Match Length: {avg_turns:.2f} turns")
    print(f"Average Stamina Drain: {avg_stamina:.2f}")
    print(f"Average Crowd Energy: {avg_crowd:.2f}")
    print(f"Average Reversals: {avg_reversals:.2f}")
    print(f"\nExecution Breakdown (total):")
    for k, v in execution_totals.items():
        print(f"  {k.capitalize()}: {v}")

    top_matches.sort(key=lambda m: m["quality"], reverse=True)
    print("\nTop 10 Matches by Quality:")
    for m in top_matches[:10]:
        print(f"{m['w1']} vs {m['w2']} — {m['quality']} quality ({m['drama']} drama)")


    print(f"\nMatch Quality Distribution:")
    for k, v in buckets.items():
        pct = (v / match_count) * 100
        label = k.replace("_", " ").title()
        print(f"  {label}: {v} matches ({pct:.1f}%)")
        
    # Sanity check (not strict pass/fail yet)
    # assert 45 < avg_quality < 90, "Average match quality is out of expected range"

if __name__ == "__main__":
    # Disable QThread.msleep to skip delays
    from PyQt5.QtCore import QThread
    original_msleep = QThread.msleep
    QThread.msleep = lambda x: None
    
    # Disable QApplication.processEvents to skip UI updates
    from PyQt5.QtWidgets import QApplication
    original_process_events = QApplication.processEvents
    QApplication.processEvents = lambda: None
    
    # Run the test
    print("Starting match simulation test with delays disabled...")
    start_time = time.time()
    test_average_quality_over_many_matches()
    total_time = time.time() - start_time
    print(f"\nTotal execution time: {total_time:.2f} seconds")
    
    # Restore original methods
    QThread.msleep = original_msleep
    QApplication.processEvents = original_process_events
