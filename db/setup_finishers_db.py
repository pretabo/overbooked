import sqlite3
from db.utils import db_path

conn = sqlite3.connect(db_path("finishers.db"))
cursor = conn.cursor()

# Create table for finishing moves
cursor.execute("""
CREATE TABLE IF NOT EXISTS finishers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    style TEXT,
    damage INTEGER
)
""")

# Full list of finishers and signature moves
finishers = [
    ("RKO", "strike", 10),
    ("Stunner", "strike", 10),
    ("Pedigree", "slam", 10),
    ("Tombstone Piledriver", "slam", 10),
    ("Spear", "strike", 9),
    ("F5", "slam", 10),
    ("Go To Sleep", "strike", 9),
    ("Kinshasa", "strike", 9),
    ("Claymore Kick", "strike", 9),
    ("Curb Stomp", "slam", 10),
    ("One Winged Angel", "slam", 10),
    ("Rainmaker", "strike", 9),
    ("Sharpshooter", "submission", 10),
    ("Ankle Lock", "submission", 9),
    ("Crossface", "submission", 9),
    ("Sleeper Hold", "submission", 8),
    ("Dragon Sleeper", "submission", 9),

    # New additions:
    ("The Postal Swervice", "aerial", 9),
    ("Ezio Bomb", "slam", 9),
    ("When Saturday Swanton Bombs", "aerial", 9),
    ("His Name Is A Chop", "strike", 8),
    ("Cod Botherer", "grapple", 8),
    ("Right Haddock", "strike", 8),
    ("Champagne Suplexnova", "slam", 9),
    ("Acoustic Guitspar", "strike", 8),
    ("Zacariah Punchson", "strike", 8),
    ("Walthamstow Wink", "submission", 8),
    ("Sweet Chill Music", "strike", 8),
    ("Cute witout the 'e'", "strike", 10),
    ("Clap Clap Fish", "strike", 10),
    ("Do Look Back In Anger", "slam", 10),
    ("Reduced Sushi", "submission", 10)
]

cursor.executemany("INSERT INTO finishers (name, style, damage) VALUES (?, ?, ?)", finishers)

conn.commit()
conn.close()

print("✅ Finishing moves database created and updated.")
