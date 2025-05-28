import random
import time
import sqlite3
from match_engine_utils import (
    select_progressive_manoeuvre,
    move_success,
    try_finisher,
    stalemate_check,
    get_crowd_reaction,
    classify_execution_score,
    calculate_final_quality
)
from match_engine import load_wrestler_by_id, get_all_wrestlers
from db.utils import db_path

def prepare_wrestler(wrestler):
    """Prepare a wrestler for a match by adding match-specific attributes."""
    prepared = wrestler.copy()
    prepared["stamina"] = 100
    prepared["damage_taken"] = 0
    prepared["momentum"] = False
    return prepared

def simulate_match_fast(wrestler1, wrestler2):
    """
    Optimized match simulation with no UI updates or delays.
    This is a stripped-down version of the main match engine, focused on performance.
    """
    # Set up match state
    w1, w2 = prepare_wrestler(wrestler1), prepare_wrestler(wrestler2)
    attacking, defending = stalemate_check(wrestler1, wrestler2)
    attacking = prepare_wrestler(attacking)
    defending = prepare_wrestler(defending)
    winner, win_type = None, None
    
    # Setup tracking variables
    match_quality_score = 0
    turn = 0
    successful_moves = 0
    had_highlight = False
    drama_score = 0
    sig_moves_landed = 0
    flow_streak = 0
    types_used = set()
    execution_buckets = {
        "botched": 0,
        "poor": 0,
        "okay": 0,
        "good": 0,
        "great": 0,
        "fantastic": 0,
        "perfect": 0
    }
    success_by_wrestler = {w1["name"]: 0, w2["name"]: 0}
    misses_by_wrestler = {w1["name"]: 0, w2["name"]: 0}
    reversals_by_wrestler = {w1["name"]: 0, w2["name"]: 0}
    
    last_reversal_turn = -5
    reversal_count = 0
    false_finish_count = 0
    crowd_energy = 50 + ((wrestler1.get("entrance_presence", 10) + wrestler2.get("entrance_presence", 10)) // 5)
    
    # Main match loop
    while True:
        use_signature = (
            "signature_moves" in attacking and
            attacking["signature_moves"] and
            random.randint(1, 6) == 1
        )
        
        turn += 1
        
        if use_signature:
            sig = random.choice(attacking["signature_moves"])
            name, move_type, damage, difficulty = sig["name"], sig["type"], sig["damage"], sig["difficulty"]
        else:
            name, move_type, damage, difficulty = select_progressive_manoeuvre(turn)
            
        is_signature = use_signature
        types_used.add(move_type)
        success, exec_score, success_chance = move_success(attacking, move_type, difficulty)
        
        # Determine match phase for tracking
        if turn <= 10:
            phase = "early"
        elif turn <= 30:
            phase = "mid"
        else:
            phase = "late"
            
        # Process move result
        if success:
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
            if bucket in ("great", "fantastic", "perfect"):
                flow_streak += 1
                if flow_streak == 3:
                    drama_score += 2
            else:
                flow_streak = 0
                
            # Track highlight-worthy moment
            if exec_score >= 0.95:
                had_highlight = True
                
            # Stamina drain
            base_drain = max(1, 6 - int(attacking.get("endurance", 10) / 2))
            extra_drain = 0
            if exec_score < 0.3:
                extra_drain = 3  # extra drain for botched
            elif exec_score < 0.6:
                extra_drain = 1  # mild penalty for okay
            attacking["stamina"] = max(0, attacking["stamina"] - (base_drain + extra_drain))
            
            # damage calculation
            defending["damage_taken"] += damage
            
            # Crowd energy adjustment based on execution
            if bucket == "botched":
                confidence = attacking.get("confidence", 10)
                soften = max(0, (confidence - 10) // 5)
                crowd_energy -= (2 - soften)
            elif bucket == "perfect":
                crowd_energy += 3
            elif bucket == "fantastic":
                crowd_energy += 2
            elif bucket == "great":
                crowd_energy += 1
                
            # Signature move bonus
            if is_signature and turn > 10:
                fan_engage = attacking.get("fan_engagement", 10)
                charisma = attacking.get("charisma", 10)
                crowd_energy += (fan_engage + charisma) // 30
                
            # Stat-based energy adjustments
            if attacking.get("fan_engagement", 10) >= 15:
                crowd_energy += 1
            if attacking.get("charisma", 10) >= 15:
                crowd_energy += 1
                
            # Clamp crowd energy
            crowd_energy = max(0, min(100, crowd_energy))
            
            # Check for match end
            if defending["damage_taken"] >= 30 + turn // 3:
                # Finisher attempt check
                if attacking["stamina"] > 30 and random.random() < 0.5 and "finisher" in attacking:
                    fin_success, fin_escape = try_finisher(attacking, defending, turn, lambda x: None)
                    if fin_success:
                        winner = attacking["name"]
                        win_type = "pinfall" if random.random() < 0.8 else "submission"
                        break
                    else:
                        false_finish_count += 1
                        drama_score += 1
                elif turn > 40 and random.random() < 0.1:
                    # Exhaustion finish
                    winner = attacking["name"]
                    win_type = "pinfall"
                    break
        else:
            # Miss tracking
            misses_by_wrestler[attacking["name"]] += 1
            
            # Reversal check
            reversal_chance = max(0.1, 0.5 - (turn * 0.015))
            fatigue_penalty = (1 - (defending["stamina"] / 100)) * 0.2
            reversal_chance -= fatigue_penalty
            reversal_chance += defending.get("dexterity", 10) / 200
            
            # Type bonuses for reversal
            type_bonus = {
                "strike": -0.05,
                "slam": 0.00,
                "grapple": 0.02,
                "submission": 0.05,
                "aerial": 0.08
            }
            reversal_chance += type_bonus.get(move_type, 0)
            
            # Process reversal
            if turn - last_reversal_turn >= 3 and random.random() < reversal_chance:
                reversal_count += 1
                reversals_by_wrestler[defending["name"]] += 1
                attacking, defending = defending, attacking
                last_reversal_turn = turn
    
    # Calculate final match quality
    flow_streak_at_end = min(flow_streak, 3)
    match_quality = calculate_final_quality(
        match_quality_score,
        types_used,
        winner_charisma=wrestler1.get("charisma", 10) if winner == wrestler1["name"] else wrestler2.get("charisma", 10),
        execution_buckets=execution_buckets,
        drama_score=drama_score,
        crowd_energy=crowd_energy,
        flow_streak_at_end=flow_streak_at_end,
        had_highlight=had_highlight
    )
    
    # Return match result
    return {
        "winner": winner,
        "finish_type": win_type,
        "quality": match_quality,
        "drama_score": drama_score,
        "false_finishes": false_finish_count,
        "sig_moves_landed": sig_moves_landed,
        "turns": turn,
        "crowd_energy": crowd_energy,
        "stamina_drain": {
            w1["name"]: 100 - w1["stamina"],
            w2["name"]: 100 - w2["stamina"]
        },
        "execution_summary": execution_buckets,
        "reversals": reversals_by_wrestler
    }


def run_bulk_matches(count, progress_callback=None):
    """Run multiple matches in bulk for testing and statistics gathering."""
    start_time = time.time()
    
    all_wrestlers = get_all_wrestlers()
    if not all_wrestlers:
        raise ValueError("No wrestlers found in database")
        
    results = []
    
    for i in range(count):
        # Select random wrestlers
        w1_id, w1_name = random.choice(all_wrestlers)
        w2_id, w2_name = random.choice(all_wrestlers)
        
        # Load wrestler data
        wrestler1 = load_wrestler_by_id(w1_id)
        wrestler2 = load_wrestler_by_id(w2_id)
        
        if not wrestler1 or not wrestler2:
            continue
            
        # Run match
        match_start = time.time()
        result = simulate_match_fast(wrestler1, wrestler2)
        match_time = time.time() - match_start
        
        result["time_taken"] = match_time
        result["wrestlers"] = [wrestler1["name"], wrestler2["name"]]
        results.append(result)
        
        if progress_callback and i % max(1, count // 10) == 0:
            progress_callback(i, count, result)
            
    total_time = time.time() - start_time
    
    # Calculate statistics
    avg_time = total_time / count
    avg_quality = sum(r["quality"] for r in results) / count
    avg_turns = sum(r["turns"] for r in results) / count
    
    summary = {
        "total_matches": count,
        "total_time": total_time,
        "avg_time_per_match": avg_time,
        "avg_quality": avg_quality,
        "avg_turns": avg_turns,
        "results": results
    }
    
    return summary

if __name__ == "__main__":
    # Test run
    match_count = 100
    print(f"Running {match_count} optimized matches...")
    
    def progress(i, total, result):
        print(f"Match {i+1}/{total}: {result['wrestlers'][0]} vs {result['wrestlers'][1]} - {result['turns']} turns, {result['time_taken']:.3f}s")
    
    summary = run_bulk_matches(match_count, progress)
    
    print("\n=== Results ===")
    print(f"Total time: {summary['total_time']:.3f} seconds")
    print(f"Average time per match: {summary['avg_time_per_match']:.3f} seconds")
    print(f"Average match quality: {summary['avg_quality']:.2f}")
    print(f"Average match length: {summary['avg_turns']:.1f} turns") 