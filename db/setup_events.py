# import sqlite3
# from db.utils import db_path

# # Create or connect to manoeuvres.db
# conn = sqlite3.connect(db_path("manoeuvres.db"))
# cursor = conn.cursor()

# # Create the table
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS manoeuvres (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL,
#     type TEXT,
#     damage INTEGER
# )
# """)

# manoeuvres = [
#     # Strikes
#     ("Dropkick", "strike", 6),
#     ("Clothesline", "strike", 5),
#     ("Superkick", "strike", 7),
#     ("Forearm Smash", "strike", 5),
#     ("Spinning Backfist", "strike", 6),
#     ("Palm Strike", "strike", 4),
#     ("Big Boot", "strike", 7),

#     # Slams
#     ("Powerbomb", "slam", 10),
#     ("Body Slam", "slam", 6),
#     ("Scoop Slam", "slam", 5),
#     ("Piledriver", "slam", 9),
#     ("Sidewalk Slam", "slam", 7),
#     ("Spinebuster", "slam", 8),
#     ("Jackknife Powerbomb", "slam", 10),

#     # Grapples
#     ("DDT", "grapple", 7),
#     ("Suplex", "grapple", 8),
#     ("Vertical Suplex", "grapple", 7),
#     ("T-Bone Suplex", "grapple", 8),
#     ("Northern Lights Suplex", "grapple", 7),
#     ("Belly-to-Belly Suplex", "grapple", 7),
#     ("Russian Leg Sweep", "grapple", 6),

#     # Aerials
#     ("Elbow Drop", "aerial", 4),
#     ("Moonsault", "aerial", 8),
#     ("Crossbody", "aerial", 6),
#     ("450 Splash", "aerial", 9),
#     ("Top Rope Leg Drop", "aerial", 7),
#     ("Missile Dropkick", "aerial", 6),
#     ("Shooting Star Press", "aerial", 10),

#     # Submissions
#     ("Boston Crab", "submission", 6),
#     ("Sharpshooter", "submission", 8),
#     ("Sleeper Hold", "submission", 5),
#     ("Ankle Lock", "submission", 7),
#     ("Triangle Choke", "submission", 7),
#     ("Armbar", "submission", 6),
#     ("Guillotine Choke", "submission", 8),

#     # Finishers
#     ("RKO", "finisher", 10),
#     ("Stunner", "finisher", 10),
#     ("Pedigree", "finisher", 10),
#     ("Tombstone Piledriver", "finisher", 10),
#     ("Spear", "finisher", 9),
#     ("F5", "finisher", 10),
#     ("Go To Sleep", "finisher", 9)
# ]


# # Insert into the table
# cursor.executemany("INSERT INTO manoeuvres (name, type, damage) VALUES (?, ?, ?)", manoeuvres)

# conn.commit()
# conn.close()

# print("Database and manoeuvres table created.")
