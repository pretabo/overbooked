"""
Setup the events database for Overbooked.
"""

import sqlite3
from db.utils import db_path
import logging

def setup_events_db():
    """
    Set up the events database schema.
    """
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
    
    # Create events_matches table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            match_number INTEGER,
            wrestler1_id INTEGER,
            wrestler2_id INTEGER,
            match_type TEXT DEFAULT 'Singles',
            stipulation TEXT DEFAULT 'Standard',
            winner_id INTEGER,
            quality INTEGER DEFAULT 0,
            match_result TEXT,
            FOREIGN KEY (event_id) REFERENCES events(id),
            FOREIGN KEY (wrestler1_id) REFERENCES wrestlers(id),
            FOREIGN KEY (wrestler2_id) REFERENCES wrestlers(id),
            FOREIGN KEY (winner_id) REFERENCES wrestlers(id)
        )
    """)
    
    # Create events_promos table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events_promos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            promo_number INTEGER,
            wrestler_id INTEGER,
            promo_text TEXT,
            quality INTEGER DEFAULT 0,
            crowd_reaction TEXT,
            FOREIGN KEY (event_id) REFERENCES events(id),
            FOREIGN KEY (wrestler_id) REFERENCES wrestlers(id)
        )
    """)
    
    # Add some sample data if the events table is empty
    cursor.execute("SELECT COUNT(*) FROM events")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Add a sample event
        cursor.execute("""
            INSERT INTO events (name, venue, city, event_date)
            VALUES (?, ?, ?, ?)
        """, ("Overbooked: Premiere", "Madison Square Garden", "New York", "1997-01-31"))
        
        logging.info("Added sample event to events database")
    
    conn.commit()
    conn.close()
    logging.info("Events database setup complete")

if __name__ == "__main__":
    setup_events_db()
    print("Events database setup complete.")
