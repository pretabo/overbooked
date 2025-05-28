import sqlite3
from db.utils import db_path
from src.core.match_engine_utils import get_wrestler_id_by_name  # We'll write this next if needed
import random
import logging
import json
import src.core.game_state_debug as game_state_debug
from src.core.diplomacy_hooks import *


class DiplomacySystem:
    """
    Manage relationships between wrestlers.
    """
    def __init__(self):
        self.relationships = {}
        self.events = []
        logging.info("Diplomacy system initialized")

    def load_from_db(self):
        """Load all wrestler relationships from the database."""
        logging.info("Loading wrestler relationships from database")
        try:
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
            
            # Load relationships
            cursor.execute("SELECT wrestler1_id, wrestler2_id, relationship_value FROM relationships")
            relationships = cursor.fetchall()
            
            # Initialize relationship dictionary
            for w1, w2, value in relationships:
                key = self._make_key(w1, w2)
                self.relationships[key] = value
            
            # Load recent events
            cursor.execute("""
                SELECT wrestler1_id, wrestler2_id, event_description, value_change, timestamp
                FROM relationship_events
                ORDER BY timestamp DESC
                LIMIT 100
            """)
            self.events = cursor.fetchall()
            
            conn.commit()
            conn.close()
            
            logging.info(f"Loaded {len(self.relationships)} relationships and {len(self.events)} recent events")
            return True
        except Exception as e:
            logging.error(f"Error loading relationships from database: {e}")
            return False

    def save_to_db(self):
        """Save all wrestler relationships to the database."""
        logging.info("Saving wrestler relationships to database")
        try:
            conn = sqlite3.connect(db_path("relationships.db"))
            cursor = conn.cursor()
            
            # Insert or update relationships
            for key, value in self.relationships.items():
                w1, w2 = self._split_key(key)
                cursor.execute("""
                    INSERT OR REPLACE INTO relationships 
                    (wrestler1_id, wrestler2_id, relationship_value) 
                    VALUES (?, ?, ?)
                """, (w1, w2, value))
            
            conn.commit()
            conn.close()
            
            logging.info(f"Saved {len(self.relationships)} relationships to database")
            return True
        except Exception as e:
            logging.error(f"Error saving relationships to database: {e}")
            return False

    def get_relationship(self, wrestler1, wrestler2):
        """Get the relationship value between two wrestlers."""
        w1 = wrestler1 if isinstance(wrestler1, int) else wrestler1["id"]
        w2 = wrestler2 if isinstance(wrestler2, int) else wrestler2["id"]
        
        if w1 == w2:
            return 0  # No relationship with self
            
        key = self._make_key(w1, w2)
        return self.relationships.get(key, 0)  # Default to neutral

    def set_relationship(self, wrestler1, wrestler2, value):
        """Set the relationship value between two wrestlers."""
        w1 = wrestler1 if isinstance(wrestler1, int) else wrestler1["id"]
        w2 = wrestler2 if isinstance(wrestler2, int) else wrestler2["id"]
        
        if w1 == w2:
            return  # No relationship with self
            
        key = self._make_key(w1, w2)
        old_value = self.relationships.get(key, 0)
        self.relationships[key] = max(-100, min(100, value))  # Clamp to -100 to 100
        
        logging.info(f"Set relationship: Wrestler {w1} to {w2} = {value} (was {old_value})")

    def adjust_relationship(self, wrestler1, wrestler2, reason, change):
        """Adjust the relationship value between two wrestlers."""
        w1 = wrestler1 if isinstance(wrestler1, int) else wrestler1["id"]
        w2 = wrestler2 if isinstance(wrestler2, int) else wrestler2["id"]
        
        if w1 == w2:
            return  # No relationship with self
            
        key = self._make_key(w1, w2)
        current = self.relationships.get(key, 0)
        new_value = max(-100, min(100, current + change))  # Clamp to -100 to 100
        self.relationships[key] = new_value
        
        # Record event
        try:
            conn = sqlite3.connect(db_path("relationships.db"))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO relationship_events 
                (wrestler1_id, wrestler2_id, event_description, value_change) 
                VALUES (?, ?, ?, ?)
            """, (w1, w2, reason, change))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Error recording relationship event: {e}")
        
        # Log the adjustment
        logging.info(f"Relationship adjusted: {w1}-{w2} by {change} → {new_value} (Reason: {reason})")
        game_state_debug.track_diplomacy_adjustment()
        
        # Return the new value
        return new_value

    def decay_relationships(self, amount=1, randomized=True):
        """Decay all relationships by specified amount (simulate time passing)."""
        logging.info(f"Decaying all relationships by {amount}")
        count = 0
        for key in self.relationships:
            current = self.relationships[key]
            
            # Skip if already at zero
            if current == 0:
                continue
                
            # Determine decay amount
            decay = amount
            if randomized:
                # Add some randomness to the decay
                decay = random.randint(0, amount * 2) if random.random() < 0.3 else 0
            
            # Apply decay
            if current > 0:
                self.relationships[key] = max(0, current - decay)
            else:
                self.relationships[key] = min(0, current + decay)
                
            if current != self.relationships[key]:
                count += 1
        
        logging.info(f"Decayed {count} relationships")
        return count

    def get_all_relationships(self, wrestler_id):
        """Get all relationships for a specific wrestler."""
        result = []
        wrestler_id = wrestler_id if isinstance(wrestler_id, int) else wrestler_id["id"]
        
        for key, value in self.relationships.items():
            w1, w2 = self._split_key(key)
            if w1 == wrestler_id:
                result.append((w2, value))
            elif w2 == wrestler_id:
                # Even though relationships are bi-directional now, this
                # maintains backward compatibility
                result.append((w1, value))
        
        return result

    def get_recent_events(self, wrestler_id=None, limit=5):
        """Get recent relationship events."""
        if wrestler_id is None:
            return self.events[:limit]
            
        # Filter events for a specific wrestler
        wrestler_id = wrestler_id if isinstance(wrestler_id, int) else wrestler_id["id"]
        filtered = []
        for event in self.events:
            if event[0] == wrestler_id or event[1] == wrestler_id:
                filtered.append(event)
                if len(filtered) >= limit:
                    break
        
        return filtered

    def _make_key(self, w1, w2):
        """Create a consistent key for a relationship pair."""
        if w1 > w2:
            w1, w2 = w2, w1  # Always put smaller ID first
        return f"{w1}-{w2}"

    def _split_key(self, key):
        """Split a relationship key back into IDs."""
        return [int(x) for x in key.split("-")]
        
    def export_relationships_json(self, filename="relationships.json"):
        """Export all relationships to a JSON file (for debugging)."""
        try:
            data = {}
            for key, value in self.relationships.items():
                data[key] = value
                
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
                
            logging.info(f"Exported {len(self.relationships)} relationships to {filename}")
            return True
        except Exception as e:
            logging.error(f"Error exporting relationships: {e}")
            return False

def load_relationships_from_db():
    """Load all wrestler relationships from the database."""
    conn = sqlite3.connect(db_path("wrestlers.db"))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT w1.name, w2.name, r.score
        FROM relationships r
        JOIN wrestlers w1 ON r.wrestler_a_id = w1.id
        JOIN wrestlers w2 ON r.wrestler_b_id = w2.id
    """)
    
    relationships = {}
    for name1, name2, score in cursor.fetchall():
        key = tuple(sorted((name1, name2)))
        relationships[key] = score

    conn.close()
    return relationships
