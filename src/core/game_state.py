from datetime import datetime, timedelta
import sqlite3
import logging
from db.utils import db_path

# Start date can be customisable
current_date = datetime(2025, 6, 1)
relationships_refresh_flag = False

# Initialize business system reference
business_db = None

def get_game_date():
    """Get the current game date as a formatted string."""
    return current_date.strftime("%A, %d %B %Y")

def set_game_date(date_string):
    """Set the current game date from a formatted string."""
    global current_date
    current_date = datetime.strptime(date_string, "%A, %d %B %Y")

def advance_day(days=1):
    """Advance the game date by the specified number of days."""
    global current_date
    current_date += timedelta(days=days)
    return get_game_date()

def set_relationships_refresh_flag():
    """Set the flag to refresh relationship displays."""
    global relationships_refresh_flag
    relationships_refresh_flag = True

def consume_relationships_refresh_flag():
    """Check and reset the relationships refresh flag."""
    global relationships_refresh_flag
    result = relationships_refresh_flag
    relationships_refresh_flag = False
    return result

def save_game_state():
    """Save the current game state to the database."""
    try:
        conn = sqlite3.connect(db_path("save_state.db"))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS save_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        cursor.execute("""
            INSERT OR REPLACE INTO save_state (key, value)
            VALUES (?, ?)
        """, ("gamedate", get_game_date()))
        conn.commit()
        conn.close()
        
        print("[SaveState] Game state saved.")
    except Exception as e:
        logging.error(f"Error saving game state: {e}")

def load_game_state():
    """Load the game state from the database."""
    try:
        conn = sqlite3.connect(db_path("save_state.db"))
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS save_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        cursor.execute("SELECT value FROM save_state WHERE key = ?", ("gamedate",))
        result = cursor.fetchone()
        conn.close()

        if result:
            set_game_date(result[0])
            print(f"[SaveState] Loaded game date: {result[0]}")
        else:
            print("[SaveState] No saved game date found.")
            
        print("[SaveState] No saved business state found.")
    except Exception as e:
        logging.error(f"Error loading game state: {e}")

def get_storyline_value(storyline_id):
    """Get the value of a storyline by ID."""
    try:
        conn = sqlite3.connect(db_path("save_state.db"))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS storylines (
                id INTEGER PRIMARY KEY,
                value TEXT
            )
        """)
        cursor.execute("SELECT value FROM storylines WHERE id = ?", (storyline_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        logging.error(f"Error in get_storyline_value: {e}")
        return None
