import sqlite3
import random
from match_engine_utils import get_execution_commentary, extract_wrestler_stats
from match_engine_utils import calculate_final_quality
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
import json
import time
import logging
import game_state_debug

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


def prepare_wrestler(wrestler):
    """Prepare a wrestler for a match by adding match-specific attributes."""
    prepared = wrestler.copy()
    prepared["stamina"] = 100
    prepared["damage_taken"] = 0
    prepared["momentum"] = False
    return prepared


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
    start_time = time.time()
    logging.info(f"Starting match simulation: {wrestler1['name']} vs {wrestler2['name']}")
    
    # Set up match state
    w1, w2 = prepare_wrestler(wrestler1), prepare_wrestler(wrestler2)
    attacker, defender = w1, w2
    attacking, defending = attacker, defender
    winner, win_type = None, None
    
    # Setup tracking variables
    match_quality_score = 0
    turn = 0
    successful_moves = 0
    had_highlight = False
    drama_score = 0
    sig_moves_landed = 0
    flow_streak = 0
    types_used = set()  # track variety
    execution_buckets = {
        "botched": 0,
        "poor": 0,
        "okay": 0,
        "good": 0,
        "great": 0,
        "fantastic": 0,
        "perfect": 0
    }
    move_log = []
    success_by_wrestler = {w1["name"]: 0, w2["name"]: 0}
    moves_by_phase = {
        "early": [],
        "mid": [],
        "late": [],
        "all": []
    }
    
    logging.debug(f"Initial wrestler stats - {w1['name']}: STR={w1.get('strength', 'N/A')}, DEX={w1.get('dexterity', 'N/A')}, END={w1.get('endurance', 'N/A')}")
    logging.debug(f"Initial wrestler stats - {w2['name']}: STR={w2.get('strength', 'N/A')}, DEX={w2.get('dexterity', 'N/A')}, END={w2.get('endurance', 'N/A')}")
    
    if update_callback:
        update_callback(w1, w2)

    log_function(f"The bell rings as {w1['name']} and {w2['name']} lock up in the center of the ring!")
    log_function(f"Both wrestlers looking to establish dominance early.")

    attacking, defending = stalemate_check(wrestler1, wrestler2)

    for wrestler in (wrestler1, wrestler2):
        wrestler["stamina"] = 100
        wrestler["damage_taken"] = 0
        wrestler["momentum"] = False
    
    crowd_energy = 50 + ((wrestler1.get("entrance_presence", 10) + wrestler2.get("entrance_presence", 10)) // 5)
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

    # Animation delay settings
    move_delay = 0 if fast_mode else 500  # milliseconds
    ui_update_enabled = not fast_mode

    while True:
        use_signature = (
            "signature_moves" in attacking and
            attacking["signature_moves"] and
            random.randint(1, 6) == 1
        )
        
        turn += 1

        # Handle color commentary with consistent timing
        maybe_inject_colour_commentary(turn, attacking, defending, colour_callback)
        
        if ui_update_enabled:
            QApplication.processEvents()

        if use_signature:
            sig = random.choice(attacking["signature_moves"])
            name, move_type, damage, difficulty = sig["name"], sig["type"], sig["damage"], sig["difficulty"]
            log_function(f"✨ {attacking['name']} goes for their signature move: {name}!")
            if move_delay > 0:
                QThread.msleep(move_delay)
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
            if move_delay > 0:
                QThread.msleep(move_delay)

            if is_signature:
                attacking["momentum"] = True
                log_function(f"✅ {attacking['name']} lands their signature!")
                if move_delay > 0:
                    QThread.msleep(move_delay)

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

            if ui_update_enabled:
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

                if ui_update_enabled:
                    QApplication.processEvents()

        # Pinfall attempt check
        if defending["damage_taken"] >= 30 + turn // 3:
            if "finisher" in attacking and attacking["stamina"] > 30 and random.random() < 0.3:
                # Try finisher
                fin_success, fin_winner, fin_type, was_escape = try_finisher(
                    attacking, defending, turn, log_function, update_callback
                )

                if fin_success:
                    winner, finish_type = fin_winner["name"], fin_type
                    log_function(f"🏆 {winner} wins by {finish_type}!")
                    break
                else:
                    if was_escape:
                        false_finish_count += 1
                        drama_score += 3

            elif turn > 40 and random.random() < 0.1:
                # Exhaustion finish (late match)
                if update_callback:
                    update_ui(attacking, defending)
                
                log_function(f"{attacking['name']} goes for a pinfall with a small package!")
                log_function(f"🏆 {attacking['name']} gets the pinfall victory!")
                winner, finish_type = attacking["name"], "pinfall"
                break
    
    # Final bookkeeping and stats
    match_time = time.time() - start_time
    logging.info(f"Match {wrestler1['name']} vs {wrestler2['name']} completed in {match_time:.2f}s")
    logging.info(f"Winner: {winner} via {finish_type}")
    
    flow_streak_at_end = min(flow_streak, 3)  # Cap for purposes of final score
    
    w1_charisma = w1.get("charisma", 10)
    w2_charisma = w2.get("charisma", 10)
    winner_charisma = w1_charisma if winner == w1["name"] else w2_charisma
    
    quality = calculate_final_quality(
        match_quality_score,
        types_used,
        winner_charisma,
        execution_buckets,
        drama_score,
        crowd_energy,
        flow_streak_at_end,
        had_highlight
    )
    
    if quality >= 90:
        log_function(f"🌟 What a match! The crowd is going wild! ({quality})")
    elif quality >= 75:
        log_function(f"👏 That was a great match! The crowd loved it. ({quality})")
    elif quality >= 60:
        log_function(f"👌 A solid match. The crowd is satisfied. ({quality})")
    elif quality >= 45:
        log_function(f"😐 A decent but unremarkable match. ({quality})")
    else:
        log_function(f"😴 That match didn't connect with the crowd. ({quality})")
    
    # Record match in database
    try:
        from db.utils import db_path
        from datetime import datetime
        
        conn = sqlite3.connect(db_path("match_history.db"))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO matches (
                wrestler1_id, wrestler2_id, winner_id, 
                match_type, finish_type, match_quality, match_time
            ) VALUES (
                ?, ?, ?,
                'singles', ?, ?, ?
            )
        """, (
            w1.get("id", 0),
            w2.get("id", 0),
            w1.get("id", 0) if winner == w1["name"] else w2.get("id", 0),
            finish_type,
            quality,
            int(match_time)
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Failed to record match: {e}")
        
    # Update move experience for both wrestlers
    for move_entry in move_log:
        try:
            if move_entry.get("wrestler_id"):
                update_wrestler_move_experience(
                    move_entry["wrestler_id"],
                    move_entry["move_name"],
                    move_entry["success"]
                )
        except Exception as e:
            logging.error(f"Failed to update move experience: {e}")
    
    if stats_callback:
        stats_callback({
            "quality": quality,
            "reaction": get_crowd_reaction(quality),
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
    
    # Return final result data
    return {
        "winner": winner,
        "win_type": finish_type,
        "quality": quality,
        "drama_score": drama_score,
        "false_finishes": false_finish_count,
        "sig_moves_landed": sig_moves_landed,
        "turns": turn,
        "crowd_energy": crowd_energy,
        "execution_summary": execution_buckets,
        "stamina_drain": {
            w1["name"]: 100 - w1["stamina"],
            w2["name"]: 100 - w2["stamina"]
        },
        "match_time": match_time,
        "reversals": reversals_by_wrestler
    }
