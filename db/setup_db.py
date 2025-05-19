import os
import subprocess
from utils import db_path

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
