#!/usr/bin/env python3
"""
Set up the wrestler_move_experience table in the wrestlers database.
"""

import sqlite3
import os
import sys

# Add the parent directory to path to import db.utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.utils import db_path

def setup_move_experience_db():
    """Create the wrestler_move_experience table."""
    print(f"Setting up wrestler move experience tracking in database...")
    
    # Connect to the wrestlers database
    conn = sqlite3.connect(db_path("wrestlers.db"))
    cursor = conn.cursor()
    
    # Create the wrestler_move_experience table
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
    
    print("✅ Wrestler move experience table created/verified")
    
    # Create index for faster lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_wrestler_move
        ON wrestler_move_experience (wrestler_id, move_name)
    ''')
    
    print("✅ Indexes created")
    
    conn.commit()
    conn.close()
    
    print("Move experience database setup complete!")


if __name__ == "__main__":
    setup_move_experience_db() 