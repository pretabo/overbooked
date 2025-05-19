import sqlite3
from pathlib import Path

def db_path(filename):
    return str(Path(__file__).resolve().parent / filename)

# Connect to the commentary database
conn = sqlite3.connect(db_path("commentary.db"))
cursor = conn.cursor()

# Drop existing table if it exists
cursor.execute("DROP TABLE IF EXISTS attacking_commentary")

# Create new table
cursor.execute("""
CREATE TABLE attacking_commentary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    context TEXT NOT NULL,   -- 'momentum', 'attacker', 'crowd', 'quality'
    tier TEXT,               -- 'low', 'medium', 'high' or NULL
    line TEXT NOT NULL
)
""")

# Sample commentary lines
commentary_lines = [
    ("momentum", None, "Bah gawd! (wrestler1) is building momentum like a runaway freight train!"),
    ("momentum", None, "This is a slobberknocker! (wrestler1) is taking it to (wrestler2)!"),
    ("momentum", None, "(wrestler1) is stomping a mudhole in (wrestler2) and walking it dry!"),
    ("momentum", None, "The tide has turned! (wrestler1) is on fire!"),
    ("momentum", None, "Business is about to pick up!(wrestler1) is in control!"),
    ("attacking", None, "Good God almighty! (wrestler1) is unleashing hell on (wrestler2)!"),
    ("attacking", None, "(wrestler1) is opening up a can of whoop-ass!"),
    ("attacking", None, "By gawd! (wrestler1) is laying the smackdown on (wrestler2)!"),
    ("attacking", None, "(wrestler1) is taking (wrestler2) to the woodshed!"),
    ("attacking", None, "This is a mauling! (wrestler1) is dismantling (wrestler2)!"),
    ("crowd", "low", "The crowd is dead, folks — they're sitting on their hands."),
    ("crowd", "low", "You could hear a pin drop in this arena right now."),
    ("crowd", "medium", "The fans are starting to come alive here!"),
    ("crowd", "medium", "Listen to this crowd, they're getting into it!"),
    ("crowd", "high", "Bah gawd! The crowd is on their feet, this place is electric!"),
    ("crowd", "high", "This capacity crowd is going bananas!"),
    ("quality", "low", "This match has been bowling shoe ugly, folks."),
    ("quality", "low", "Not exactly a technical masterpiece we're witnessing here."),
    ("quality", "medium", "Solid back-and-forth action between these two competitors."),
    ("quality", "medium", "We're seeing a good old-fashioned wrestling match here."),
    ("quality", "high", "This is a main event anywhere in the country!"),
    ("quality", "high", "These two are putting on a clinic!"),
    ("momentum", None, "(wrestler1) is like a house on fire!"),
("momentum", None, "(wrestler2) has all the momentum now!"),
("momentum", None, "(wrestler1) is building steam like a runaway train!"),
("momentum", None, "(wrestler1) has turned this arena upside down!"),
("momentum", None, "All the momentum belongs to (wrestler1) now!"),
("momentum", None, "This could be the turning point for (wrestler1)!"),
("momentum", None, "(wrestler1) is absolutely rolling — look out!"),
("momentum", None, "(wrestler1) is on fire, and there’s no extinguisher in sight!"),
("momentum", None, "Listen to this crowd roar for (wrestler1)’s comeback!"),
("momentum", None, "Momentum has swung hard to (wrestler1)’s corner!"),
("momentum", None, "You can see it in (wrestler1)’s eyes — they want this bad!"),
("momentum", None, "(wrestler1) is relentless right now!"),
("momentum", None, "(wrestler1) is like a shark smelling blood in the water!"),
("momentum", None, "The crowd is rallying behind (wrestler1)!"),
("momentum", None, "(wrestler1) is taking it to another level!"),
("momentum", None, "(wrestler1) is on a roll and there’s no stopping them!"),
("momentum", None, "(wrestler1) is like a freight train — unstoppable!"),
("momentum", None, "(wrestler1) is firing on all cylinders!"),
("momentum", None, "The momentum has shifted dramatically in (wrestler1)’s favor!"),
("momentum", None, "(wrestler1) is gaining momentum with every move!"),
("momentum", None, "(wrestler1) is building a head of steam!"),
("momentum", None, "The tide has turned in favor of (wrestler1)!"),

]


# Insert all commentary lines
cursor.executemany("INSERT INTO attacking_commentary (context, tier, line) VALUES (?, ?, ?)", commentary_lines)

# Save and close
conn.commit()
conn.close()

print("✅ Commentary DB setup complete.")
