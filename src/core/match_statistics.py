import sqlite3
import os
from datetime import datetime
from src.core.game_state import get_game_date
import json
import logging

class MatchStatistics:
    def __init__(self):
        self.db_path = "match_statistics.db"
        self._init_db()
        
    def _init_db(self):
        """Initialize the database with required tables."""
        try:
            # Check if file exists, if not create it
            if not os.path.exists(self.db_path):
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create matches table (new schema)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wrestler1_id INTEGER NOT NULL,
                    wrestler2_id INTEGER NOT NULL,
                    winner_id INTEGER,
                    match_date TEXT NOT NULL,
                    match_rating INTEGER NOT NULL,
                    duration_minutes REAL NOT NULL,
                    moves_used TEXT,
                    match_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create wrestler performances table (new schema)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wrestler_performances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    wrestler_id INTEGER NOT NULL,
                    won INTEGER NOT NULL,
                    match_rating INTEGER NOT NULL,
                    duration_minutes REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (match_id) REFERENCES matches (id)
                )
            ''')
            
            # Create the legacy tables if they don't exist for backward compatibility
            cursor.execute('''
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
            ''')
            
            cursor.execute('''
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
            ''')
            
            conn.commit()
            conn.close()
            logging.info(f"Match statistics database initialized at {self.db_path}")
            return True
        except Exception as e:
            logging.error(f"Error initializing match statistics database: {e}")
            return False
        
    def get_wrestler_attr(self, wrestler, attr, default=None):
        """Safely get wrestler attribute regardless of if it's a class or dict"""
        if wrestler is None:
            return default
        if attr == 'id' and hasattr(wrestler, 'id'):
            return wrestler.id
        elif hasattr(wrestler, attr):
            return getattr(wrestler, attr)
        elif isinstance(wrestler, dict) and attr in wrestler:
            return wrestler[attr]
        return default
        
    def get_wrestler_id(self, wrestler):
        """Get a wrestler's ID safely regardless of object type"""
        if wrestler is None:
            return None
        wrestler_id = self.get_wrestler_attr(wrestler, 'id')
        if wrestler_id is not None:
            return wrestler_id
        
        # If we don't have an ID but have a name, use a hash of the name
        name = self.get_wrestler_attr(wrestler, 'name')
        if name and isinstance(name, str):
            return self._get_or_create_wrestler_id_by_name(name)
        
        # Last resort - if we have a string, assume it's a name
        if isinstance(wrestler, str):
            return self._get_or_create_wrestler_id_by_name(wrestler)
            
        return None

    def _get_or_create_wrestler_id_by_name(self, name):
        """Get a wrestler ID by name or create a placeholder ID"""
        if not name:
            return None
        
        try:
            # Check if we have a function to load wrestlers by name
            from src.core.match_engine import load_wrestler_by_name
            wrestler = load_wrestler_by_name(name)
            if wrestler:
                return self.get_wrestler_attr(wrestler, 'id')
        except ImportError:
            pass
        
        # Fall back to using the name hash as an ID
        # This is not ideal but allows the system to continue
        return abs(hash(name)) % 1000000
        
    def record_match(self, wrestler1=None, wrestler2=None, winner=None, match_rating=None, duration_minutes=None, moves_used=None, match_type="Singles"):
        """
        Record a match result in the database.
        
        Can be called with either:
        1. A single match_result dictionary (preferred format)
        2. Individual parameters (legacy format)
        
        Parameters (when used with individual parameters):
        - wrestler1: The first wrestler
        - wrestler2: The second wrestler
        - winner: The winning wrestler
        - match_rating: The match rating (0-100)
        - duration_minutes: The match duration in minutes
        - moves_used: Dictionary of move counts per wrestler
        - match_type: Type of match (Singles, Tag, etc.)
        
        When called with a match_result dictionary, it should contain:
        - winner_object or winner: The winning wrestler
        - loser_object or loser: The losing wrestler
        - wrestler1 and wrestler2: The participating wrestlers
        - match_rating or quality: The match rating
        - duration_minutes: The match duration
        - move_history: Detailed move history
        - match_type: Type of match
        """
        try:
            # Check if the first parameter is a match result dictionary
            if isinstance(wrestler1, dict) and ('quality' in wrestler1 or 'match_rating' in wrestler1):
                # Extract data from the match result dictionary
                match_result = wrestler1
                
                # Check if we have direct wrestler IDs in the match result
                w1_id = match_result.get('wrestler1_id')
                w2_id = match_result.get('wrestler2_id')
                winner_id = match_result.get('winner_id')
                
                # If we have all the IDs already, use them directly
                if w1_id is not None and w2_id is not None:
                    wrestler1_id = w1_id
                    wrestler2_id = w2_id
                    # Get the winner_id if not provided directly
                    if winner_id is None:
                        winner_name = match_result.get('winner')
                        w1_name = self.get_wrestler_attr(match_result.get('wrestler1'), 'name')
                        w2_name = self.get_wrestler_attr(match_result.get('wrestler2'), 'name')
                        
                        if winner_name == w1_name:
                            winner_id = w1_id
                        elif winner_name == w2_name:
                            winner_id = w2_id
                            
                    # Extract other match data
                    match_rating = match_result.get('match_rating', match_result.get('quality', 0))
                    duration_minutes = match_result.get('duration_minutes', 10)
                    match_type = match_result.get('match_type', 'Singles')
                    
                    # Create JSON for moves if provided
                    if 'move_history' in match_result:
                        moves_used = self._convert_move_history_to_moves_used(match_result['move_history'])
                    else:
                        moves_used = {}
                    
                    # Record the match with the extracted IDs
                    logging.info(f"Recording match with direct IDs: {wrestler1_id} vs {wrestler2_id}, winner: {winner_id}")
                    self._insert_match_record(wrestler1_id, wrestler2_id, winner_id, match_rating, duration_minutes, 
                                            moves_used, match_type, match_result)
                    return True
                
                # If we don't have direct IDs, extract wrestlers and continue with legacy approach
                # Extract wrestlers from the result
                w1 = match_result.get('wrestler1', match_result.get('winner_object'))
                w2 = match_result.get('wrestler2', match_result.get('loser_object'))
                
                if not w1 or not w2:
                    # Try alternate wrestler extraction if needed
                    wrestlers = []
                    if 'winner_object' in match_result:
                        wrestlers.append(match_result['winner_object'])
                    if 'loser_object' in match_result:
                        wrestlers.append(match_result['loser_object'])
                    
                    if len(wrestlers) == 2:
                        w1, w2 = wrestlers
                    else:
                        # One more attempt - try extracting from winner/loser names
                        w1_name = match_result.get('winner')
                        w2_name = match_result.get('loser')
                        if w1_name and w2_name:
                            # Try to create placeholder objects with the names
                            w1 = {'name': w1_name, 'id': self._get_or_create_wrestler_id_by_name(w1_name)}
                            w2 = {'name': w2_name, 'id': self._get_or_create_wrestler_id_by_name(w2_name)}
                        else:
                            logging.error("Could not extract wrestlers from match result")
                            return False
                
                # Extract winner
                if 'winner_object' in match_result:
                    winner = match_result['winner_object']
                else:
                    winner_name = match_result.get('winner')
                    if winner_name:
                        # Find the wrestler object with matching name
                        w1_name = self.get_wrestler_attr(w1, 'name')
                        w2_name = self.get_wrestler_attr(w2, 'name')
                        
                        if winner_name == w1_name:
                            winner = w1
                        elif winner_name == w2_name:
                            winner = w2
                        else:
                            # Create a placeholder winner object
                            winner = {'name': winner_name, 'id': self._get_or_create_wrestler_id_by_name(winner_name)}
                
                # Extract other match data
                match_rating = match_result.get('match_rating', match_result.get('quality', 0))
                duration_minutes = match_result.get('duration_minutes', 10)
                match_type = match_result.get('match_type', 'Singles')
                
                # Convert move history to moves_used format if available
                if 'move_history' in match_result:
                    moves_used = self._convert_move_history_to_moves_used(match_result['move_history'])
                
                # Use the updated variables for the rest of the function
                wrestler1, wrestler2 = w1, w2
            
            # Extract wrestler IDs safely
            wrestler1_id = self.get_wrestler_id(wrestler1)
            wrestler2_id = self.get_wrestler_id(wrestler2)
            winner_id = self.get_wrestler_id(winner) if winner else None
            
            # Ensure we have valid IDs
            if not wrestler1_id or not wrestler2_id:
                logging.error(f"Cannot record match: Missing wrestler IDs ({wrestler1_id}, {wrestler2_id})")
                return False
            
            # Record the match with extracted data
            return self._insert_match_record(wrestler1_id, wrestler2_id, winner_id, match_rating, duration_minutes, 
                                          moves_used, match_type, None)
            
        except Exception as e:
            logging.error(f"Error recording match statistics: {e}")
            return False
    
    def _convert_move_history_to_moves_used(self, move_history):
        """Convert move_history to moves_used format"""
        moves_used = {}
        for move in move_history:
            wrestler_name = move.get('wrestler', '')
            move_name = move.get('move', '')
            if wrestler_name and move_name:
                if wrestler_name not in moves_used:
                    moves_used[wrestler_name] = {}
                
                if move_name not in moves_used[wrestler_name]:
                    moves_used[wrestler_name][move_name] = 0
                
                moves_used[wrestler_name][move_name] += 1
        return moves_used
    
    def _insert_match_record(self, wrestler1_id, wrestler2_id, winner_id, match_rating, duration_minutes, 
                           moves_used, match_type, match_result=None):
        """Insert a match record into the database with the provided data"""
        try:
            # Create JSON for moves if provided
            moves_json = json.dumps(moves_used) if moves_used else "{}"
            
            # Get current game date
            match_date = get_game_date()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert match record
            cursor.execute('''
                INSERT INTO matches (
                    wrestler1_id, wrestler2_id, winner_id, 
                    match_date, match_rating, duration_minutes,
                    moves_used, match_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                wrestler1_id, wrestler2_id, winner_id, 
                match_date, match_rating, duration_minutes,
                moves_json, match_type
            ))
            
            match_id = cursor.lastrowid
            
            # Insert wrestler statistics
            # For wrestler 1
            self._record_wrestler_performance(
                cursor, match_id, wrestler1_id, 
                winner_id == wrestler1_id,
                match_rating, duration_minutes
            )
            
            # For wrestler 2
            self._record_wrestler_performance(
                cursor, match_id, wrestler2_id, 
                winner_id == wrestler2_id,
                match_rating, duration_minutes
            )
            
            # Also add to match history table (legacy format)
            if match_result:
                self._insert_legacy_match_history(cursor, match_id, match_result, wrestler1_id, wrestler2_id, winner_id)
            else:
                # Create minimal match history entry
                wrestlers_json = json.dumps({
                    "wrestler1_id": wrestler1_id,
                    "wrestler2_id": wrestler2_id
                })
                
                cursor.execute('''
                    INSERT INTO match_history (
                        match_id, date, wrestlers_json, winner, 
                        quality, drama_score, crowd_energy,
                        execution_summary_json, reversals_json, 
                        stamina_drain_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ''', (
                    f"match_{match_id}", match_date, wrestlers_json, str(winner_id),
                    match_rating, match_rating, 50,
                    "{}", "{}", "{}"
                ))
            
            conn.commit()
            conn.close()
            
            logging.info(f"Match statistics recorded: {wrestler1_id} vs {wrestler2_id}, winner: {winner_id}")
            return True
        
        except Exception as e:
            logging.error(f"Error inserting match record: {e}")
            return False
    
    def _insert_legacy_match_history(self, cursor, match_id, match_result, wrestler1_id, wrestler2_id, winner_id):
        """Insert a record into the legacy match_history table"""
        try:
            # Extract data for legacy format
            match_date = get_game_date()
            w1_name = match_result.get("wrestler1_name", str(wrestler1_id))
            w2_name = match_result.get("wrestler2_name", str(wrestler2_id))
            
            wrestlers_json = json.dumps({
                "wrestler1": w1_name,
                "wrestler2": w2_name,
                "wrestler1_id": wrestler1_id,
                "wrestler2_id": wrestler2_id
            })
            
            execution_summary = match_result.get("execution_summary", {})
            reversals = match_result.get("reversals", {})
            stamina_drain = match_result.get("stamina_drain", {})
            
            winner_name = match_result.get("winner", str(winner_id))
            match_rating = match_result.get("match_rating", match_result.get("quality", 50))
            drama_score = match_result.get("drama_score", match_rating)
            crowd_energy = match_result.get("crowd_energy", 50)
            
            cursor.execute('''
                INSERT INTO match_history (
                    match_id, date, wrestlers_json, winner, 
                    quality, drama_score, crowd_energy,
                    execution_summary_json, reversals_json, 
                    stamina_drain_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', (
                f"match_{match_id}", match_date, wrestlers_json, winner_name,
                match_rating, drama_score, crowd_energy,
                json.dumps(execution_summary), json.dumps(reversals),
                json.dumps(stamina_drain)
            ))
            
            return True
        except Exception as e:
            logging.error(f"Error inserting legacy match history: {e}")
            return False
    
    def _record_wrestler_performance(self, cursor, match_id, wrestler_id, is_winner, match_rating, duration):
        """Record individual wrestler performance for a match."""
        cursor.execute('''
            INSERT INTO wrestler_performances (
                match_id, wrestler_id, won, match_rating, duration_minutes
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            match_id, wrestler_id, 1 if is_winner else 0, match_rating, duration
        ))
        
    def get_wrestler_stats(self, wrestler_id):
        """Get statistics for a specific wrestler."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as total_matches,
                   SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) as wins,
                   AVG(match_rating) as avg_rating,
                   AVG(duration_minutes) as avg_duration
            FROM wrestler_performances
            WHERE wrestler_id = ?
        ''', (wrestler_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            total, wins, avg_rating, avg_duration = result
            losses = total - wins if total else 0
            win_rate = (wins / total * 100) if total > 0 else 0
            
            return {
                "total_matches": total or 0,
                "wins": wins or 0,
                "losses": losses,
                "win_rate": win_rate,
                "avg_rating": avg_rating or 0,
                "avg_duration": avg_duration or 0
            }
        
        return {
            "total_matches": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0,
            "avg_rating": 0,
            "avg_duration": 0
        }
    
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