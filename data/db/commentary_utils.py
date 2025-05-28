import sqlite3
import random
from db.utils import db_path


def get_commentary_line(context, tier=None, w1="Wrestler 1", w2="Wrestler 2"):
    conn = sqlite3.connect(db_path("commentary.db"))
    cursor = conn.cursor()

    try:
        if tier:
            cursor.execute(
                "SELECT line FROM attacking_commentary WHERE context = ? AND tier = ?",
                (context, tier)
            )
        else:
            cursor.execute(
                "SELECT line FROM attacking_commentary WHERE context = ? AND tier IS NULL",
                (context,)
            )

        rows = cursor.fetchall()
    finally:
        conn.close()

    if not rows:
        return f"{w1} is in control!"  # Fallback string

    # Pick random line
    line = random.choice(rows)[0]

    # Replace placeholders
    return line.replace("(wrestler1)", w1).replace("(wrestler2)", w2)

import random

