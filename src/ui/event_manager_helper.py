import sqlite3
import json
from db.utils import db_path
import os
import datetime
from random import choice, randint
from src.core.game_state import get_game_date

def connect():
    return sqlite3.connect(db_path("events.db"))

def get_all_events():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_event(event_id):
    conn = sqlite3.connect(db_path("events.db"))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()


def add_event(name, card, location, venue, date, results="[]"):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO events (name, card, location, venue, date, results)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, json.dumps(card), location, venue, date, results))
    conn.commit()
    conn.close()

def get_event_by_id(event_id):
    """Get event details by ID, including match ratings if available"""
    conn = connect()
    cursor = conn.cursor()
    
    # First check if match_ratings column exists
    cursor.execute("PRAGMA table_info(events)")
    columns = [info[1] for info in cursor.fetchall()]
    
    # Construct SELECT statement based on available columns
    select_sql = "SELECT * FROM events WHERE id = ?"
    
    cursor.execute(select_sql, (event_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        event_data = {
            "id": row[0],
            "name": row[1],
            "card": json.loads(row[2] or "[]"),
            "location": row[3],
            "venue": row[4],
            "date": row[5],
            "results": json.loads(row[6] or "[]"),
            "hype": row[7],
            "gate": row[8],
            "sales": row[9],
            "ad_money": row[10],
            "tv_rating": row[11],
            "ppv_rating": row[12]
        }
        
        # Add match_ratings if the column exists
        if 'match_ratings' in columns and len(row) > 13:
            try:
                event_data["match_ratings"] = json.loads(row[13] or "[]")
            except (json.JSONDecodeError, TypeError):
                event_data["match_ratings"] = []
        else:
            event_data["match_ratings"] = []
            
        return event_data
    
    return None



def update_event(event_id, name, card):
    conn = sqlite3.connect(db_path("events.db"))
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE events
        SET name = ?, card = ?
        WHERE id = ?
    """, (name, json.dumps(card), event_id))
    conn.commit()
    conn.close()

def update_event_results(event_id, results, match_ratings=None):
    """
    Update event results and optionally match ratings
    
    Args:
        event_id: The ID of the event to update
        results: List of match/promo results
        match_ratings: Optional list of match ratings in format [(event_id, match_index, rating)]
    """
    conn = connect()
    cursor = conn.cursor()
    
    # First update results
    cursor.execute("""
        UPDATE events
        SET results = ?
        WHERE id = ?
    """, (json.dumps(results), event_id))
    
    # If match ratings provided, update those too
    if match_ratings:
        # Check if match_ratings column exists
        cursor.execute("PRAGMA table_info(events)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'match_ratings' not in columns:
            # Add the column if it doesn't exist
            cursor.execute("ALTER TABLE events ADD COLUMN match_ratings TEXT DEFAULT '[]'")
        
        # Update match ratings
        cursor.execute("""
            UPDATE events
            SET match_ratings = ?
            WHERE id = ?
        """, (json.dumps(match_ratings), event_id))
    
    conn.commit()
    conn.close()


import sqlite3
from db.utils import db_path

def save_match_to_db(event_id, match_index, name1, name2, result):
    import sqlite3
    from db.utils import db_path

    conn = sqlite3.connect(db_path("matches.db"))
    cursor = conn.cursor()

    # Defensive extraction of stats (handle dict or int)
    def safe_total(val):
        return val if isinstance(val, int) else sum(val.values())

    def safe_get(val, name):
        return val.get(name, 0) if isinstance(val, dict) else 0

    hits = result.get("hits", {})
    revs = result.get("reversals", {})
    misses = result.get("misses", {})
    total_reversals = safe_total(revs)
    total_successes = safe_total(result.get("successes", 0))
    total_misses = safe_total(misses)

    cursor.execute("""
        INSERT INTO matches (
            event_id, match_index,
            wrestler_1, wrestler_2, winner, method,
            quality, crowd_reaction, reversal_count,
            successful_moves, missed_moves,
            hits_w1, hits_w2,
            reversals_w1, reversals_w2,
            misses_w1, misses_w2
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_id,
        match_index,
        name1,
        name2,
        result.get("winner"),
        result.get("ending_move"),
        result.get("quality"),
        result.get("reaction"),
        total_reversals,
        total_successes,
        total_misses,
        safe_get(hits, name1), safe_get(hits, name2),
        safe_get(revs, name1), safe_get(revs, name2),
        safe_get(misses, name1), safe_get(misses, name2),
    ))

    conn.commit()
    conn.close()

def get_main_event(event_id):
    import sqlite3
    from db.utils import db_path

    conn = sqlite3.connect(db_path("matches.db"))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT wrestler_1, wrestler_2
        FROM matches
        WHERE event_id = ?
        ORDER BY match_index DESC
        LIMIT 1
    """, (event_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "No matches"
    return f"{row[0]} vs {row[1]}"

def get_main_event_result(event_id):
    import sqlite3
    from db.utils import db_path

    conn = sqlite3.connect(db_path("matches.db"))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT wrestler_1, wrestler_2, winner
        FROM matches
        WHERE event_id = ?
        ORDER BY match_index DESC
        LIMIT 1
    """, (event_id,))
    row = cursor.fetchone()
    conn.close()

    if not row or not row[2]:
        return "Result not recorded"

    w1, w2, winner = row
    loser = w2 if winner == w1 else w1
    return f"{winner} def. {loser}"

def generate_weekly_events_for_year(start_year, start_month):
    from datetime import datetime, timedelta
    import sqlite3

    conn = sqlite3.connect(db_path("events.db"))
    cursor = conn.cursor()

    # Load all weekly show configs
    cursor.execute("SELECT name, day_of_week, cadence_weeks, start_date FROM weekly_shows")
    shows = cursor.fetchall()

    # Existing event dates
    cursor.execute("SELECT date FROM events")
    existing_dates = {row[0] for row in cursor.fetchall()}

    days_lookup = {
        "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
        "Friday": 4, "Saturday": 5, "Sunday": 6
    }

    from src.core.game_state import get_game_date
    today = datetime.strptime(get_game_date(), "%A, %d %B %Y").date()
    end_date = today + timedelta(weeks=52)

    for name, day, cadence, start_str in shows:
        try:
            start = datetime.strptime(start_str, "%Y-%m-%d")
        except ValueError:
            print(f"❌ Invalid start date for {name}: {start_str}")
            continue

        day_index = days_lookup.get(day, 0)

        # Align start to the next matching weekday
        while start.weekday() != day_index:
            start += timedelta(days=1)

        # Do not generate anything before today
        if start.date() < today:
            start = datetime.combine(today, datetime.min.time())
            while start.weekday() != day_index:
                start += timedelta(days=1)

        current = start
        while current.date() <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            if date_str not in existing_dates:
                event_name = f"{name} {date_str}"
                # Insert event into the database
                cursor.execute("""
                    INSERT INTO events (name, location, venue, date, card, results)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (event_name, "TV Studio", "Main Arena", date_str, "[]", "[]"))
                print(f"✅ Inserting: {name} on {date_str}")
            current += timedelta(weeks=cadence)

    conn.commit()
    conn.close()
