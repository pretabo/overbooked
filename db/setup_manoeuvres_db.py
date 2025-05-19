import sqlite3
from    db.utils import db_path

# Connect to the manoeuvres database
conn = sqlite3.connect(db_path("manoeuvres.db"))
cursor = conn.cursor()

# Recreate the manoeuvres table
cursor.execute("DROP TABLE IF EXISTS manoeuvres")
cursor.execute("""
CREATE TABLE IF NOT EXISTS manoeuvres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    damage INTEGER NOT NULL,
    difficulty INTEGER NOT NULL
)
""")

# Full move list including signatures + extras
manoeuvres = [

    # Your original set
    ("Dropkick", "strike", 6, 6),
    ("Clothesline", "strike", 5, 3),
    ("Superkick", "strike", 7, 7),
    ("Forearm Smash", "strike", 5, 4),
    ("Spinning Backfist", "strike", 6, 6),
    ("Big Boot", "strike", 7, 5),
    ("Powerbomb", "slam", 10, 8),
    ("Body Slam", "slam", 6, 4),
    ("Scoop Slam", "slam", 5, 3),
    ("Piledriver", "slam", 9, 8),
    ("Sidewalk Slam", "slam", 7, 5),
    ("Spinebuster", "slam", 8, 7),
    ("Suplex", "grapple", 8, 6),
    ("Vertical Suplex", "grapple", 7, 5),
    ("T-Bone Suplex", "grapple", 8, 7),
    ("Belly-to-Belly Suplex", "grapple", 7, 6),
    ("Northern Lights Suplex", "grapple", 7, 6),
    ("Russian Leg Sweep", "grapple", 6, 4),
    ("Elbow Drop", "aerial", 4, 4),
    ("Moonsault", "aerial", 8, 8),
    ("Crossbody", "aerial", 6, 6),
    ("450 Splash", "aerial", 9, 9),
    ("Top Rope Leg Drop", "aerial", 7, 7),
    ("Shooting Star Press", "aerial", 10, 10),
    ("Boston Crab", "submission", 6, 5),
    ("Sharpshooter", "submission", 8, 7),
    ("Sleeper Hold", "submission", 5, 4),
    ("Ankle Lock", "submission", 7, 6),
    ("Triangle Choke", "submission", 7, 7),
    ("Armbar", "submission", 6, 5),
    ("German Suplex", "grapple", 7, 6),
    ("Snapmare", "grapple", 4, 3),
    ("Rolling Elbow", "strike", 7, 6),
    ("Diving Headbutt", "aerial", 8, 9),
    ("Camel Clutch", "submission", 6, 6),

    # New pro-style filler moves
    ("Gutwrench Suplex", "grapple", 7, 6),
    ("Discus Lariat", "strike", 8, 7),
    ("Pop-Up Powerbomb", "slam", 9, 8),
    ("Samoan Drop", "slam", 7, 6),
    ("Enziguri", "strike", 6, 6),
    ("Double Underhook Suplex", "grapple", 8, 7),
    ("Senton Bomb", "aerial", 9, 8),
    ("Frog Splash", "aerial", 9, 9),
    ("Octopus Stretch", "submission", 6, 6),
    ("Dragon Sleeper", "submission", 7, 7),

        # Basic strikes
    ("Chop", "strike", 3, 2),
    ("Open Hand Slap", "strike", 2, 1),
    ("Elbow Strike", "strike", 3, 2),
    ("Knee Lift", "strike", 3, 2),
    ("Backhand", "strike", 3, 2),
    ("Palm Strike", "strike", 3, 2),
    ("Throat Thrust", "strike", 4, 3),
    ("Shoulder Tackle", "strike", 4, 3),
    ("Body Punch", "strike", 3, 2),
    ("Spinning Elbow", "strike", 4, 4),

    # Basic grapples
    ("Headlock Takedown", "grapple", 3, 2),
    ("Side Headlock", "grapple", 2, 1),
    ("Arm Drag", "grapple", 3, 2),
    ("Hip Toss", "grapple", 4, 3),
    ("Hammerlock", "grapple", 2, 2),
    ("Wrist Lock", "grapple", 2, 2),
    ("Waist Lock", "grapple", 2, 2),
    ("Snapmare Takeover", "grapple", 3, 2),

    # Basic slams
    ("Back Body Drop", "slam", 5, 4),
    ("Quick Slam", "slam", 4, 3),
    ("Low Scoop Slam", "slam", 3, 2),
    ("Running Slam", "slam", 5, 4),

    # Basic submissions
    ("Chinlock", "submission", 2, 2),
    ("Abdominal Stretch", "submission", 3, 3),
    ("Wrist Lock", "submission", 2, 2),
    ("Ground Headlock", "submission", 3, 2),
    ("Standing Armbar", "submission", 3, 3),

    # Basic aerials
    ("Second Rope Dropkick", "aerial", 4, 4),
    ("Springboard Crossbody", "aerial", 5, 5),
    ("Rope Assisted Elbow", "aerial", 3, 3),
    ("Corner Splash", "aerial", 4, 3),

    #  Strikes
    ("Jumping Knee Strike", "strike", 5, 4),
    ("Mounted Punches", "strike", 4, 3),
    ("Corner Chop", "strike", 3, 2),
    ("Running Forearm", "strike", 5, 4),
    ("Clothesline From Hell", "strike", 8, 8),
    ("Leg Lariat", "strike", 6, 5),
    ("Rope Rebound Lariat", "strike", 6, 5),
    ("Rolling Kick", "strike", 6, 6),
    ("Discus Elbow", "strike", 6, 5),
    ("Shotgun Dropkick", "strike", 6, 6),

    # Slams
    ("Military Press Slam", "slam", 8, 7),
    ("Spinning Spinebuster", "slam", 8, 7),
    ("Cradle Slam", "slam", 6, 5),
    ("Jackknife Powerbomb", "slam", 10, 9),
    ("Uranage", "slam", 8, 7),
    ("Tiger Bomb", "slam", 9, 8),
    ("Pump Handle Slam", "slam", 7, 6),
    ("Gutbuster", "slam", 5, 4),
    ("Fallaway Slam", "slam", 7, 6),
    ("Running Powerslam", "slam", 9, 8),

    # Grapples
    ("Electric Chair Drop", "grapple", 8, 7),
    ("Double Underhook DDT", "grapple", 7, 6),
    ("Reverse DDT", "grapple", 6, 5),
    ("Neckbreaker", "grapple", 6, 5),
    ("Swinging Neckbreaker", "grapple", 7, 6),
    ("Exploder Suplex", "grapple", 8, 7),
    ("Fireman's Carry", "grapple", 5, 4),
    ("Back Suplex", "grapple", 6, 5),
    ("Running Bulldog", "grapple", 6, 5),
    ("Gutwrench Powerbomb", "grapple", 9, 8),

    # Submissions
    ("Cattle Mutilation", "submission", 8, 8),
    ("Cloverleaf", "submission", 7, 6),
    ("Surfboard Stretch", "submission", 6, 5),
    ("Sleeper Suplex", "submission", 8, 7),
    ("Headscissors Choke", "submission", 5, 5),
    ("Reverse Chinlock", "submission", 3, 2),
    ("Camel Clutch Stretch", "submission", 6, 6),
    ("Triangle Armbar", "submission", 7, 6),
    ("Ground Octopus Hold", "submission", 6, 6),
    ("Lotus Lock", "submission", 8, 8),

    # Aerials
    ("Springboard Moonsault", "aerial", 9, 9),
    ("Diving Elbow", "aerial", 6, 5),
    ("Diving Crossbody", "aerial", 7, 6),
    ("Twisting Splash", "aerial", 8, 7),
    ("Diving Leg Drop", "aerial", 6, 5),
    ("Missile Dropkick", "aerial", 7, 6),
    ("Asai Moonsault", "aerial", 9, 8),
    ("Corkscrew Plancha", "aerial", 9, 8),
    ("Rope Walk Arm Drag", "aerial", 7, 7),
    ("Springboard DDT", "aerial", 8, 8),

    # Flashy finishers or setups
    ("Canadian Destroyer", "slam", 10, 10),
    ("Spanish Fly", "slam", 9, 9),
    ("Phoenix Splash", "aerial", 10, 10),
    ("Reverse Rana", "grapple", 9, 9),
    ("Package Piledriver", "slam", 10, 9),
    ("Gory Bomb", "slam", 8, 8),
    ("Poisonrana", "aerial", 9, 9),
    ("Buckle Bomb", "slam", 9, 9),
    ("Dragonrana", "aerial", 10, 10),
    ("Codebreaker", "strike", 8, 7),

    # Dirty/heel moves
    ("Eye Rake", "strike", 1, 1),
    ("Low Blow", "strike", 1, 1),
    ("Choking Rope Break", "submission", 2, 2),
    ("Foreign Object Strike", "strike", 3, 1),
    ("Thumb to the Eye", "strike", 2, 1),
    ("Exposed Turnbuckle Smash", "slam", 5, 2),
    ("Hair Pull Slam", "slam", 4, 2),
    ("Biting the Forehead", "strike", 1, 1),
    ("Pull of the Tights Roll-Up", "grapple", 4, 3),
    ("Steel Chair Shot", "strike", 10, 1),

]

# Insert moves
cursor.executemany("""
INSERT INTO manoeuvres (name, type, damage, difficulty)
VALUES (?, ?, ?, ?)
""", manoeuvres)

conn.commit()
conn.close()

print(f"✅ Loaded {len(manoeuvres)} manoeuvres into manoeuvres.db")

# Ensure the `wrestler_manoeuvre_experience` table is created correctly
conn = sqlite3.connect(db_path("manoeuvres.db"))
cursor = conn.cursor()

# New: Track per-wrestler, per-move-name experience
cursor.execute("""
    CREATE TABLE IF NOT EXISTS wrestler_move_experience (
        wrestler_id INTEGER,
        move_name TEXT,
        success_count INTEGER DEFAULT 0,
        attempt_count INTEGER DEFAULT 0,
        experience_score INTEGER DEFAULT 0,
        PRIMARY KEY (wrestler_id, move_name)
    )
""")
