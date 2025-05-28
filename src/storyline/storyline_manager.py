from typing import List, Dict, Optional, Tuple
import json
import sqlite3
from datetime import datetime, timedelta
from src.core.game_state import get_game_date
import os
import logging
import random

class StorylineManager:
    def __init__(self):
        self.db_path = "data/storylines.db"
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables."""
        try:
            # Ensure the data directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Potential storylines table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS potential_storylines (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        wrestler1_id INTEGER NOT NULL,
                        wrestler2_id INTEGER NOT NULL,
                        interaction_type TEXT NOT NULL,
                        interaction_date TEXT NOT NULL,
                        interaction_details TEXT,
                        potential_rating INTEGER DEFAULT 0,
                        created_at TEXT NOT NULL
                    )
                """)
                
                # Active storylines table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS active_storylines (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        potential_storyline_id INTEGER,
                        wrestler1_id INTEGER NOT NULL,
                        wrestler2_id INTEGER NOT NULL,
                        storyline_type TEXT NOT NULL,
                        start_date TEXT NOT NULL,
                        status TEXT DEFAULT 'active',
                        priority INTEGER DEFAULT 0,
                        last_progress_date TEXT,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (potential_storyline_id) REFERENCES potential_storylines(id)
                    )
                """)
                
                # Storyline progress table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS storyline_progress (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        storyline_id INTEGER NOT NULL,
                        progress_type TEXT NOT NULL,
                        progress_date TEXT NOT NULL,
                        details TEXT,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (storyline_id) REFERENCES active_storylines(id)
                    )
                """)
                
                # Storyline interactions table (new)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS storyline_interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        storyline_pair TEXT NOT NULL, -- e.g. "id1-id2" sorted
                        interaction_type TEXT NOT NULL,
                        interaction_date TEXT NOT NULL,
                        base_value INTEGER NOT NULL,
                        decay_rate REAL DEFAULT 0.1, -- 10% per week
                        attributes_json TEXT, -- JSON for flexible attributes
                        created_at TEXT NOT NULL
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Error initializing storyline database: {e}")
            # Create a fallback database in memory if file-based DB fails
            self.db_path = ":memory:"
            logging.warning("Using in-memory database as fallback.")

    def add_potential_storyline(self, wrestler1_id: int, wrestler2_id: int, 
                              interaction_type: str, interaction_details: str) -> int:
        """Add a new potential storyline based on wrestler interaction, and add a storyline_interaction."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO potential_storylines 
                (wrestler1_id, wrestler2_id, interaction_type, interaction_date, 
                 interaction_details, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (wrestler1_id, wrestler2_id, interaction_type, get_game_date(),
                  interaction_details, now))
            storyline_id = cursor.lastrowid
        # Add a storyline_interaction as well
        base_value = 20 if "Match" in interaction_type else 10
        attributes = {"details": interaction_details, "type": interaction_type}
        self.add_storyline_interaction(wrestler1_id, wrestler2_id, interaction_type, base_value, attributes)
        return storyline_id

    def activate_storyline(self, potential_storyline_id: int, 
                          storyline_type: str, priority: int = 0) -> int:
        """Convert a potential storyline into an active storyline and remove it from potential storylines."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Get the potential storyline details
            cursor.execute("""
                SELECT wrestler1_id, wrestler2_id 
                FROM potential_storylines 
                WHERE id = ?
            """, (potential_storyline_id,))
            wrestler1_id, wrestler2_id = cursor.fetchone()
            now = datetime.now().isoformat()
            # Create the active storyline
            cursor.execute("""
                INSERT INTO active_storylines 
                (potential_storyline_id, wrestler1_id, wrestler2_id, 
                 storyline_type, start_date, priority, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (potential_storyline_id, wrestler1_id, wrestler2_id,
                  storyline_type, get_game_date(), priority, now))
            # Remove from potential storylines
            cursor.execute("DELETE FROM potential_storylines WHERE id = ?", (potential_storyline_id,))
            return cursor.lastrowid

    def get_potential_storylines(self) -> List[Dict]:
        """Get all potential storylines, one per unique wrestler pair, summarizing interactions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, wrestler1_id, wrestler2_id, interaction_type,
                       interaction_date, interaction_details, potential_rating, created_at
                FROM potential_storylines
                ORDER BY created_at DESC
            """)
            all_rows = cursor.fetchall()

            # Group by wrestler pair (order-insensitive)
            pair_map = {}
            for row in all_rows:
                key = tuple(sorted([row[1], row[2]]))
                if key not in pair_map:
                    pair_map[key] = []
                pair_map[key].append(row)

            result = []
            for pair, rows in pair_map.items():
                # Use the most recent interaction for display
                most_recent = rows[0]
                # Summarize all interaction types and details
                all_types = list({r[3] for r in rows})
                all_details = [r[5] for r in rows if r[5]]
                summary_details = "; ".join(all_details)
                result.append({
                    'id': most_recent[0],
                    'wrestler1_id': most_recent[1],
                    'wrestler2_id': most_recent[2],
                    'interaction_type': ", ".join(all_types),
                    'interaction_date': most_recent[4],
                    'interaction_details': summary_details,
                    'potential_rating': most_recent[6]
                })
            return result

    def get_active_storylines(self) -> List[Dict]:
        """Get all active storylines."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, wrestler1_id, wrestler2_id, storyline_type,
                       start_date, status, priority, last_progress_date
                FROM active_storylines
                WHERE status = 'active'
                ORDER BY priority DESC, start_date DESC
            """)
            
            return [{
                'id': row[0],
                'wrestler1_id': row[1],
                'wrestler2_id': row[2],
                'storyline_type': row[3],
                'start_date': row[4],
                'status': row[5],
                'priority': row[6],
                'last_progress_date': row[7]
            } for row in cursor.fetchall()]

    def add_storyline_progress(self, storyline_id: int, progress_type: str, 
                             details: str) -> int:
        """Add progress to an active storyline."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO storyline_progress 
                (storyline_id, progress_type, progress_date, details, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (storyline_id, progress_type, get_game_date(), details, now))
            
            # Update last_progress_date in active_storylines
            cursor.execute("""
                UPDATE active_storylines 
                SET last_progress_date = ? 
                WHERE id = ?
            """, (get_game_date(), storyline_id))
            
            return cursor.lastrowid

    def get_storyline_progress(self, storyline_id: int) -> List[Dict]:
        """Get all progress entries for a storyline."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, progress_type, progress_date, details
                FROM storyline_progress
                WHERE storyline_id = ?
                ORDER BY progress_date DESC
            """, (storyline_id,))
            
            return [{
                'id': row[0],
                'progress_type': row[1],
                'progress_date': row[2],
                'details': row[3]
            } for row in cursor.fetchall()]

    def update_storyline_priority(self, storyline_id: int, priority: int) -> None:
        """Update the priority of an active storyline."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE active_storylines 
                SET priority = ? 
                WHERE id = ?
            """, (priority, storyline_id))

    def end_storyline(self, storyline_id: int, status: str = 'completed') -> None:
        """End an active storyline."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE active_storylines 
                SET status = ? 
                WHERE id = ?
            """, (status, storyline_id))

    def generate_potential_storylines_from_match(self, wrestler1_id: int, wrestler2_id: int, 
                                               match_result: dict) -> List[int]:
        """Generate potential storylines from a match result and always add a storyline interaction."""
        potential_storylines = []
        # Always add a storyline interaction for the match
        base_value = match_result.get("match_rating", 60) // 4  # e.g. 60 rating = 15 value
        attributes = {
            "match_rating": match_result.get("match_rating", 0),
            "winner_id": match_result.get("winner_id"),
            "type": "Match"
        }
        self.add_storyline_interaction(wrestler1_id, wrestler2_id, "Match", base_value, attributes)
        # Generate based on match quality
        if match_result.get("match_rating", 0) >= 80:
            potential_storylines.append(
                self.add_potential_storyline(
                    wrestler1_id, wrestler2_id,
                    "High Quality Match",
                    f"Both wrestlers delivered an excellent match (Rating: {match_result.get('match_rating', 0)})"
                )
            )
        # Generate based on winner/loser dynamics
        winner_id = match_result.get("winner_id")
        if winner_id:
            loser_id = wrestler2_id if winner_id == wrestler1_id else wrestler1_id
            potential_storylines.append(
                self.add_potential_storyline(
                    winner_id, loser_id,
                    "Post-Match Tension",
                    f"Winner {winner_id} defeated {loser_id} in a competitive match"
                )
            )
        return potential_storylines

    def generate_potential_storylines_from_promo(self, wrestler_id: int, promo_result: dict) -> List[int]:
        """Generate potential storylines from a promo result."""
        potential_storylines = []
        
        # Get all other wrestlers
        from match_engine import get_all_wrestlers
        all_wrestlers = get_all_wrestlers()
        
        # Generate based on promo quality
        if promo_result.get("final_rating", 0) >= 85:
            # High quality promo could create tension with any wrestler
            for other_wrestler_id, _ in all_wrestlers:
                if other_wrestler_id != wrestler_id:
                    potential_storylines.append(
                        self.add_potential_storyline(
                            wrestler_id, other_wrestler_id,
                            "Promo Heat",
                            f"Wrestler delivered an excellent promo (Rating: {promo_result.get('final_rating', 0)})"
                        )
                    )
        
        return potential_storylines

    def get_potential_storyline_details(self, storyline_id: int) -> Dict:
        """Get detailed information about a potential storyline."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, wrestler1_id, wrestler2_id, interaction_type,
                       interaction_date, interaction_details, potential_rating
                FROM potential_storylines
                WHERE id = ?
            """, (storyline_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            return {
                'id': row[0],
                'wrestler1_id': row[1],
                'wrestler2_id': row[2],
                'interaction_type': row[3],
                'interaction_date': row[4],
                'interaction_details': row[5],
                'potential_rating': row[6]
            }

    def delete_potential_storyline(self, storyline_id: int) -> None:
        """Delete a potential storyline."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM potential_storylines
                WHERE id = ?
            """, (storyline_id,))

    def add_storyline_interaction(self, wrestler1_id: int, wrestler2_id: int, interaction_type: str, base_value: int, attributes: dict, decay_rate: float = 0.1) -> int:
        """Add a detailed interaction to the storyline_interactions table."""
        pair = "-".join(str(i) for i in sorted([wrestler1_id, wrestler2_id]))
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO storyline_interactions
                (storyline_pair, interaction_type, interaction_date, base_value, decay_rate, attributes_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                pair, interaction_type, get_game_date(), base_value, decay_rate, json.dumps(attributes), now
            ))
            return cursor.lastrowid

    def get_storyline_value(self, wrestler1_id: int, wrestler2_id: int) -> float:
        """Calculate the current value of a storyline by summing decayed contributions."""
        pair = "-".join(str(i) for i in sorted([wrestler1_id, wrestler2_id]))
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT base_value, decay_rate, interaction_date
                    FROM storyline_interactions
                    WHERE storyline_pair = ?
                """, (pair,))
                
                total = 0.0
                rows = cursor.fetchall()
                if not rows:
                    return 0.0
                
                # Get game date once, not in the loop
                from datetime import datetime as dt
                from game_state import get_game_date
                
                try:
                    game_now = dt.strptime(get_game_date(), "%A, %d %B %Y")
                except Exception as e:
                    logging.error(f"Error parsing game date: {e}")
                    game_now = dt.now()  # Fallback
                
                for base_value, decay_rate, interaction_date in rows:
                    # Calculate weeks since interaction
                    try:
                        try:
                            interaction_dt = dt.strptime(interaction_date, "%A, %d %B %Y")
                        except ValueError:
                            interaction_dt = dt.fromisoformat(interaction_date)
                        
                        weeks = max(0, (game_now - interaction_dt).days // 7)
                        value = base_value * ((1 - decay_rate) ** weeks)
                        total += value
                    except Exception as e:
                        logging.error(f"Error calculating value for interaction: {e}")
                
                return total
        except Exception as e:
            logging.error(f"Error in get_storyline_value: {e}")
            return 0.0

    def get_storyline_interactions(self, wrestler1_id: int, wrestler2_id: int) -> list:
        """Get all interactions for a storyline pair."""
        pair = "-".join(str(i) for i in sorted([wrestler1_id, wrestler2_id]))
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, interaction_type, interaction_date, base_value, decay_rate, attributes_json
                FROM storyline_interactions
                WHERE storyline_pair = ?
                ORDER BY interaction_date DESC
            """, (pair,))
            return [
                {
                    'id': row[0],
                    'interaction_type': row[1],
                    'interaction_date': row[2],
                    'base_value': row[3],
                    'decay_rate': row[4],
                    'attributes': json.loads(row[5]) if row[5] else {}
                }
                for row in cursor.fetchall()
            ] 