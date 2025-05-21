"""
Game State Debug Module

This module provides tools for debugging and monitoring the state of the game.
It includes functions for:
- Printing detailed game state reports
- Tracking changes to game elements
- Monitoring performance metrics
"""

import logging
import json
import time
import os
from datetime import datetime

# Track module-level stats for debugging
performance_stats = {
    "match_simulations": 0,
    "match_simulation_time": 0,
    "promo_generations": 0,
    "promo_generation_time": 0,
    "storyline_updates": 0,
    "diplomacy_adjustments": 0,
    "last_reset": datetime.now().isoformat()
}

# Create a dictionary to track game object states for change detection
state_tracking = {
    "wrestlers": {},
    "events": {},
    "storylines": {},
    "relationships": {}
}

def reset_stats():
    """Reset all performance statistics"""
    global performance_stats
    performance_stats = {
        "match_simulations": 0,
        "match_simulation_time": 0,
        "promo_generations": 0,
        "promo_generation_time": 0,
        "storyline_updates": 0,
        "diplomacy_adjustments": 0,
        "last_reset": datetime.now().isoformat()
    }
    logging.info("Debug performance statistics reset")

def track_match_simulation(duration):
    """Track a match simulation performance"""
    performance_stats["match_simulations"] += 1
    performance_stats["match_simulation_time"] += duration
    avg_time = performance_stats["match_simulation_time"] / performance_stats["match_simulations"]
    logging.debug(f"Match simulation completed in {duration:.2f}s (avg: {avg_time:.2f}s)")

def track_promo_generation(duration):
    """Track a promo generation performance"""
    performance_stats["promo_generations"] += 1
    performance_stats["promo_generation_time"] += duration
    avg_time = performance_stats["promo_generation_time"] / performance_stats["promo_generations"]
    logging.debug(f"Promo generation completed in {duration:.2f}s (avg: {avg_time:.2f}s)")

def track_diplomacy_adjustment():
    """Track a diplomacy relationship adjustment"""
    performance_stats["diplomacy_adjustments"] += 1

def track_storyline_update():
    """Track a storyline update"""
    performance_stats["storyline_updates"] += 1

def print_game_summary():
    """Print a comprehensive summary of the current game state"""
    from game_state import get_game_date
    
    # Get wrestler count
    try:
        import sqlite3
        from db.utils import db_path
        conn = sqlite3.connect(db_path("wrestlers.db"))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM wrestlers")
        wrestler_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM relationships")
        relationship_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM events")
        event_count = cursor.fetchone()[0] 
        conn.close()
    except Exception as e:
        logging.error(f"Error getting game state counts: {e}")
        wrestler_count = "ERROR"
        relationship_count = "ERROR"
        event_count = "ERROR"
    
    # Print summary
    border = "=" * 50
    logging.info(border)
    logging.info("GAME STATE SUMMARY")
    logging.info(border)
    logging.info(f"Current Date: {get_game_date()}")
    logging.info(f"Wrestlers: {wrestler_count}")
    logging.info(f"Relationships: {relationship_count}")
    logging.info(f"Events: {event_count}")
    logging.info(border)
    logging.info("PERFORMANCE STATS")
    logging.info(border)
    logging.info(f"Match Simulations: {performance_stats['match_simulations']}")
    if performance_stats['match_simulations'] > 0:
        avg_match = performance_stats['match_simulation_time'] / performance_stats['match_simulations']
        logging.info(f"Avg Match Sim Time: {avg_match:.2f}s")
    logging.info(f"Promo Generations: {performance_stats['promo_generations']}")
    if performance_stats['promo_generations'] > 0:
        avg_promo = performance_stats['promo_generation_time'] / performance_stats['promo_generations']
        logging.info(f"Avg Promo Gen Time: {avg_promo:.2f}s")
    logging.info(f"Diplomacy Adjustments: {performance_stats['diplomacy_adjustments']}")
    logging.info(f"Storyline Updates: {performance_stats['storyline_updates']}")
    logging.info(border)

def print_wrestler_details(wrestler_id):
    """Print detailed information about a specific wrestler"""
    try:
        from match_engine import load_wrestler_by_id
        wrestler = load_wrestler_by_id(wrestler_id)
        
        if not wrestler:
            logging.error(f"Wrestler with ID {wrestler_id} not found")
            return
            
        border = "-" * 50
        logging.info(border)
        logging.info(f"WRESTLER DETAILS: {wrestler['name']} (ID: {wrestler_id})")
        logging.info(border)
        
        # Print basic stats
        logging.info(f"Reputation: {wrestler.get('reputation', 'N/A')}")
        logging.info(f"Condition: {wrestler.get('condition', 'N/A')}")
        
        # Print high-level attributes
        logging.info("High-Level Attributes:")
        for attr in ['strength', 'dexterity', 'endurance', 'intelligence', 'charisma']:
            logging.info(f"  {attr.capitalize()}: {wrestler.get(attr, 'N/A')}")
        
        # Print relationships
        try:
            import sqlite3
            from db.utils import db_path
            conn = sqlite3.connect(db_path("relationships.db"))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT wrestler2_id, relationship_value
                FROM relationships
                WHERE wrestler1_id = ?
                ORDER BY relationship_value DESC
                LIMIT 5
            """, (wrestler_id,))
            relationships = cursor.fetchall()
            conn.close()
            
            if relationships:
                logging.info("Top 5 Relationships:")
                for rel_id, value in relationships:
                    rel_wrestler = load_wrestler_by_id(rel_id)
                    name = rel_wrestler['name'] if rel_wrestler else f"Unknown ({rel_id})"
                    logging.info(f"  {name}: {value}")
        except Exception as e:
            logging.error(f"Error getting relationships: {e}")
        
        logging.info(border)
    except Exception as e:
        logging.error(f"Error printing wrestler details: {e}")

def export_debug_state():
    """Export the entire game state for debugging purposes"""
    try:
        if not os.path.exists('debug'):
            os.makedirs('debug')
            
        filename = f"debug/game_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Collect game state
        debug_state = {
            "timestamp": datetime.now().isoformat(),
            "performance_stats": performance_stats,
            "game_date": None,
            "wrestlers": [],
            "events": [],
            "storylines": []
        }
        
        # Add game date
        from game_state import get_game_date
        debug_state["game_date"] = get_game_date()
        
        # Get wrestlers
        try:
            import sqlite3
            from db.utils import db_path
            conn = sqlite3.connect(db_path("wrestlers.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM wrestlers")
            columns = [col[0] for col in cursor.description]
            wrestlers = []
            for row in cursor.fetchall():
                wrestlers.append(dict(zip(columns, row)))
            debug_state["wrestlers"] = wrestlers
            conn.close()
        except Exception as e:
            logging.error(f"Error exporting wrestlers: {e}")
        
        # Write to file
        with open(filename, 'w') as f:
            json.dump(debug_state, f, indent=2)
            
        logging.info(f"Debug state exported to {filename}")
    except Exception as e:
        logging.error(f"Error exporting debug state: {e}")

def enable_ui_debug_mode():
    """Enable debug mode in the UI - adds extra information to UI elements"""
    logging.info("UI Debug mode enabled - UI elements will display extra debug information")
    return True 