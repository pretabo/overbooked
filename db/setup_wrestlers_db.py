import sqlite3
from utils import db_path
from wrestler_test_data import TEST_WRESTLERS, SIGNATURE_MOVES, FINISHERS

# === Connect to wrestlers.db
conn = sqlite3.connect(db_path("wrestlers.db"))
cursor = conn.cursor()

# === Drop and recreate all tables
cursor.execute("DROP TABLE IF EXISTS wrestlers")
cursor.execute("DROP TABLE IF EXISTS wrestler_attributes")
cursor.execute("DROP TABLE IF EXISTS signature_moves")
cursor.execute("DROP TABLE IF EXISTS wrestler_signature_moves")
cursor.execute("DROP TABLE IF EXISTS finishers")

# === Create tables
cursor.execute("""
CREATE TABLE finishers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    style TEXT,
    damage INTEGER,
    difficulty INTEGER
)
""")

cursor.execute("""
CREATE TABLE signature_moves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    damage INTEGER,
    difficulty INTEGER
)
""")

cursor.execute("""
CREATE TABLE wrestlers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    reputation INTEGER,
    condition INTEGER,
    finisher_id INTEGER,
    fan_popularity TEXT,
    marketability TEXT,
    merchandise_sales TEXT,
    contract_type TEXT,
    contract_expiry TEXT,
    contract_value INTEGER,
    contract_promises TEXT,
    contract_company TEXT,
    locker_room_impact TEXT,
    loyalty_level TEXT,
    ambition TEXT,
    injury TEXT,
    height INTEGER,
    weight INTEGER,
    FOREIGN KEY (finisher_id) REFERENCES finishers(id)
)
""")

cursor.execute("""
CREATE TABLE wrestler_attributes (
    wrestler_id INTEGER PRIMARY KEY,
    powerlifting INTEGER,
    grapple_control INTEGER,
    grip_strength INTEGER,
    agility INTEGER,
    balance INTEGER,
    flexibility INTEGER,
    recovery_rate INTEGER,
    conditioning INTEGER,
    chain_wrestling INTEGER,
    mat_transitions INTEGER,
    submission_technique INTEGER,
    strike_accuracy INTEGER,
    brawling_technique INTEGER,
    aerial_precision INTEGER,
    counter_timing INTEGER,
    pressure_handling INTEGER,
    promo_delivery INTEGER,
    fan_engagement INTEGER,
    entrance_presence INTEGER,
    presence_under_fire INTEGER,
    confidence INTEGER,
    focus INTEGER,
    resilience INTEGER,
    adaptability INTEGER,
    risk_assessment INTEGER,
    loyalty INTEGER,
    political_instinct INTEGER,
    determination INTEGER,
    FOREIGN KEY (wrestler_id) REFERENCES wrestlers(id)
)
""")

cursor.execute("""
CREATE TABLE wrestler_signature_moves (
    wrestler_id INTEGER,
    signature_move_id INTEGER,
    FOREIGN KEY (wrestler_id) REFERENCES wrestlers(id),
    FOREIGN KEY (signature_move_id) REFERENCES signature_moves(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wrestler_a_id INTEGER NOT NULL,
    wrestler_b_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    UNIQUE(wrestler_a_id, wrestler_b_id),
    FOREIGN KEY (wrestler_a_id) REFERENCES wrestlers(id),
    FOREIGN KEY (wrestler_b_id) REFERENCES wrestlers(id)
)""")


# === Insert finishers into finishers table
finisher_id_map = {}
for name, style, damage, difficulty in FINISHERS:
    cursor.execute(
        "INSERT INTO finishers (name, style, damage, difficulty) VALUES (?, ?, ?, ?)",
        (name, style, damage, difficulty)
    )
    finisher_id_map[name] = cursor.lastrowid

# === Insert signature moves
sig_id_map = {}
for name, type_, damage, difficulty in SIGNATURE_MOVES:
    cursor.execute(
        "INSERT INTO signature_moves (name, type, damage, difficulty) VALUES (?, ?, ?, ?)",
        (name, type_, damage, difficulty)
    )
    sig_id_map[name] = cursor.lastrowid

# === Insert wrestlers and their attributes
for wrestler in TEST_WRESTLERS:
    name = wrestler["name"]
    reputation = wrestler["reputation"]
    condition = wrestler["condition"]
    attributes = wrestler["attributes"]
    finisher = wrestler["finisher"]
    sig_names = wrestler.get("signatures", [])

    # Extended fields
    fan_popularity = wrestler["fan_popularity"]
    marketability = wrestler["marketability"]
    merchandise_sales = wrestler["merchandise_sales"]
    contract_type = wrestler["contract_type"]
    contract_expiry = wrestler["contract_expiry"]
    contract_value = wrestler["contract_value"]
    contract_promises = wrestler["contract_promises"]
    contract_company = wrestler["contract_company"]
    locker_room_impact = wrestler["locker_room_impact"]
    loyalty_level = wrestler["loyalty_level"]
    ambition = wrestler["ambition"]
    injury = wrestler["injury"]

    if len(attributes) != 28:
        raise ValueError(f"❌ {name} has {len(attributes)} attributes (expected 28)")

    finisher_id = finisher_id_map.get(finisher)
    if not finisher_id:
        raise ValueError(f"❌ Finisher '{finisher}' not found for {name}")

    # Insert wrestler
    cursor.execute("""
        INSERT INTO wrestlers (
            name, reputation, condition, finisher_id,
            fan_popularity, marketability, merchandise_sales,
            contract_type, contract_expiry, contract_value,
            contract_promises, contract_company,
            locker_room_impact, loyalty_level, ambition, injury,
            height, weight
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, reputation, condition, finisher_id,
        fan_popularity, marketability, merchandise_sales,
        contract_type, contract_expiry, contract_value,
        contract_promises, contract_company,
        locker_room_impact, loyalty_level, ambition, injury,
        wrestler["height"], wrestler["weight"]
    ))

    wrestler_id = cursor.lastrowid

    # Insert attributes
    cursor.execute(f"""
        INSERT INTO wrestler_attributes (
            wrestler_id,
            powerlifting, grapple_control, grip_strength,
            agility, balance, flexibility, recovery_rate, conditioning,
            chain_wrestling, mat_transitions, submission_technique, strike_accuracy,
            brawling_technique, aerial_precision, counter_timing, pressure_handling,
            promo_delivery, fan_engagement, entrance_presence, presence_under_fire, confidence,
            focus, resilience, adaptability, risk_assessment,
            loyalty, political_instinct, determination
        ) VALUES ({','.join(['?'] * 29)})
    """, (wrestler_id, *attributes))

    # Link signatures
    for sig in sig_names:
        sig_id = sig_id_map.get(sig)
        if sig_id:
            cursor.execute(
                "INSERT INTO wrestler_signature_moves (wrestler_id, signature_move_id) VALUES (?, ?)",
                (wrestler_id, sig_id)
            )
        else:
            print(f"⚠️ Signature move not found: {sig} for {name}")

conn.commit()
conn.close()

print("✅ Wrestlers, attributes, signature moves, and finishers have all been set up in `wrestlers.db`.")
