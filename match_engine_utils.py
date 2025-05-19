import random
import sqlite3


# --------------------------
# Select a manoeuvre based on match progression
# --------------------------
def select_progressive_manoeuvre(turn):
    from db.utils import db_path

    turn_weight = min(turn / 40, 1.0)

    min_damage = int(3 + (7 * turn_weight))    # 3 → 10
    max_damage = int(6 + (10 * turn_weight))   # 6 → 16
    max_difficulty = int(4 + (6 * turn_weight)) # 4 → 10

    min_damage = max(1, min_damage)
    max_damage = min(16, max_damage)
    max_difficulty = min(10, max_difficulty)

    conn = sqlite3.connect(db_path("manoeuvres.db"))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, type, damage, difficulty
        FROM manoeuvres
        WHERE damage BETWEEN ? AND ?
        AND difficulty <= ?
        ORDER BY RANDOM()
        LIMIT 1
    """, (min_damage, max_damage, max_difficulty))
    move = cursor.fetchone()
    conn.close()

    return move  # (name, type, damage, difficulty)


# --------------------------
# Select a manoeuvre based on wrestler attributes
# --------------------------
def select_weighted_manoeuvre(wrestler, turn):
    import random
    from db.utils import db_path

    # Base weights for manoeuvre types
    base_weights = {
        "strike": 1.0,
        "slam": 1.0,
        "grapple": 1.0,
        "aerial": 1.0,
        "submission": 1.0
    }

    # Adjust weights based on wrestler attributes
    stamina_factor = max(0.5, wrestler["stamina"] / 100)  # Scale stamina to 0.5–1.0
    base_weights["strike"] += wrestler["strike_accuracy"] * 0.1
    base_weights["slam"] += wrestler["powerlifting"] * 0.1
    base_weights["grapple"] += (wrestler["grapple_control"] + wrestler["grip_strength"]) * 0.05
    base_weights["aerial"] += wrestler["aerial_precision"] * 0.1
    base_weights["submission"] += wrestler["mat_transitions"] * 0.1

    # Adjust for height and weight
    if wrestler["height"] > 75 or wrestler["weight"] > 250:
        base_weights["slam"] += 0.5  # Larger wrestlers favour slams
        base_weights["grapple"] += 0.5
    else:
        base_weights["aerial"] += 0.5  # Smaller wrestlers favour aerial moves

    # Normalize weights
    total_weight = sum(base_weights.values())
    normalized_weights = {k: v / total_weight for k, v in base_weights.items()}

    # Select manoeuvre type based on weights
    manoeuvre_type = random.choices(
        population=list(normalized_weights.keys()),
        weights=list(normalized_weights.values()),
        k=1
    )[0]

    # Query manoeuvres database for a move of the selected type
    conn = sqlite3.connect(db_path("manoeuvres.db"))
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT name, type, damage, difficulty
        FROM manoeuvres
        WHERE type = ?
        ORDER BY RANDOM()
        LIMIT 1
        """,
        (manoeuvre_type,)
    )
    move = cursor.fetchone()
    conn.close()

    return move  # (name, type, damage, difficulty)


# --------------------------
# Select a manoeuvre based on wrestler attributes and match phase
# --------------------------
def select_weighted_manoeuvre_with_personality(wrestler, opponent, turn):
    import random
    from db.utils import db_path

    # Determine match phase
    if turn <= 10:
        match_phase = "early"
    elif turn <= 30:
        match_phase = "mid"
    else:
        match_phase = "late"

    # Base weights for manoeuvre types
    base_weights = {
        "strike": 1.0,
        "slam": 1.0,
        "grapple": 1.0,
        "aerial": 1.0,
        "submission": 1.0
    }

    # Adjust weights based on wrestler attributes
    base_weights["strike"] += wrestler["strike_accuracy"] * 0.1
    base_weights["slam"] += wrestler["powerlifting"] * 0.1
    base_weights["grapple"] += (wrestler["grapple_control"] + wrestler["grip_strength"]) * 0.05
    base_weights["aerial"] += wrestler["aerial_precision"] * 0.1
    base_weights["submission"] += wrestler["mat_transitions"] * 0.1

    # Adjust weights based on match phase
    if match_phase == "early":
        base_weights["strike"] += 0.2
        base_weights["grapple"] += 0.2
    elif match_phase == "mid":
        base_weights["slam"] += 0.3
        base_weights["submission"] += 0.3
    elif match_phase == "late":
        base_weights["aerial"] += 0.4
        base_weights["slam"] += 0.4

    # Adjust weights based on matchup (height and weight differences)
    if wrestler["height"] < opponent["height"] or wrestler["weight"] < opponent["weight"]:
        base_weights["aerial"] += 0.5  # Smaller wrestlers favour agility-based moves
    else:
        base_weights["slam"] += 0.5  # Larger wrestlers favour power-based moves
        base_weights["grapple"] += 0.5

    # Adjust weights based on personality and mental attributes
    base_weights["strike"] += wrestler["confidence"] * 0.05
    base_weights["aerial"] += wrestler["risk_assessment"] * 0.05
    base_weights["submission"] += wrestler["determination"] * 0.05
    base_weights["grapple"] += wrestler["focus"] * 0.05
    base_weights["slam"] += wrestler["resilience"] * 0.05

    # Adjust for fan engagement and promo delivery
    if wrestler["fan_engagement"] > 15:
        base_weights["aerial"] += 0.2  # Crowd-pleasing moves
    if wrestler["promo_delivery"] > 15:
        base_weights["strike"] += 0.2  # Charismatic strikes

    # Ensure the database connection and cursor are initialized at the start of the function
    conn = sqlite3.connect(db_path("manoeuvres.db"))
    cursor = conn.cursor()

    # Select manoeuvre type based on weights before querying experience score
    total_weight = sum(base_weights.values())
    normalized_weights = {k: v / total_weight for k, v in base_weights.items()}

    manoeuvre_type = random.choices(
        population=list(normalized_weights.keys()),
        weights=list(normalized_weights.values()),
        k=1
    )[0]

    # Adjust weights based on wrestler-specific experience score
    cursor.execute(
        """
        SELECT experience_score
        FROM wrestler_manoeuvre_experience
        WHERE wrestler_id = ? AND manoeuvre_type = ?
        """,
        (wrestler["id"], manoeuvre_type)
    )
    result = cursor.fetchone()
    if result:
        experience_score = result[0]
        base_weights[manoeuvre_type] += experience_score * 0.1

    # Re-normalize weights after experience adjustment
    total_weight = sum(base_weights.values())
    normalized_weights = {k: v / total_weight for k, v in base_weights.items()}

    # Select manoeuvre type based on weights
    manoeuvre_type = random.choices(
        population=list(normalized_weights.keys()),
        weights=list(normalized_weights.values()),
        k=1
    )[0]

    # Query manoeuvres database for a move of the selected type
    try:
        cursor.execute(
            """
            SELECT name, type, damage, difficulty
            FROM manoeuvres
            WHERE type = ?
            ORDER BY RANDOM()
            LIMIT 1
            """,
            (manoeuvre_type,)
        )
        move = cursor.fetchone()
    finally:
        conn.close()

    return move  # (name, type, damage, difficulty)


# --------------------------
# Determine if a move succeeds
# --------------------------
def move_success(wrestler, move_type, difficulty):
    if move_type == "strike":
        skill = (wrestler["strength"] + wrestler["dexterity"]) / 2
    elif move_type == "slam":
        skill = wrestler["strength"]
    elif move_type == "grapple":
        skill = (wrestler["strength"] + wrestler["intelligence"]) / 2
    elif move_type == "aerial":
        skill = wrestler["dexterity"]
    elif move_type == "submission":
        skill = (wrestler["intelligence"] + wrestler["endurance"]) / 2
    else:
        skill = 10

    # 🧠 Normalize skill to 0–1 scale
    normalized_skill = min(max((skill - 5) / 15, 0), 1)  # assuming 5–20 stat range
    success_chance = 0.3 + (normalized_skill * 0.6) - (difficulty * 0.03)

    # Cap between 5% and 95%
    success_chance = max(0.05, min(success_chance, 0.95))
    
    roll = random.random()
    result = roll < success_chance

    # Calculate how well the move was executed
    execution_score = (success_chance - abs(roll - success_chance)) / success_chance
    execution_score = max(0.0, min(execution_score, 1.0))


    result = random.random() < success_chance
    # print(f"Move success: {result} (chance: {success_chance:.2f} | skill: {skill:.1f} | difficulty: {difficulty})")
    return result, execution_score, success_chance


# --------------------------
# Finisher logic
# --------------------------
def try_finisher(attacker, defender, turn, log_function, update_callback=None):
    base_chance = 0.05 + (turn * 0.015)
    momentum_bonus = 0.15 if attacker.get("momentum") else 0
    desperation_bonus = 0.1 if attacker["stamina"] < 30 else 0
    confidence_penalty = 0.1 if attacker["damage_taken"] > 50 else 0

    final_chance = min(base_chance + momentum_bonus + desperation_bonus - confidence_penalty, 0.9)

    if random.random() >= final_chance:
        return False, None, None, False

    finisher = attacker["finisher"]
    log_function(f"🔥 {attacker['name']} attempts their finisher: {finisher['name']}!")

    if finisher["style"] == "submission":
        if try_submission(attacker, defender, finisher["damage"]):
            log_function(f"💢 {defender['name']} taps out to the {finisher['name']}!")
            return True, attacker, "submission", False
        else:
            log_function(f"{defender['name']} escapes the {finisher['name']}!")
            attacker["momentum"] = False
            if update_callback:
                update_callback(attacker, defender)
            return False, None, None, True
    else:
        resistance = (
            defender["endurance"] +
            defender["stamina"] -
            defender["damage_taken"] +
            random.uniform(0, 20)
        )
        if attacker.get("momentum"):
            resistance -= 5

        if resistance < 25:
            log_function(f"💥 {attacker['name']} lands the {finisher['name']}! That's it!")
            return True, attacker, "pinfall", False
        else:
            log_function(f"{attacker['name']} can't hit the {finisher['name']}!")
            attacker["momentum"] = False
            if update_callback:
                update_callback(attacker, defender)
            return False, None, None, True


# --------------------------
# Submission helper
# --------------------------
def try_submission(attacker, defender, difficulty):
    if "submission_escapes" not in defender:
        defender["submission_escapes"] = 0

    attacker_score = attacker["intelligence"] + random.uniform(0, 5)
    defender_score = defender["endurance"] + random.uniform(0, 5)
    defender_score -= defender["submission_escapes"] * 0.5

    threshold = difficulty + 2
    success = attacker_score > threshold and attacker_score > defender_score

    if success:
        return True
    else:
        defender["submission_escapes"] += 1
        defender["stamina"] = max(0, defender["stamina"] - 3)
        return False


# --------------------------
# Choose starting attacker/defender
# --------------------------
def stalemate_check(wrestler1, wrestler2):
    return (wrestler1, wrestler2) if random.random() < 0.5 else (wrestler2, wrestler1)


# --------------------------
# Translate match quality to crowd reaction
# --------------------------
def get_crowd_reaction(quality):
    if quality >= 90:
        return "🔥 Insane Pop!"
    elif quality >= 75:
        return "👏 Hot Crowd"
    elif quality >= 50:
        return "👌 Mild Interest"
    elif quality >= 30:
        return "😐 Flat Reactions"
    else:
        return "💤 Dead Crowd"

def attempt_finisher(attacker, defender, log_function):
    finisher = attacker["finisher"]
    style = finisher["style"]
    name = finisher["name"]
    damage = finisher["damage"]

    log_function(f"🔥 {attacker['name']} attempts their finisher: {name} ({style})!")

    if style == "submission":
        if try_submission(attacker, defender, damage):
            log_function(f"💢 {defender['name']} taps out to the {name}!")
            return attacker, "submission"
        else:
            log_function(f"{defender['name']} escapes the {name}!")
            return None, None

    # Otherwise: pinfall-style finisher
    resistance = defender["endurance"] + defender["stamina"] - defender["damage_taken"]
    resistance_roll = random.uniform(0, 20)

    if resistance + resistance_roll < 25:
        log_function(f"💥 {attacker['name']} lands the {name}! That's it!")
        return attacker, "pinfall"
    else:
        log_function(f"{defender['name']} kicks out of the {name}!")
        return None, None


def classify_execution_score(score):
    if score < 0.2:
        return "botched"
    elif score < 0.5:
        return "okay"
    elif score < 0.7:
        return "great"
    elif score < 0.9:
        return "fantastic"
    else:
        return "perfect"

def calculate_match_quality(score_sum, types_used, turns, charisma):
    return min(100,
        score_sum +               # execution-based contribution
        len(types_used) * 5 +     # variety bonus
        turns +                   # pacing bonus
        (charisma // 2)           # storytelling/charisma bonus
    )


def get_execution_commentary(grade, wrestler_name, move_name):
    # Remove random skip chance to make commentary more consistent
    lines = {
        "botched": [
            f"{wrestler_name} completely botched the {move_name}.",
            f"That {move_name} did not go to plan.",
            f"{wrestler_name} fumbled the {move_name} — sloppy stuff.",
            f"{move_name}? That was a mess from the start.",
            f"{wrestler_name} was way off on the timing of that {move_name}.",
            f"The crowd winced — that {move_name} was ugly.",
            f"That didn't look good. {wrestler_name} blew the {move_name}.",
            f"Bad execution on the {move_name}. {wrestler_name} will want that one back.",
            f"That {move_name} came apart in mid-air.",
            f"{wrestler_name} completely lost control of the {move_name}.",
        ],
        "okay": [
            f"{wrestler_name} landed the {move_name}, but it lacked impact.",
            f"A serviceable {move_name}, nothing special.",
            f"{wrestler_name} made it work, just about.",
            f"The {move_name} connected, but it wasn't smooth.",
            f"An acceptable effort from {wrestler_name} on that {move_name}.",
            f"The {move_name} gets the job done, if a little flat.",
            f"{wrestler_name} didn't miss, but it was far from crisp.",
            f"The {move_name} could have used more snap.",
            f"A decent attempt, but {wrestler_name} has done better.",
            f"{wrestler_name} didn't sell the {move_name} with much conviction.",
        ],
        "great": [
            f"Good connection from {wrestler_name} with that {move_name}.",
            f"{wrestler_name} delivered the {move_name} with authority.",
            f"That {move_name} landed cleanly and looked strong.",
            f"Solid execution from {wrestler_name} — the {move_name} hit its mark.",
            f"That {move_name} had weight behind it.",
            f"{wrestler_name} found the timing for that {move_name} perfectly.",
            f"Clean technique on that {move_name}.",
            f"The {move_name} was sharp, and the crowd reacted.",
            f"{wrestler_name} brought the goods on that {move_name}.",
            f"The {move_name} had just the right amount of impact.",
        ],
        "fantastic": [
            f"{wrestler_name} made the {move_name} look easy.",
            f"That was an impressive piece of execution from {wrestler_name}.",
            f"Strong delivery — the {move_name} really connected.",
            f"The crowd came alive after that {move_name}.",
            f"{wrestler_name} delivered a picture-perfect {move_name}.",
            f"That's a move they'll be talking about after the show.",
            f"{wrestler_name} hit that {move_name} with confidence and precision.",
            f"That {move_name} was something special.",
            f"{wrestler_name} looked completely in control with that {move_name}.",
            f"That {move_name} shifted the energy in the building.",
        ],
        "perfect": [
            f"{wrestler_name} just hit the cleanest {move_name} of the night.",
            f"Flawless execution on that {move_name}.",
            f"That {move_name} couldn't have been timed better.",
            f"That's how you deliver a {move_name} — perfect form.",
            f"{wrestler_name} made the {move_name} look effortless.",
            f"The technique on that {move_name} was textbook.",
            f"{wrestler_name} couldn't have done that any better.",
            f"That {move_name} belongs in a highlight reel.",
            f"You won't see a smoother {move_name} than that.",
            f"That was world-class execution from {wrestler_name}.",
        ]
    }
    
    options = lines.get(grade, [])
    if not options:
        return None

    return random.choice(options)

import random

import random

def calculate_final_quality(
    match_quality_score,
    types_used,
    winner_charisma,
    execution_buckets,
    drama_score=0,
    crowd_energy=50,
    flow_streak_at_end=0,
    had_highlight=False
):
    # --- Base components
    base = match_quality_score * 0.6
    variety_bonus = len(types_used) * 3
    charisma_bonus = winner_charisma * 0.6
    crowd_bias = random.randint(-5, 5)
    botch_penalty = -5 if execution_buckets.get("botched", 0) >= 3 else 0

    # --- Diminishing drama returns
    if drama_score > 20:
        drama_score -= int((drama_score - 20) * 0.5)

    # --- Crowd expectation penalty
    if crowd_energy > 90:
        expectation_penalty = (crowd_energy - 90) // 5  # stronger penalty if crowd's already hot
    else:
        expectation_penalty = 0

    # --- Flow-based climax bonus
    flow_bonus = 2 if flow_streak_at_end >= 3 else 0

    # --- Highlight moment bonus
    highlight_bonus = 2 if had_highlight else 0

    # --- Clinical but cold penalty (high execution, no drama)
    clinical_penalty = -3 if drama_score < 5 and match_quality_score > 80 else 0

    # --- Final quality
    quality = int(
        base +
        variety_bonus +
        charisma_bonus +
        crowd_bias +
        botch_penalty +
        drama_score +
        flow_bonus +
        highlight_bonus +
        clinical_penalty -
        expectation_penalty
    )

    # 1 in 1000 chance of legendary moment
    if random.random() < 0.001 and quality >= 95:
        quality += 4
    
    if quality >= 99:
        # Require multiple criteria to reach 5★
        if (
            drama_score < 20 or
            execution_buckets.get("perfect", 0) < 3 or
            crowd_energy < 85 or
            not had_highlight or
            flow_streak_at_end < 3
        ):
            quality = 98  # fallback to high 4.5-star match


    return min(100, max(10, quality))

def extract_wrestler_stats(attributes, derived):
    """
    Merge detailed and high-level stats into one clean dict.
    Assumes all detailed stats are always present.
    """

    return {
        # High-level stats
        "strength": derived["strength"]["value"],
        "dexterity": derived["dexterity"]["value"],
        "intelligence": derived["intelligence"]["value"],
        "endurance": derived["endurance"]["value"],
        "charisma": derived["charisma"]["value"],
        
        # All detailed stats
        **attributes
    }

# Update manoeuvre success rate and experience score after a match
def update_manoeuvre_stats(manoeuvre_type, success):
    from db.utils import db_path
    conn = sqlite3.connect(db_path("manoeuvres.db"))
    cursor = conn.cursor()

    # Fetch current stats
    cursor.execute(
        """
        SELECT success_rate, experience_score
        FROM manoeuvres
        WHERE type = ?
        """,
        (manoeuvre_type,)
    )
    result = cursor.fetchone()

    if result:
        success_rate, experience_score = result

        # Update stats
        new_success_rate = (success_rate * 0.9 + (1 if success else 0) * 0.1)
        new_experience_score = experience_score + (1 if success else 0)

        cursor.execute(
            """
            UPDATE manoeuvres
            SET success_rate = ?, experience_score = ?
            WHERE type = ?
            """,
            (new_success_rate, new_experience_score, manoeuvre_type),
        )

    conn.commit()
    conn.close()

def update_wrestler_move_experience(wrestler_id, move_name, success):
    from db.utils import db_path
    conn = sqlite3.connect(db_path("manoeuvres.db"))
    cursor = conn.cursor()

    # Make sure the row exists
    cursor.execute("""
        INSERT OR IGNORE INTO wrestler_move_experience (wrestler_id, move_name)
        VALUES (?, ?)
    """, (wrestler_id, move_name))

    # Update the experience tracking
    cursor.execute("""
        UPDATE wrestler_move_experience
        SET 
            attempt_count = attempt_count + 1,
            success_count = success_count + ?,
            experience_score = experience_score + ?
        WHERE wrestler_id = ? AND move_name = ?
    """, (1 if success else 0, 1 if success else 0, wrestler_id, move_name))

    conn.commit()
    conn.close()


def get_wrestler_id_by_name(name):
    from db.utils import db_path
    conn = sqlite3.connect(db_path("wrestlers.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM wrestlers WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
