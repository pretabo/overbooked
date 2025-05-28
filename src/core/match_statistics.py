import sqlite3
import os
from datetime import datetime
from src.core.game_state import get_game_date
import json
import logging

class MatchStatistics:
    def __init__(self):
        self.db_path = "data/match_statistics.db"
        self._init_db()
        
    def _init_db(self):
        """Initialize the database with required tables."""
        try:
            # Ensure the data directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Match history table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS match_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        match_id TEXT NOT NULL,
                        date TEXT NOT NULL,
                        wrestlers_json TEXT NOT NULL,
                        winner TEXT NOT NULL,
                        quality INTEGER NOT NULL,
                        drama_score INTEGER NOT NULL,
                        crowd_energy INTEGER NOT NULL,
                        execution_summary_json TEXT NOT NULL,
                        reversals_json TEXT NOT NULL,
                        stamina_drain_json TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)
                
                # Wrestler statistics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS wrestler_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        wrestler_name TEXT NOT NULL UNIQUE,
                        matches INTEGER DEFAULT 0,
                        wins INTEGER DEFAULT 0,
                        losses INTEGER DEFAULT 0,
                        avg_quality REAL DEFAULT 0,
                        total_quality INTEGER DEFAULT 0,
                        best_match INTEGER DEFAULT 0,
                        worst_match INTEGER DEFAULT 100,
                        avg_drama REAL DEFAULT 0,
                        total_drama INTEGER DEFAULT 0,
                        reversal_rate REAL DEFAULT 0,
                        total_reversals INTEGER DEFAULT 0,
                        last_updated TEXT NOT NULL
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Error initializing match statistics database: {e}")
            # Create a fallback database in memory if file-based DB fails
            self.db_path = ":memory:"
            logging.warning("Using in-memory database as fallback.")
        
    def record_match(self, match_data):
        """Record a match's statistics in the database"""
        try:
            match_id = match_data.get("match_id", f"match_{datetime.now().strftime('%Y%m%d%H%M%S')}")
            wrestler1 = match_data.get("wrestler1", {})
            wrestler2 = match_data.get("wrestler2", {})
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Add match to history
                now = datetime.now().isoformat()
                cursor.execute("""
                    INSERT INTO match_history 
                    (match_id, date, wrestlers_json, winner, quality, drama_score, 
                    crowd_energy, execution_summary_json, reversals_json, stamina_drain_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    match_id,
                    match_data.get("date", get_game_date()),
                    json.dumps([wrestler1.get("name", "Unknown"), wrestler2.get("name", "Unknown")]),
                    match_data.get("winner", "Unknown"),
                    match_data.get("quality", 0),
                    match_data.get("drama_score", 0),
                    match_data.get("crowd_energy", 0),
                    json.dumps(match_data.get("execution_summary", {})),
                    json.dumps(match_data.get("reversals", {})),
                    json.dumps(match_data.get("stamina_drain", {})),
                    now
                ))
                
                # Update wrestler statistics
                for wrestler in [wrestler1, wrestler2]:
                    wrestler_name = wrestler.get("name", "Unknown")
                    self._update_wrestler_stats(cursor, wrestler_name, match_data)
                
                conn.commit()
                
            return True
        except Exception as e:
            logging.error(f"Error recording match statistics: {e}")
            return False
    
    def _update_wrestler_stats(self, cursor, wrestler_name, match_data):
        """Update statistics for a specific wrestler"""
        try:
            # Check if wrestler exists in stats table
            cursor.execute("SELECT * FROM wrestler_stats WHERE wrestler_name = ?", (wrestler_name,))
            existing_stats = cursor.fetchone()
            
            now = datetime.now().isoformat()
            
            if existing_stats:
                # Update existing stats
                matches = existing_stats[2] + 1
                wins = existing_stats[3] + (1 if match_data.get("winner") == wrestler_name else 0)
                losses = existing_stats[4] + (1 if match_data.get("winner") != wrestler_name else 0)
                total_quality = existing_stats[6] + match_data.get("quality", 0)
                avg_quality = total_quality / matches
                best_match = max(existing_stats[7], match_data.get("quality", 0))
                worst_match = min(existing_stats[8], match_data.get("quality", 0))
                total_drama = existing_stats[10] + match_data.get("drama_score", 0)
                avg_drama = total_drama / matches
                
                # Get reversals for this wrestler
                reversals = match_data.get("reversals", {}).get(wrestler_name, 0)
                total_reversals = existing_stats[12] + reversals
                reversal_rate = total_reversals / matches
                
                cursor.execute("""
                    UPDATE wrestler_stats
                    SET matches = ?, wins = ?, losses = ?, avg_quality = ?, 
                        total_quality = ?, best_match = ?, worst_match = ?,
                        avg_drama = ?, total_drama = ?, reversal_rate = ?, 
                        total_reversals = ?, last_updated = ?
                    WHERE wrestler_name = ?
                """, (
                    matches, wins, losses, avg_quality, total_quality, best_match, worst_match,
                    avg_drama, total_drama, reversal_rate, total_reversals, now, wrestler_name
                ))
            else:
                # Insert new stats
                wins = 1 if match_data.get("winner") == wrestler_name else 0
                losses = 1 if match_data.get("winner") != wrestler_name else 0
                quality = match_data.get("quality", 0)
                drama = match_data.get("drama_score", 0)
                reversals = match_data.get("reversals", {}).get(wrestler_name, 0)
                
                cursor.execute("""
                    INSERT INTO wrestler_stats
                    (wrestler_name, matches, wins, losses, avg_quality, total_quality,
                     best_match, worst_match, avg_drama, total_drama, reversal_rate,
                     total_reversals, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    wrestler_name, 1, wins, losses, quality, quality, quality, quality,
                    drama, drama, reversals, reversals, now
                ))
        except Exception as e:
            logging.error(f"Error updating wrestler stats for {wrestler_name}: {e}")
    
    def get_wrestler_stats(self, wrestler_name):
        """Get statistics for a specific wrestler"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM wrestler_stats WHERE wrestler_name = ?", (wrestler_name,))
                stats = cursor.fetchone()
                
                if not stats:
                    return {}
                
                return {
                    "matches": stats[2],
                    "wins": stats[3],
                    "losses": stats[4],
                    "win_percentage": (stats[3] / stats[2]) * 100 if stats[2] > 0 else 0,
                    "avg_quality": stats[5],
                    "total_quality": stats[6],
                    "best_match": stats[7],
                    "worst_match": stats[8],
                    "avg_drama": stats[9],
                    "total_drama": stats[10],
                    "reversal_rate": stats[11],
                    "total_reversals": stats[12]
                }
        except Exception as e:
            logging.error(f"Error getting wrestler stats for {wrestler_name}: {e}")
            return {}
    
    def get_match_comparison(self, match_id1, match_id2):
        """Compare two matches"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get first match
                cursor.execute("SELECT * FROM match_history WHERE match_id = ?", (match_id1,))
                match1 = cursor.fetchone()
                
                # Get second match
                cursor.execute("SELECT * FROM match_history WHERE match_id = ?", (match_id2,))
                match2 = cursor.fetchone()
                
                if not match1 or not match2:
                    return None
                
                wrestlers1 = json.loads(match1[3])
                wrestlers2 = json.loads(match2[3])
                
                return {
                    "quality_diff": match1[5] - match2[5],
                    "drama_diff": match1[6] - match2[6],
                    "crowd_energy_diff": match1[7] - match2[7],
                    "common_wrestler": any(w in wrestlers2 for w in wrestlers1)
                }
        except Exception as e:
            logging.error(f"Error comparing matches {match_id1} and {match_id2}: {e}")
            return None
    
    def get_wrestler_trends(self, wrestler_name, last_n_matches=5):
        """Get recent performance trends for a wrestler"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get last N matches for this wrestler
                cursor.execute("""
                    SELECT * FROM match_history 
                    WHERE wrestlers_json LIKE ?
                    ORDER BY date DESC
                    LIMIT ?
                """, (f'%"{wrestler_name}"%', last_n_matches))
                
                recent_matches = cursor.fetchall()
                
                if not recent_matches:
                    return None
                
                # Calculate trends
                qualities = [match[5] for match in recent_matches]
                dramas = [match[6] for match in recent_matches]
                
                # Calculate win streak
                win_streak = 0
                for match in recent_matches:
                    if match[4] == wrestler_name:
                        win_streak += 1
                    else:
                        break
                
                return {
                    "recent_quality_avg": sum(qualities) / len(qualities),
                    "recent_drama_avg": sum(dramas) / len(dramas),
                    "win_streak": win_streak,
                    "quality_trend": "up" if len(qualities) > 1 and qualities[0] > qualities[-1] else "down",
                    "match_count": len(recent_matches)
                }
        except Exception as e:
            logging.error(f"Error getting wrestler trends for {wrestler_name}: {e}")
            return None 