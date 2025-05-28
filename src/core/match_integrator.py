import logging
from datetime import datetime
import uuid
from src.core.match_statistics import MatchStatistics
from src.storyline.enhanced_storyline_manager import EnhancedStorylineManager
from src.core.game_state import get_game_date

class MatchIntegrator:
    """
    Integrates match simulation with statistics tracking and storyline generation.
    """
    
    def __init__(self):
        self.stats_manager = MatchStatistics()
        self.storyline_manager = EnhancedStorylineManager()
        
    def simulate_match_with_tracking(self, wrestler1, wrestler2, **simulation_args):
        """
        Simulate a match between two wrestlers and track statistics and storylines.
        
        Args:
            wrestler1: First wrestler data
            wrestler2: Second wrestler data
            **simulation_args: Additional arguments to pass to the simulate_match function
            
        Returns:
            Enhanced match result with statistics and storylines
        """
        try:
            # Import here to avoid circular imports
            from src.core.match_engine import simulate_match
            
            # Generate a unique match ID
            match_id = f"match_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Simulate the match
            match_result = simulate_match(wrestler1, wrestler2, **simulation_args)
            
            # Add match metadata
            match_result["match_id"] = match_id
            match_result["date"] = get_game_date()
            match_result["wrestler1"] = wrestler1
            match_result["wrestler2"] = wrestler2
            
            # Record match statistics
            self.stats_manager.record_match(match_result)
            
            # Generate storylines
            storylines = self.storyline_manager.process_match_result(match_result)
            
            # Add statistics and storylines to the result
            match_result["statistics"] = {
                "wrestler1": self.stats_manager.get_wrestler_stats(wrestler1.get("name")),
                "wrestler2": self.stats_manager.get_wrestler_stats(wrestler2.get("name")),
                "wrestler1_trends": self.stats_manager.get_wrestler_trends(wrestler1.get("name")),
                "wrestler2_trends": self.stats_manager.get_wrestler_trends(wrestler2.get("name"))
            }
            
            match_result["storylines"] = storylines
            
            return match_result
            
        except Exception as e:
            logging.error(f"Error in match integration: {e}")
            # If there's an error, return the original result from simulate_match
            from src.core.match_engine import simulate_match
            return simulate_match(wrestler1, wrestler2, **simulation_args)
    
    def get_wrestler_statistics(self, wrestler_name):
        """Get statistics for a specific wrestler"""
        return self.stats_manager.get_wrestler_stats(wrestler_name)
    
    def get_wrestler_trends(self, wrestler_name, last_n_matches=5):
        """Get recent performance trends for a wrestler"""
        return self.stats_manager.get_wrestler_trends(wrestler_name, last_n_matches)
    
    def get_rivalries(self):
        """Get all tracked rivalries"""
        return self.storyline_manager.get_rivalries()
    
    def get_rivalry_details(self, rivalry_id):
        """Get detailed information about a rivalry"""
        return self.storyline_manager.get_rivalry_details(rivalry_id) 