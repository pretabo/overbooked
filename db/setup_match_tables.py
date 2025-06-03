#!/usr/bin/env python3
"""
Set up match tables in match-related databases

This script ensures that all necessary match-related tables are created
in the appropriate databases, resolving the 'no such table: matches' error.
"""

import os
import sqlite3
import sys
import logging

# Add the project root to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.core.db_utils import get_db_path, execute_script, table_exists

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_matches_table():
    """Set up the matches table in matches.db."""
    db_name = "matches.db"
    
    if table_exists(db_name, "matches"):
        logging.info(f"Matches table already exists in {db_name}")
        return
    
    logging.info(f"Creating matches table in {db_name}")
    
    schema = """
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wrestler1_id INTEGER NOT NULL,
        wrestler2_id INTEGER NOT NULL,
        winner_id INTEGER,
        match_date TEXT,
        match_type TEXT,
        venue TEXT,
        crowd_rating REAL,
        technical_rating REAL,
        storytelling_rating REAL,
        overall_rating REAL,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    execute_script(db_name, schema)
    logging.info(f"Successfully created matches table in {db_name}")

def setup_match_history_table():
    """Set up the match history tables in match_history.db."""
    db_name = "match_history.db"
    
    if table_exists(db_name, "matches"):
        logging.info(f"Matches table already exists in {db_name}")
        return
    
    logging.info(f"Creating tables in {db_name}")
    
    schema = """
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wrestler1_id INTEGER NOT NULL,
        wrestler2_id INTEGER NOT NULL,
        winner_id INTEGER,
        match_date TEXT,
        match_type TEXT,
        venue TEXT,
        crowd_rating REAL,
        technical_rating REAL,
        storytelling_rating REAL,
        overall_rating REAL,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS match_moves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER NOT NULL,
        turn INTEGER NOT NULL,
        wrestler_id INTEGER NOT NULL,
        move_id INTEGER,
        move_name TEXT,
        success BOOLEAN,
        damage REAL,
        stamina_cost REAL,
        is_finisher BOOLEAN,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (match_id) REFERENCES matches (id)
    );
    
    CREATE TABLE IF NOT EXISTS match_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER NOT NULL,
        wrestler_id INTEGER NOT NULL,
        hits INTEGER DEFAULT 0,
        misses INTEGER DEFAULT 0,
        reversals INTEGER DEFAULT 0,
        finishers_hit INTEGER DEFAULT 0,
        finishers_missed INTEGER DEFAULT 0,
        damage_dealt REAL DEFAULT 0,
        damage_taken REAL DEFAULT 0,
        stamina_used REAL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (match_id) REFERENCES matches (id)
    );
    """
    
    execute_script(db_name, schema)
    logging.info(f"Successfully created tables in {db_name}")

def setup_match_statistics_tables():
    """Set up the match statistics tables in match_statistics.db."""
    db_name = "match_statistics.db"
    
    if table_exists(db_name, "wrestler_stats"):
        logging.info(f"Wrestler stats table already exists in {db_name}")
        return
    
    logging.info(f"Creating tables in {db_name}")
    
    schema = """
    CREATE TABLE IF NOT EXISTS wrestler_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wrestler_id INTEGER NOT NULL,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        draws INTEGER DEFAULT 0,
        total_matches INTEGER DEFAULT 0,
        avg_match_rating REAL DEFAULT 0,
        highest_match_rating REAL DEFAULT 0,
        signature_moves TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS move_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wrestler_id INTEGER NOT NULL,
        move_id INTEGER NOT NULL,
        move_name TEXT,
        times_used INTEGER DEFAULT 0,
        success_rate REAL DEFAULT 0,
        avg_damage REAL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    execute_script(db_name, schema)
    logging.info(f"Successfully created tables in {db_name}")

def main():
    """Set up all match-related tables."""
    logging.info("Setting up match-related tables in databases")
    
    setup_matches_table()
    setup_match_history_table()
    setup_match_statistics_tables()
    
    logging.info("All match-related tables have been set up successfully")

if __name__ == "__main__":
    main() 