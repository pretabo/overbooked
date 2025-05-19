import sqlite3
from db.utils import db_path
from match_engine_utils import get_wrestler_id_by_name  # We'll write this next if needed


class DiplomacySystem:
    def __init__(self):
        # Only store non-neutral relationships
        self.relationships = {}  # { (wrestler_a_name, wrestler_b_name): score }

    def adjust_relationship(self, wrestler_a, wrestler_b, reason, intensity):
        """Adjusts relationship score between two wrestlers."""
        key = self._get_key(wrestler_a["name"], wrestler_b["name"])
        current_score = self.relationships.get(key, 0)

        # Apply change
        new_score = current_score + intensity
        new_score = max(-100, min(100, new_score))  # Clamp between -100 and +100

        if new_score == 0:
            # Remove neutral relationships to save space
            if key in self.relationships:
                del self.relationships[key]
        else:
            self.relationships[key] = new_score

        print(f"[Diplomacy] {reason}: {wrestler_a['name']} ↔ {wrestler_b['name']} now {new_score}")

    def tick_relationships(self):
        """Decay all relationships slightly toward neutrality each week."""
        decay_rate = 2  # You can tune this

        to_delete = []
        for key, score in self.relationships.items():
            if score > 0:
                new_score = max(0, score - decay_rate)
            elif score < 0:
                new_score = min(0, score + decay_rate)
            else:
                new_score = 0

            if new_score == 0:
                to_delete.append(key)
            else:
                self.relationships[key] = new_score

        # Clean up neutral relationships
        for key in to_delete:
            del self.relationships[key]

    def get_relationship_status(self, wrestler_a, wrestler_b):
        """Returns human-readable relationship status."""
        score = self.relationships.get(self._get_key(wrestler_a["name"], wrestler_b["name"]), 0)
        if score >= 75:
            return "Allies"
        elif score >= 25:
            return "Friends"
        elif score >= -24:
            return "Neutral"
        elif score >= -74:
            return "Rivals"
        else:
            return "Enemies"

    def _get_key(self, name1, name2):
        """Always store wrestler pairs consistently (sorted alphabetically)."""
        return tuple(sorted((name1, name2)))


    def save_to_db(self):
        conn = sqlite3.connect(db_path("wrestlers.db"))
        cursor = conn.cursor()

        # Clear old relationships
        cursor.execute("DELETE FROM relationships")

        # Insert current relationships
        for (name_a, name_b), score in self.relationships.items():
            wrestler_a_id = get_wrestler_id_by_name(name_a)
            wrestler_b_id = get_wrestler_id_by_name(name_b)

            if wrestler_a_id and wrestler_b_id:
                cursor.execute("""
                    INSERT INTO relationships (wrestler_a_id, wrestler_b_id, score)
                    VALUES (?, ?, ?)
                """, (wrestler_a_id, wrestler_b_id, score))

        conn.commit()
        conn.close()

    def load_from_db(self):
        conn = sqlite3.connect(db_path("wrestlers.db"))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.wrestler_a_id, r.wrestler_b_id, r.score, w1.name, w2.name
            FROM relationships r
            JOIN wrestlers w1 ON r.wrestler_a_id = w1.id
            JOIN wrestlers w2 ON r.wrestler_b_id = w2.id
        """)
        rows = cursor.fetchall()
        conn.close()

        for wrestler_a_id, wrestler_b_id, score, name_a, name_b in rows:
            self.relationships[(name_a, name_b)] = score


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
