import sqlite3
import os
import json
import logging
from datetime import datetime
from src.core.game_state import get_game_date
from src.storyline.storyline_manager import StorylineManager

class EnhancedStorylineManager(StorylineManager):
    def __init__(self):
        super().__init__()
        self.rivalry_db_path = "rivalries.db"
        self._init_rivalry_db()
        
    def _init_rivalry_db(self):
        """Initialize the rivalry database with required tables."""
        try:
            # Ensure the data directory exists
            os.makedirs(os.path.dirname(self.rivalry_db_path), exist_ok=True)
            
            with sqlite3.connect(self.rivalry_db_path) as conn:
                cursor = conn.cursor()
                
                # Rivalry tracking table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rivalries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        wrestler_pair TEXT NOT NULL UNIQUE,
                        matches INTEGER DEFAULT 0,
                        quality_sum INTEGER DEFAULT 0,
                        drama_sum INTEGER DEFAULT 0,
                        last_match_date TEXT,
                        intensity REAL DEFAULT 0,
                        created_at TEXT NOT NULL,
                        last_updated TEXT NOT NULL
                    )
                """)
                
                # Match history for rivalries
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rivalry_matches (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rivalry_id INTEGER NOT NULL,
                        match_id TEXT NOT NULL,
                        match_date TEXT NOT NULL,
                        winner TEXT NOT NULL,
                        quality INTEGER NOT NULL,
                        drama_score INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (rivalry_id) REFERENCES rivalries(id)
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Error initializing rivalry database: {e}")
            # Create a fallback database in memory if file-based DB fails
            self.rivalry_db_path = ":memory:"
            logging.warning("Using in-memory database as fallback.")
    
    def process_match_result(self, match_data):
        """Process a match result and generate storylines"""
        try:
            wrestler1 = match_data.get("wrestler1", {})
            wrestler2 = match_data.get("wrestler2", {})
            
            wrestler1_id = wrestler1.get("id")
            wrestler2_id = wrestler2.get("id")
            
            if not wrestler1_id or not wrestler2_id:
                logging.error("Missing wrestler IDs in match data")
                return []
            
            # Update rivalry tracking
            self._update_rivalry(wrestler1_id, wrestler2_id, match_data)
            
            # Generate storylines based on match quality and other factors
            storylines = []
            
            # High quality match storyline
            if match_data.get("quality", 0) >= 85:
                storylines.append(self._create_high_quality_storyline(
                    wrestler1_id, wrestler2_id, match_data
                ))
            
            # Rivalry intensification
            if self._is_rivalry_intensified(wrestler1_id, wrestler2_id):
                storylines.append(self._create_rivalry_storyline(
                    wrestler1_id, wrestler2_id, match_data
                ))
            
            # Post-match tension
            if match_data.get("drama_score", 0) >= 15:
                storylines.append(self._create_post_match_tension(
                    wrestler1_id, wrestler2_id, match_data
                ))
            
            # Championship implications
            if match_data.get("championship_match", False):
                storylines.append(self._create_championship_storyline(
                    wrestler1_id, wrestler2_id, match_data
                ))
                
            # Add potential storylines to the database
            storyline_ids = []
            for storyline in storylines:
                if storyline:
                    potential_id = self.add_potential_storyline(
                        wrestler1_id,
                        wrestler2_id,
                        storyline["type"],
                        storyline["description"]
                    )
                    storyline_ids.append(potential_id)
            
            return storyline_ids
            
        except Exception as e:
            logging.error(f"Error processing match result: {e}")
            return []
    
    def _update_rivalry(self, wrestler1_id, wrestler2_id, match_data):
        """Update rivalry tracking between two wrestlers"""
        try:
            # Create a consistent key for the wrestler pair (sorted to ensure consistency)
            wrestler_pair = "-".join(sorted([str(wrestler1_id), str(wrestler2_id)]))
            
            with sqlite3.connect(self.rivalry_db_path) as conn:
                cursor = conn.cursor()
                
                # Check if rivalry exists
                cursor.execute("SELECT * FROM rivalries WHERE wrestler_pair = ?", (wrestler_pair,))
                existing_rivalry = cursor.fetchone()
                
                now = datetime.now().isoformat()
                match_date = match_data.get("date", get_game_date())
                
                if existing_rivalry:
                    # Update existing rivalry
                    matches = existing_rivalry[2] + 1
                    quality_sum = existing_rivalry[3] + match_data.get("quality", 0)
                    drama_sum = existing_rivalry[4] + match_data.get("drama_score", 0)
                    
                    # Calculate rivalry intensity
                    avg_quality = quality_sum / matches
                    avg_drama = drama_sum / matches
                    intensity = (avg_quality * 0.6) + (avg_drama * 0.4)
                    
                    cursor.execute("""
                        UPDATE rivalries
                        SET matches = ?, quality_sum = ?, drama_sum = ?,
                            last_match_date = ?, intensity = ?, last_updated = ?
                        WHERE wrestler_pair = ?
                    """, (
                        matches, quality_sum, drama_sum, match_date,
                        intensity, now, wrestler_pair
                    ))
                    
                    rivalry_id = existing_rivalry[0]
                    
                else:
                    # Create new rivalry
                    quality = match_data.get("quality", 0)
                    drama = match_data.get("drama_score", 0)
                    intensity = (quality * 0.6) + (drama * 0.4)
                    
                    cursor.execute("""
                        INSERT INTO rivalries
                        (wrestler_pair, matches, quality_sum, drama_sum,
                         last_match_date, intensity, created_at, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        wrestler_pair, 1, quality, drama, match_date,
                        intensity, now, now
                    ))
                    
                    rivalry_id = cursor.lastrowid
                
                # Add match to rivalry history
                cursor.execute("""
                    INSERT INTO rivalry_matches
                    (rivalry_id, match_id, match_date, winner, quality, drama_score, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    rivalry_id,
                    match_data.get("match_id", f"match_{now}"),
                    match_date,
                    match_data.get("winner", "Unknown"),
                    match_data.get("quality", 0),
                    match_data.get("drama_score", 0),
                    now
                ))
                
                conn.commit()
                
                return rivalry_id
                
        except Exception as e:
            logging.error(f"Error updating rivalry: {e}")
            return None
    
    def _is_rivalry_intensified(self, wrestler1_id, wrestler2_id):
        """Check if a rivalry has intensified based on recent matches"""
        try:
            wrestler_pair = "-".join(sorted([str(wrestler1_id), str(wrestler2_id)]))
            
            with sqlite3.connect(self.rivalry_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM rivalries WHERE wrestler_pair = ?", (wrestler_pair,))
                rivalry = cursor.fetchone()
                
                if not rivalry:
                    return False
                
                return (
                    rivalry[2] >= 3 and  # At least 3 matches
                    rivalry[6] >= 75 and  # Intensity >= 75
                    (rivalry[4] / rivalry[2]) >= 15  # Average drama score >= 15
                )
                
        except Exception as e:
            logging.error(f"Error checking rivalry intensification: {e}")
            return False
    
    def _create_high_quality_storyline(self, wrestler1_id, wrestler2_id, match_data):
        """Create a storyline based on a high-quality match"""
        match_quality = match_data.get("quality", 0)
        if match_quality < 85:
            return None
            
        descriptions = [
            f"An instant classic between {wrestler1_id} and {wrestler2_id}",
            f"The match between {wrestler1_id} and {wrestler2_id} stole the show",
            f"Fans are buzzing about the amazing contest between {wrestler1_id} and {wrestler2_id}",
            f"{wrestler1_id} and {wrestler2_id} put on a wrestling clinic"
        ]
        
        return {
            "type": "High Quality Match",
            "wrestlers": [wrestler1_id, wrestler2_id],
            "description": descriptions[match_quality % len(descriptions)],
            "value": match_quality // 4,
            "attributes": {
                "match_quality": match_quality,
                "drama_score": match_data.get("drama_score", 0),
                "crowd_energy": match_data.get("crowd_energy", 0)
            }
        }
    
    def _create_rivalry_storyline(self, wrestler1_id, wrestler2_id, match_data):
        """Create a storyline based on an intensified rivalry"""
        try:
            wrestler_pair = "-".join(sorted([str(wrestler1_id), str(wrestler2_id)]))
            
            with sqlite3.connect(self.rivalry_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM rivalries WHERE wrestler_pair = ?", (wrestler_pair,))
                rivalry = cursor.fetchone()
                
                if not rivalry:
                    return None
                
                intensity = rivalry[6]
                total_matches = rivalry[2]
                
                descriptions = [
                    f"The rivalry between {wrestler1_id} and {wrestler2_id} reaches new heights",
                    f"{wrestler1_id} and {wrestler2_id} can't seem to settle their differences",
                    f"The feud between {wrestler1_id} and {wrestler2_id} continues to intensify",
                    f"Bad blood boils over between {wrestler1_id} and {wrestler2_id}"
                ]
                
                return {
                    "type": "Rivalry Intensified",
                    "wrestlers": [wrestler1_id, wrestler2_id],
                    "description": descriptions[total_matches % len(descriptions)],
                    "value": min(25, int(intensity / 4)),
                    "attributes": {
                        "rivalry_intensity": intensity,
                        "total_matches": total_matches
                    }
                }
                
        except Exception as e:
            logging.error(f"Error creating rivalry storyline: {e}")
            return None
    
    def _create_post_match_tension(self, wrestler1_id, wrestler2_id, match_data):
        """Create a storyline based on post-match tension"""
        drama_score = match_data.get("drama_score", 0)
        if drama_score < 15:
            return None
            
        descriptions = [
            f"Tensions run high after the match between {wrestler1_id} and {wrestler2_id}",
            f"The match might be over, but {wrestler1_id} and {wrestler2_id} aren't done with each other",
            f"The animosity between {wrestler1_id} and {wrestler2_id} continues after the bell",
            f"There's unfinished business between {wrestler1_id} and {wrestler2_id}"
        ]
        
        return {
            "type": "Post-Match Tension",
            "wrestlers": [wrestler1_id, wrestler2_id],
            "description": descriptions[drama_score % len(descriptions)],
            "value": drama_score // 3,
            "attributes": {
                "drama_score": drama_score,
                "match_quality": match_data.get("quality", 0)
            }
        }
    
    def _create_championship_storyline(self, wrestler1_id, wrestler2_id, match_data):
        """Create a storyline based on championship implications"""
        if not match_data.get("championship_match", False):
            return None
            
        championship = match_data.get("championship", "Unknown")
        winner = match_data.get("winner", "Unknown")
        
        # Determine which wrestler ID matches the winner name
        winner_id = wrestler1_id if winner == match_data.get("wrestler1", {}).get("name") else wrestler2_id
        loser_id = wrestler2_id if winner_id == wrestler1_id else wrestler1_id
        
        descriptions = [
            f"{winner_id} emerges victorious in a championship bout against {loser_id}",
            f"The {championship} Championship match between {wrestler1_id} and {wrestler2_id} changes the landscape",
            f"{winner_id} proves worthy of championship gold against {loser_id}",
            f"The battle for the {championship} between {wrestler1_id} and {wrestler2_id} will go down in history"
        ]
        
        return {
            "type": "Championship Implications",
            "wrestlers": [wrestler1_id, wrestler2_id],
            "description": descriptions[int(match_data.get("quality", 0)) % len(descriptions)],
            "value": 30,
            "attributes": {
                "championship": championship,
                "match_quality": match_data.get("quality", 0),
                "winner": winner
            }
        }
        
    def get_rivalries(self):
        """Get all tracked rivalries"""
        try:
            with sqlite3.connect(self.rivalry_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM rivalries
                    ORDER BY intensity DESC
                """)
                
                return [{
                    'id': row[0],
                    'wrestler_pair': row[1],
                    'matches': row[2],
                    'quality_avg': row[3] / row[2] if row[2] > 0 else 0,
                    'drama_avg': row[4] / row[2] if row[2] > 0 else 0,
                    'last_match_date': row[5],
                    'intensity': row[6]
                } for row in cursor.fetchall()]
                
        except Exception as e:
            logging.error(f"Error getting rivalries: {e}")
            return []
    
    def get_rivalry_details(self, rivalry_id):
        """Get detailed information about a rivalry"""
        try:
            with sqlite3.connect(self.rivalry_db_path) as conn:
                cursor = conn.cursor()
                
                # Get rivalry info
                cursor.execute("SELECT * FROM rivalries WHERE id = ?", (rivalry_id,))
                rivalry = cursor.fetchone()
                
                if not rivalry:
                    return None
                
                # Get rivalry matches
                cursor.execute("""
                    SELECT * FROM rivalry_matches
                    WHERE rivalry_id = ?
                    ORDER BY match_date DESC
                """, (rivalry_id,))
                
                matches = [{
                    'match_id': row[2],
                    'date': row[3],
                    'winner': row[4],
                    'quality': row[5],
                    'drama_score': row[6]
                } for row in cursor.fetchall()]
                
                # Get wrestler IDs from pair
                wrestler_ids = rivalry[1].split('-')
                
                return {
                    'id': rivalry[0],
                    'wrestler_ids': wrestler_ids,
                    'matches': rivalry[2],
                    'quality_avg': rivalry[3] / rivalry[2] if rivalry[2] > 0 else 0,
                    'drama_avg': rivalry[4] / rivalry[2] if rivalry[2] > 0 else 0,
                    'last_match_date': rivalry[5],
                    'intensity': rivalry[6],
                    'match_history': matches
                }
                
        except Exception as e:
            logging.error(f"Error getting rivalry details: {e}")
            return None 