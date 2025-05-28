import os
import subprocess
from db.utils import db_path
import sqlite3

print("🔧 Setting up all Overbooked databases...\n")


setup_scripts = [
    "db/setup_finishers_db.py",
    "db/setup_wrestlers_db.py",
    "db/setup_manoeuvres_db.py",
    "db/setup_commentary_db.py",
    "db/setup_events_and_matches.py",
]

for script in setup_scripts:
    if os.path.exists(script):
        print(f"▶️ Running {script}...")
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()  # ensure `db` is importable
        result = subprocess.run(["python", script], capture_output=True, text=True, env=env)
        print(result.stdout)
        if result.stderr:
            print("⚠️ Error output:\n", result.stderr)
    else:
        print(f"❌ Script not found: {script}")

print("✅ All databases are set up!\n")

# Create wrestler_move_experience table
conn = sqlite3.connect(db_path("wrestlers.db"))
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS wrestler_move_experience (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wrestler_id INTEGER NOT NULL,
        move_name TEXT NOT NULL,
        experience INTEGER DEFAULT 0,
        times_used INTEGER DEFAULT 0,
        times_succeeded INTEGER DEFAULT 0,
        UNIQUE(wrestler_id, move_name),
        FOREIGN KEY (wrestler_id) REFERENCES wrestlers(id) ON DELETE CASCADE
    )
''')

conn.commit()
conn.close()
