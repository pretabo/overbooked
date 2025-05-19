import sqlite3
import random
from match_engine_utils import get_execution_commentary, extract_wrestler_stats
from match_engine_utils import calculate_final_quality
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread

import random
import time
from match_engine_utils import (
    select_progressive_manoeuvre,
    move_success,
    try_finisher,
    stalemate_check,
    get_crowd_reaction,
    classify_execution_score
)
from db.utils import db_path
from ui.stats_utils import calculate_high_level_stats_with_grades


def get_all_wrestlers():
    conn = sqlite3.connect(db_path("wrestlers.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM wrestlers ORDER BY name")
    wrestlers = cursor.fetchall()
    conn.close()
    return wrestlers  


def load_wrestler_by_id(wrestler_id):
    conn = sqlite3.connect(db_path("wrestlers.db"))
    conn.execute(f"ATTACH DATABASE '{db_path('finishers.db')}' AS fdb")
    cursor = conn.cursor()

    # Get meta + finisher info
    cursor.execute("""
        SELECT w.name, w.reputation, w.condition,
            f.name AS finisher_name, f.style, f.damage
        FROM wrestlers w
        JOIN finishers f ON f.id = w.finisher_id
        WHERE w.id = ?
    """, (wrestler_id,))
    row = cursor.fetchone()

    if not row:
        return None

    name, reputation, condition, fin_name, fin_style, fin_dmg = row

    # Get detailed attributes
    cursor.execute("SELECT * FROM wrestler_attributes WHERE wrestler_id = ?", (wrestler_id,))
    attr_row = cursor.fetchone()
    attr_names = [desc[0] for desc in cursor.description][1:]
    attributes = dict(zip(attr_names, attr_row[1:]))

    # Calculate high-level stats
    derived = calculate_high_level_stats_with_grades(attributes)

    conn.close()

    signature_moves = load_signature_moves_for_wrestler(wrestler_id)

    return {
        "id": wrestler_id,
        "name": name,
        "reputation": reputation,
        "condition": condition,
        "finisher": {
            "name": fin_name,
            "style": fin_style,
            "damage": fin_dmg
        },
        "signature_moves": signature_moves,
        **extract_wrestler_stats(attributes, derived),
    }

def load_signature_moves_for_wrestler(wrestler_id):
    conn = sqlite3.connect(db_path("wrestlers.db"))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.name, s.type, s.damage, s.difficulty
        FROM signature_moves s
        JOIN wrestler_signature_moves wsm ON s.id = wsm.signature_move_id
        WHERE wsm.wrestler_id = ?
    """, (wrestler_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"name": r[0], "type": r[1], "damage": r[2], "difficulty": r[3]} for r in rows]


def maybe_inject_colour_commentary(turn, attacking, defending, colour_callback):
    # Only inject color commentary every 4th turn for consistency
    if turn % 4 != 0 or not colour_callback:
        return
    
    from db.commentary_utils import get_commentary_line
    line = get_commentary_line("colour", w1=attacking["name"], w2=defending["name"])
    if line:
        colour_callback(line)



# --------------------------
# Simulate a full match
# --------------------------
def simulate_match(wrestler1, wrestler2, log_function=print, update_callback=None, colour_callback=None, stats_callback=None, fast_mode=False):
    """Simulate a wrestling match between two wrestlers."""
    log_function("🎮 MATCH START 🎮")
    QThread.msleep(1000)
    
    log_function(f"{wrestler1['name']} vs. {wrestler2['name']}")
    QThread.msleep(1000)

    attacking, defending = stalemate_check(wrestler1, wrestler2)

    for wrestler in (wrestler1, wrestler2):
        wrestler["stamina"] = 100
        wrestler["damage_taken"] = 0
        wrestler["momentum"] = False
    
    crowd_energy = 50 + ((wrestler1.get("entrance_presence", 10) + wrestler2.get("entrance_presence", 10)) // 5)
    match_quality_score = 0
    execution_buckets = {
        "botched": 0,
        "okay": 0,
        "great": 0,
        "fantastic": 0,
        "perfect": 0
    }
    moves_by_phase = {
        "early": [],
        "mid": [],
        "late": [],
        "all": []
    }
    move_log = []  # Track each move's full details by wrestler


    types_used = set()
    turn = 0
    winner = None
    finish_type = None
    last_reversal_turn = -5

    # Match stats
    successful_moves = 0
    missed_moves = 0
    reversal_count = 0
    
    # quality calculator
    drama_score = 0
    false_finish_count = 0
    sig_moves_landed = 0
    flow_streak = 0
    flow_streak_at_end = 0
    had_highlight = False



    # Per-wrestler tracking
    success_by_wrestler = {wrestler1["name"]: 0, wrestler2["name"]: 0}
    misses_by_wrestler = {wrestler1["name"]: 0, wrestler2["name"]: 0}
    reversals_by_wrestler = {wrestler1["name"]: 0, wrestler2["name"]: 0}

    original_left = wrestler1["name"]

    def update_ui(att, def_):
        if update_callback:
            if att["name"] == original_left:
                update_callback(att, def_)
            else:
                update_callback(def_, att)

    while True:
        use_signature = (
            "signature_moves" in attacking and
            attacking["signature_moves"] and
            random.randint(1, 6) == 1
        )
        
        turn += 1

        # Handle color commentary with consistent timing
        maybe_inject_colour_commentary(turn, attacking, defending, colour_callback)
        
        if not fast_mode:
            QApplication.processEvents()

        if use_signature:
            sig = random.choice(attacking["signature_moves"])
            name, move_type, damage, difficulty = sig["name"], sig["type"], sig["damage"], sig["difficulty"]
            log_function(f"✨ {attacking['name']} goes for their signature move: {name}!")
            QThread.msleep(500)
        else:
            name, move_type, damage, difficulty = select_progressive_manoeuvre(turn)

        is_signature = use_signature
        types_used.add(move_type)
        success, exec_score, success_chance = move_success(attacking, move_type, difficulty)
        
        # Track move usage
        move_log.append({
            "wrestler_id": attacking.get("id", None),
            "move_name": name,
            "success": success
        })


        # Determine match phase
        if turn <= 10:
            phase = "early"
        elif turn <= 30:
            phase = "mid"
        else:
            phase = "late"

        # Log the move used
        moves_by_phase[phase].append({
            "type": move_type,
            "success": success
        })
        moves_by_phase["all"].append({
            "type": move_type,
            "success": success
        })


        # print success chance and execution score
        grade = classify_execution_score(exec_score)
        # print(f"Execution rating: {grade.upper()} ({exec_score:.2f})")
        # print(f"Success chance: {success_chance:.2f} | Move: {move_type} (diff {difficulty})")
        # print(f"Move name: {name}")

        if success:
            log_function(f"{attacking['name']} successfully uses {name}!")
            QThread.msleep(500)

            if is_signature:
                attacking["momentum"] = True
                log_function(f"✅ {attacking['name']} lands their signature!")
                QThread.msleep(500)

            # count successful moves
            successful_moves += 1
            success_by_wrestler[attacking["name"]] += 1
            match_quality_score += int(exec_score * 10)

            # calculate execution score
            bucket = classify_execution_score(exec_score)
            execution_buckets[bucket] += 1
            
            # Signature drama bonus
            if is_signature:
                sig_moves_landed += 1
                if turn > 10:
                    drama_score += 2
                else:
                    drama_score += 1

            # Comeback tracking
            if grade in ("great", "fantastic", "perfect"):
                flow_streak += 1
                if flow_streak == 3:
                    drama_score += 2
            else:
                flow_streak = 0

            # Track highlight-worthy moment
            if exec_score >= 0.95:
                had_highlight = True


            # Stamina drain
            base_drain = max(1, 6 - int(attacking["endurance"] / 2))
            extra_drain = 0
            if exec_score < 0.3:
                extra_drain = 3  # extra drain for botched
            elif exec_score < 0.6:
                extra_drain = 1  # mild penalty for okay
            attacking["stamina"] = max(0, attacking["stamina"] - (base_drain + extra_drain))
            
            # damage calculation
            defending["damage_taken"] += damage
            
            grade = classify_execution_score(exec_score)

            # Crowd energy adjustment
            # -- Crowd energy from execution quality
            if grade == "botched":
                confidence = attacking.get("confidence", 10)
                soften = max(0, (confidence - 10) // 5)  # Up to -1 penalty reduction
                crowd_energy -= (2 - soften)
            elif grade == "perfect":
                crowd_energy += 3
            elif grade == "fantastic":
                crowd_energy += 2
            elif grade == "great":
                crowd_energy += 1

            # -- Signature move late in match
            if is_signature and turn > 10:
                fan_engage = attacking.get("fan_engagement", 10)
                charisma = attacking.get("charisma", 10)
                crowd_energy += (fan_engage + charisma) // 30

            # -- Comeback streak pop
            if flow_streak == 3:
                under_fire = attacking.get("presence_under_fire", 10)
                if under_fire >= 15:
                    crowd_energy += 1
            # -- Stat-based passive buffs
            if attacking.get("fan_engagement", 10) >= 15:
                crowd_energy += 1
            if attacking.get("charisma", 10) >= 15:
                crowd_energy += 1
            if attacking.get("confidence", 10) >= 15:
                crowd_energy += 1

            # -- Stat-based passive debuffs
            if attacking.get("fan_engagement", 10) < 8:
                crowd_energy -= 1
            if attacking.get("charisma", 10) < 8:
                crowd_energy -= 1
            if grade == "botched" and attacking.get("confidence", 10) < 8:
                crowd_energy -= 1

            # Clamp to 0–100
            crowd_energy = max(0, min(100, crowd_energy))
            
            commentary = get_execution_commentary(grade, attacking["name"], name)
            if commentary:
                log_function(commentary)



            update_ui(attacking, defending)
            
            if stats_callback:
                stats_callback({
                    "quality": match_quality_score,
                    "reaction": get_crowd_reaction(match_quality_score),
                    "hits": success_by_wrestler,
                    "reversals": reversals_by_wrestler,
                    "misses": misses_by_wrestler,
                    "successes": success_by_wrestler,
                    "flow_streak": flow_streak,
                    "drama_score": drama_score,
                    "false_finishes": false_finish_count,
                    "sig_moves_landed": sig_moves_landed,
                    "turns": turn
                })

            QApplication.processEvents()
        else:
            # Reversal check
            reversal_chance = max(0.1, 0.5 - (turn * 0.015))
            fatigue_penalty = (1 - (defending["stamina"] / 100)) * 0.2
            reversal_chance -= fatigue_penalty
            reversal_chance += defending["dexterity"] / 200
            # print(f"Reversal chance: {reversal_chance:.2f} (fatigue: {fatigue_penalty:.2f}, dexterity: {defending['dexterity'] / 200:.2f})")

            type_bonus = {
                "strike": -0.05,
                "slam": 0.00,
                "grapple": 0.02,
                "submission": 0.05,
                "aerial": 0.08
            }
            reversal_chance += type_bonus.get(move_type, 0)


            if turn - last_reversal_turn >= 3 and random.random() < reversal_chance:
                log_function(f"{defending['name']} reverses the {name}!")


                reversal_count += 1
                reversals_by_wrestler[defending["name"]] += 1
                attacking, defending = defending, attacking
                last_reversal_turn = turn
                update_ui(attacking, defending)
                if stats_callback:
                    stats_callback({
                        "quality": match_quality_score,
                        "reaction": get_crowd_reaction(match_quality_score),
                        "hits": success_by_wrestler,
                        "reversals": reversals_by_wrestler,
                        "misses": misses_by_wrestler,
                        "successes": success_by_wrestler,
                        "flow_streak": flow_streak,
                        "drama_score": drama_score,
                        "false_finishes": false_finish_count,
                        "sig_moves_landed": sig_moves_landed,
                        "turns": turn
                    })

                QApplication.processEvents()

                continue
            else:
                log_function(f"{attacking['name']}'s {name} misses!")
                # print(f"Missed move: {name} (attacker's {move_type} vs. difficulty {difficulty})")

                missed_moves += 1
                misses_by_wrestler[attacking["name"]] += 1
                
                # stamina drain
                attacking["stamina"] = max(0, attacking["stamina"] - 2)
                
                attacking, defending = stalemate_check(attacking, defending)
                update_ui(attacking, defending)
                if stats_callback:
                    stats_callback({
                        "quality": match_quality_score,
                        "reaction": get_crowd_reaction(match_quality_score),
                        "hits": success_by_wrestler,
                        "reversals": reversals_by_wrestler,
                        "misses": misses_by_wrestler,
                        "successes": success_by_wrestler,
                        "flow_streak": flow_streak,
                        "drama_score": drama_score,
                        "false_finishes": false_finish_count,
                        "sig_moves_landed": sig_moves_landed,
                        "turns": turn
                    })

                QApplication.processEvents()
                continue

        success, winner, finish_type, switch_roles = try_finisher(attacking, defending, turn, log_function, update_callback)
        if success:
            break
        elif switch_roles:
            attacking, defending = defending, attacking
            false_finish_count += 1
            drama_score += 2


    # Add a delay before showing the winner to ensure commentary is complete
    if not fast_mode:
        time.sleep(1.5)
    
    log_function("\n🏁 MATCH ENDS!")
    log_function(f"🏆 WINNER: {winner['name']} by {finish_type}!")

    flow_streak_at_end = flow_streak
    quality = calculate_final_quality(
        match_quality_score,
        types_used,
        winner["charisma"],
        execution_buckets,
        drama_score=drama_score,
        crowd_energy=crowd_energy,
        flow_streak_at_end=flow_streak_at_end,
        had_highlight=had_highlight
    )

    log_function(f"⭐ Match Quality: {quality:.1f}/100")
    log_function(f"🎤 Crowd Reaction: {get_crowd_reaction(quality)}")

    return {
        "winner": winner["name"],
        "ending_move": winner["finisher"]["name"],
        "quality": quality,
        "reaction": get_crowd_reaction(quality),
        "reversals": reversals_by_wrestler,
        "successes": successful_moves,
        "crowd_energy": crowd_energy,
        "misses": misses_by_wrestler,
        "damage_dealt": {
            wrestler1["name"]: wrestler2["damage_taken"],
            wrestler2["name"]: wrestler1["damage_taken"]
        },
        "stamina_drain": {
            wrestler1["name"]: 100 - wrestler1["stamina"],
            wrestler2["name"]: 100 - wrestler2["stamina"]
        },
        "hits": success_by_wrestler,
        "misses_by_wrestler": misses_by_wrestler,
        "reversals_by_wrestler": reversals_by_wrestler,
        "execution_summary": execution_buckets,
        "drama_score": drama_score,
        "false_finishes": false_finish_count,
        "sig_moves_landed": sig_moves_landed,
        "turns": turn,
        "moves": moves_by_phase,
        "used_manoeuvres": move_log

    }
