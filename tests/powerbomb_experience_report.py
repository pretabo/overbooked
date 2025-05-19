# tests/powerbomb_experience_report.py

import sqlite3
from db.utils import db_path

MOVE_NAME = "Powerbomb"  # You can change this to test other moves

def run_report():
    conn = sqlite3.connect(db_path("manoeuvres.db"))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT wrestler_id, move_name, success_count, attempt_count, experience_score
        FROM wrestler_move_experience
        WHERE move_name = ?
    """, (MOVE_NAME,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"No data found for move: {MOVE_NAME}")
        return

    print(f"\n📊 Experience Report for '{MOVE_NAME}':\n")
    print(f"{'Wrestler ID':<12} {'Attempts':<10} {'Successes':<10} {'Success Rate':<14} {'XP Score':<10}")
    print("-" * 60)

    sorted_rows = sorted(rows, key=lambda x: -x[4])  # Sort by experience_score DESC

    for wrestler_id, _, success, total, xp in sorted_rows:
        rate = (success / total * 100) if total > 0 else 0.0
        print(f"{wrestler_id:<12} {total:<10} {success:<10} {rate:<13.2f}% {xp:<10}")

if __name__ == "__main__":
    run_report()
