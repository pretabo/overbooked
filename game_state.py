from datetime import datetime, timedelta

# Start date can be customisable
current_date = datetime(1997, 1, 1)

def get_game_date():
    return current_date.strftime("%A, %d %B %Y")

def advance_game_date():
    global current_date
    current_date += timedelta(days=1)

    from game_state import mark_relationships_dirty
# After advancing the date
    mark_relationships_dirty()


event_lock = False

def is_event_locked():
    return event_lock

def set_event_lock(value: bool):
    global event_lock
    event_lock = value
    if value:
        print("Event creation is locked.")
    else:
        print("Event creation is unlocked.")    


needs_relationships_refresh = False

def mark_relationships_dirty():
    global needs_relationships_refresh
    needs_relationships_refresh = True

def consume_relationships_refresh_flag():
    global needs_relationships_refresh
    if needs_relationships_refresh:
        needs_relationships_refresh = False
        return True
    return False


import sqlite3
from db.utils import db_path

def save_game_state():
    from game_state import get_game_date
    conn = sqlite3.connect(db_path("save_state.db"))
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO save_state (key, value)
        VALUES (?, ?)
    """, ("gamedate", get_game_date()))
    conn.commit()
    conn.close()
    print("[SaveState] Game state saved.")

def load_game_state():
    from game_state import set_game_date
    conn = sqlite3.connect(db_path("save_state.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM save_state WHERE key = ?", ("gamedate",))
    result = cursor.fetchone()
    conn.close()

    if result:
        set_game_date(result[0])
        print(f"[SaveState] Loaded game date: {result[0]}")
    else:
        print("[SaveState] No saved game state found.")

def get_game_date():
    return current_date.strftime("%A, %d %B %Y")

def set_game_date(date_string):
    global current_date
    current_date = datetime.strptime(date_string, "%A, %d %B %Y")
