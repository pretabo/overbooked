"""
Setup script to initialize the match history database for Overbooked.
"""

import os
import logging
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)

# Setup database path
def db_path(filename):
    return os.path.join("db", filename)

def setup_match_history_db():
    """Setup the match history database."""
    logging.info("Setting up match history database...")
    conn = sqlite3.connect(db_path("match_history.db"))
    cursor = conn.cursor()
    
    # Create matches table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wrestler1_id INTEGER,
            wrestler2_id INTEGER,
            winner_id INTEGER,
            match_type TEXT,
            finish_type TEXT,
            match_quality REAL,
            match_time INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logging.info("Match history database setup complete")

if __name__ == "__main__":
    # Create the db directory if it doesn't exist
    if not os.path.exists("db"):
        os.makedirs("db")
        
    setup_match_history_db()
    print("Match history database setup complete!") 