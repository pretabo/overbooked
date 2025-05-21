"""
Setup script to initialize all database tables for Overbooked.
"""

import os
import logging
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)

# Setup database path
def db_path(filename):
    return os.path.join("db", filename)

def setup_relationships_db():
    """Setup the relationships database."""
    logging.info("Setting up relationships database...")
    conn = sqlite3.connect(db_path("relationships.db"))
    cursor = conn.cursor()
    
    # Create relationships table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relationships (
            wrestler1_id INTEGER,
            wrestler2_id INTEGER,
            relationship_value INTEGER DEFAULT 0,
            PRIMARY KEY (wrestler1_id, wrestler2_id)
        )
    """)
    
    # Create relationship events table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relationship_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wrestler1_id INTEGER,
            wrestler2_id INTEGER,
            event_description TEXT,
            value_change INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logging.info("Relationships database setup complete")

def setup_save_state_db():
    """Setup the save state database."""
    logging.info("Setting up save state database...")
    conn = sqlite3.connect(db_path("save_state.db"))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS save_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Initialize with default date if not exists
    cursor.execute("SELECT COUNT(*) FROM save_state WHERE key = 'gamedate'")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO save_state (key, value) VALUES (?, ?)", 
            ("gamedate", "Wednesday, 22 January 1997")
        )

    conn.commit()
    conn.close()
    logging.info("Save state database setup complete")

def setup_events_db():
    """Setup the events database."""
    logging.info("Setting up events database...")
    conn = sqlite3.connect(db_path("events.db"))
    cursor = conn.cursor()
    
    # Create events table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            card TEXT,
            venue TEXT,
            city TEXT,
            event_date TEXT,
            results TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logging.info("Events database setup complete")

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

def setup_all_databases():
    """Setup critical database tables."""
    logging.info("Setting up database tables...")
    
    # Create the db directory if it doesn't exist
    if not os.path.exists("db"):
        os.makedirs("db")
    
    # Setup critical databases
    setup_relationships_db()
    setup_save_state_db()
    setup_events_db()
    setup_match_history_db()
    
    logging.info("Critical database tables setup complete")

if __name__ == "__main__":
    setup_all_databases()
    print("Database tables setup complete!") 