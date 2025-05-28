import sqlite3
from db.utils import db_path

def setup_events_db():
    conn = sqlite3.connect(db_path("events.db"))
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        card TEXT,
        location TEXT,
        venue TEXT,
        date TEXT,  -- 🆕 new
        results TEXT,  -- 🆕 new (JSON string of results)
        hype INTEGER DEFAULT 0,
        gate INTEGER DEFAULT 0,
        sales INTEGER DEFAULT 0,
        ad_money INTEGER DEFAULT 0,
        tv_rating REAL DEFAULT 0.0,
        ppv_rating REAL DEFAULT 0.0
    )
    """)

    conn.commit()
    conn.close()

def setup_matches_db():
    conn = sqlite3.connect(db_path("matches.db"))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            match_index INTEGER,
            wrestler_1 TEXT,
            wrestler_2 TEXT,
            winner TEXT,
            method TEXT,
            quality INTEGER,
            crowd_reaction INTEGER,
            reversal_count INTEGER,
            successful_moves INTEGER,
            missed_moves INTEGER,
            hits_w1 INTEGER,
            hits_w2 INTEGER,
            reversals_w1 INTEGER,
            reversals_w2 INTEGER,
            misses_w1 INTEGER,
            misses_w2 INTEGER
        )
    """)
    conn.commit()
    conn.close()
    
def setup_weekly_shows_db():
    conn = sqlite3.connect(db_path("events.db"))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weekly_shows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            day_of_week TEXT NOT NULL,         -- e.g. 'Monday'
            cadence_weeks INTEGER NOT NULL,    -- 1 = weekly, 2 = bi-weekly, etc.
            start_date TEXT NOT NULL           -- first episode date (YYYY-MM-DD)
        )
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    setup_events_db()
    setup_matches_db()
    setup_weekly_shows_db()
    print("✅ Databases set up successfully.")

