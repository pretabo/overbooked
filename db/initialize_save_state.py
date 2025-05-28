import os
import sqlite3
from datetime import datetime

# Get the absolute path to the db directory
db_dir = os.path.dirname(os.path.abspath(__file__))

def db_path(filename):
    """Get the absolute path to a database file."""
    return os.path.join(db_dir, filename)

def initialize_save_state():
    """Initialize the save state database with required tables and default values."""
    conn = sqlite3.connect(db_path("save_state.db"))
    cursor = conn.cursor()
    
    # Create save_state table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS save_state (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    
    # Set default game date (current day of the week)
    today = datetime.now().strftime("%A, %d %B %Y")
    
    # Insert or update the game date
    cursor.execute("""
    INSERT OR REPLACE INTO save_state (key, value)
    VALUES ('gamedate', ?)
    """, (today,))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Save state database initialized successfully.")
    print(f"Current game date set to: {today}")

if __name__ == "__main__":
    initialize_save_state() 