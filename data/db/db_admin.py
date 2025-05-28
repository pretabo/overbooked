import sqlite3
from db.utils import db_path

def add_wrestler(
    name,
    strength,
    dexterity,
    endurance,
    intelligence,
    charisma,
    reputation,
    condition,
    finisher_name,
    finisher_style,
    finisher_damage,
    signature_moves  # List of dicts: [{name, type, damage, difficulty}]
):
    # 1. Ensure finisher exists
    conn = sqlite3.connect(db_path("wrestlers.db"))
    conn.execute(f"ATTACH DATABASE '{db_path('finishers.db')}' AS fdb")
    cursor = conn.cursor()

    # Check if finisher exists
    cursor.execute("SELECT id FROM fdb.finishers WHERE name = ?", (finisher_name,))
    row = cursor.fetchone()
    if row:
        finisher_id = row[0]
    else:
        # Insert into finishers.db
        cursor.execute(
            "INSERT INTO fdb.finishers (name, style, damage) VALUES (?, ?, ?)",
            (finisher_name, finisher_style, finisher_damage)
        )
        finisher_id = cursor.lastrowid

    # 2. Insert wrestler
    cursor.execute("""
        INSERT INTO wrestlers (
            name, strength, dexterity, endurance,
            intelligence, charisma, reputation, condition,
            finisher_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, strength, dexterity, endurance,
        intelligence, charisma, reputation, condition,
        finisher_id
    ))
    wrestler_id = cursor.lastrowid

    # 3. Insert signature moves
    for move in signature_moves:
        move_name = move["name"]
        move_type = move["type"]
        move_damage = move["damage"]
        move_difficulty = move["difficulty"]

        # Check if move exists
        cursor.execute("""
            SELECT id FROM signature_moves
            WHERE name = ? AND type = ? AND damage = ? AND difficulty = ?
        """, (move_name, move_type, move_damage, move_difficulty))
        move_row = cursor.fetchone()
        if move_row:
            move_id = move_row[0]
        else:
            # Insert into signature_moves
            cursor.execute("""
                INSERT INTO signature_moves (name, type, damage, difficulty)
                VALUES (?, ?, ?, ?)
            """, (move_name, move_type, move_damage, move_difficulty))
            move_id = cursor.lastrowid

        # Associate with wrestler
        cursor.execute("""
            INSERT INTO wrestler_signature_moves (wrestler_id, signature_move_id)
            VALUES (?, ?)
        """, (wrestler_id, move_id))

    conn.commit()
    conn.close()
    print(f"✅ Wrestler '{name}' added successfully with {len(signature_moves)} signature move(s).")
