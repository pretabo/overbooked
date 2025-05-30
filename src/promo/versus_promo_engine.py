"""
Versus Promo Engine implementation for Overbooked
This engine allows two wrestlers to perform promos against each other
"""

from src.promo.promo_engine import PromoEngine
import random
import statistics
import math
from src.promo.promo_engine_helpers import roll_promo_score
from src.promo.promo_lines import get_versus_promo_line

def get_attribute(wrestler, attr_name, default=50):
    """Helper function to get attributes from wrestler object with fallback default."""
    # Check if wrestler is an object with attributes
    if hasattr(wrestler, attr_name):
        return getattr(wrestler, attr_name)
        
    # Check if wrestler is a dictionary
    if isinstance(wrestler, dict):
        # Check direct attributes
        if attr_name in wrestler:
            return wrestler[attr_name]
            
        # Check in attributes dict
        if "attributes" in wrestler:
            attrs = wrestler["attributes"]
            if isinstance(attrs, dict) and attr_name in attrs:
                return attrs[attr_name]
    
    return default

# Custom promo lines for versus promos
VERSUS_PROMO_LINES = {
    "opening": {
        "boast": [
            "{self} has been waiting for this moment...",
            "You think you can stand in {self}'s ring, {opponent}?",
            "Let me tell you something about respect, {opponent}..."
        ],
        "challenge": [
            "I'm calling you out right here, right now, {opponent}!",
            "You've been running your mouth long enough, {opponent}!",
            "Time to put your money where your mouth is, {opponent}!"
        ],
        "storyline": [
            "This rivalry between {self} and {opponent} has been building for weeks...",
            "You've crossed the line one too many times, {opponent}...",
            "It's time to settle this once and for all, {opponent}..."
        ]
    },
    "middle": {
        "response": [
            "You talk a good game, {opponent}, but can you back it up?",
            "I've heard it all before from {opponent}, and I'm still standing!",
            "Your words mean nothing in this ring, {opponent}!"
        ],
        "counter": [
            "While you were talking, {self} was training!",
            "You think you're special, {opponent}? {self} has beaten better!",
            "Your legacy ends when you step in the ring with {self}!"
        ]
    },
    "ending": {
        "closing": [
            "This Sunday, {self} will show {opponent} what a real champion looks like!",
            "Your time is up, {opponent}, {self}'s time is now!",
            "The only thing you'll be remembered for, {opponent}, is losing to {self}!"
        ]
    }
}

class VersusPromoEngine:
    """Engine to simulate a promo battle between two wrestlers."""
    
    def __init__(self, wrestler1, wrestler2):
        self.wrestler1 = wrestler1
        self.wrestler2 = wrestler2
        self.beats = []
        
        # Get the relevant stats
        self.w1_charisma = get_attribute(wrestler1, "charisma", 50)
        self.w1_showmanship = get_attribute(wrestler1, "showmanship", 50)
        self.w1_microphone = get_attribute(wrestler1, "microphone", 50)
        self.w1_intelligence = get_attribute(wrestler1, "intelligence", 50)
        self.w1_aggression = get_attribute(wrestler1, "aggression", 50)
        
        self.w2_charisma = get_attribute(wrestler2, "charisma", 50)
        self.w2_showmanship = get_attribute(wrestler2, "showmanship", 50)
        self.w2_microphone = get_attribute(wrestler2, "microphone", 50)
        self.w2_intelligence = get_attribute(wrestler2, "intelligence", 50)
        self.w2_aggression = get_attribute(wrestler2, "aggression", 50)
        
        # Track momentum for each wrestler
        self.w1_momentum = 0
        self.w2_momentum = 0
        
        # Track confidence for each wrestler
        self.w1_confidence = 50
        self.w2_confidence = 50
        
        # Keep track of scores
        self.w1_scores = []
        self.w2_scores = []
        
    def simulate(self):
        """Simulate the entire promo battle and return results."""
        # Add intro
        self._add_intro()
        
        # Determine number of exchanges (4-6 normally)
        num_exchanges = random.randint(4, 6)
        
        # Simulate each exchange
        for i in range(num_exchanges):
            phase = "opening" if i == 0 else "ending" if i == num_exchanges - 1 else "middle"
            self._simulate_exchange(phase)
        
        # Add a summary beat
        self._add_summary()
        
        # Calculate final scores
        final_scores = self._calculate_final_scores()
        
        return {
            "beats": self.beats,
            "final_scores": final_scores
        }
    
    def _add_intro(self):
        """Add an introductory beat to set the scene."""
        # Get names safely
        w1_name = self.wrestler1.name if hasattr(self.wrestler1, 'name') else self.wrestler1['name'] if isinstance(self.wrestler1, dict) else str(self.wrestler1)
        w2_name = self.wrestler2.name if hasattr(self.wrestler2, 'name') else self.wrestler2['name'] if isinstance(self.wrestler2, dict) else str(self.wrestler2)
        
        intro_text = f"{w1_name} and {w2_name} face off in the ring, microphones in hand."
        
        # Format as a beat
        intro_beat = {
            "promo_line": intro_text,
            "phase": "opening",
            "is_intro": True,
            "wrestler": None,  # No specific wrestler speaking
            "momentum": 0,
            "confidence": 50
        }
        
        self.beats.append(intro_beat)
    
    def _add_summary(self):
        """Add a summary beat to conclude the promo battle."""
        # Get names safely
        w1_name = self.wrestler1.name if hasattr(self.wrestler1, 'name') else self.wrestler1['name'] if isinstance(self.wrestler1, dict) else str(self.wrestler1)
        w2_name = self.wrestler2.name if hasattr(self.wrestler2, 'name') else self.wrestler2['name'] if isinstance(self.wrestler2, dict) else str(self.wrestler2)
        
        # Determine who had better overall scores
        w1_avg = statistics.mean(self.w1_scores) if self.w1_scores else 0
        w2_avg = statistics.mean(self.w2_scores) if self.w2_scores else 0
        
        if w1_avg > w2_avg + 10:
            summary_text = f"{w1_name} clearly dominated this verbal exchange, leaving {w2_name} struggling to respond."
        elif w2_avg > w1_avg + 10:
            summary_text = f"{w2_name} clearly dominated this verbal exchange, leaving {w1_name} struggling to respond."
        elif w1_avg > w2_avg + 5:
            summary_text = f"{w1_name} got the better of {w2_name} in this war of words."
        elif w2_avg > w1_avg + 5:
            summary_text = f"{w2_name} got the better of {w1_name} in this war of words."
        else:
            summary_text = f"The verbal exchange between {w1_name} and {w2_name} was evenly matched."
        
        # Format as a beat
        summary_beat = {
            "promo_line": summary_text,
            "phase": "ending",
            "is_summary": True,
            "wrestler": None,  # No specific wrestler speaking
            "momentum": max(self.w1_momentum, self.w2_momentum),
            "confidence": 50
        }
        
        self.beats.append(summary_beat)
    
    def _simulate_exchange(self, phase):
        """Simulate a verbal exchange between the two wrestlers."""
        # Determine who goes first (50/50 chance, but slightly favoring wrestler with momentum)
        w1_goes_first = random.random() < 0.5 + (self.w1_momentum - self.w2_momentum) / 200
        
        # Simulate the first wrestler's promo
        if w1_goes_first:
            self._simulate_promo_line(self.wrestler1, self.wrestler2, phase, "first")
            self._simulate_promo_line(self.wrestler2, self.wrestler1, phase, "response")
        else:
            self._simulate_promo_line(self.wrestler2, self.wrestler1, phase, "first")
            self._simulate_promo_line(self.wrestler1, self.wrestler2, phase, "response")
    
    def _simulate_promo_line(self, speaker, target, phase, position):
        """Simulate a single promo line from one wrestler to another."""
        # Determine the tone based on aggression and position
        if speaker == self.wrestler1:
            aggression = self.w1_aggression
            speaker_momentum = self.w1_momentum
            speaker_confidence = self.w1_confidence
        else:
            aggression = self.w2_aggression
            speaker_momentum = self.w2_momentum
            speaker_confidence = self.w2_confidence
        
        # Higher aggression means more likely to use aggressive tones
        aggressive_chance = aggression / 100
        
        if position == "first":
            # First speaker sets the tone
            if random.random() < aggressive_chance:
                tone = random.choice(["insult", "challenge", "callout"])
            else:
                tone = random.choice(["boast", "humble"])
        else:
            # Response usually matches or escalates
            prev_beat = self.beats[-1]
            prev_tone = prev_beat.get("tone", "boast")
            
            if prev_tone in ["insult", "challenge", "callout"]:
                # Respond to aggression
                if random.random() < aggressive_chance:
                    # Respond aggressively
                    tone = random.choice(["insult", "challenge", "callout"])
                else:
                    # Deflect
                    tone = random.choice(["boast", "humble"])
            else:
                # Respond to non-aggression
                if random.random() < aggressive_chance:
                    # Escalate
                    tone = random.choice(["insult", "challenge", "callout"])
                else:
                    # Stay calm
                    tone = random.choice(["boast", "humble"])
        
        # Get a promo line
        promo_line = get_versus_promo_line(tone, phase, position)
        
        # Replace placeholders with wrestler names
        promo_line = promo_line.replace("[WRESTLER]", speaker["name"])
        promo_line = promo_line.replace("[OPPONENT]", target["name"])
        
        # Roll for promo quality
        if speaker == self.wrestler1:
            # Create stats dictionary
            stats = {
                "promo_delivery": self.w1_microphone,
                "charisma": self.w1_charisma,
                "showmanship": self.w1_showmanship,
                "intelligence": self.w1_intelligence,
                "aggression": self.w1_aggression
            }
            
            # Add randomness to create more varied scores
            quality_roll = roll_promo_score(
                stats,
                1,  # beat number
                self.w1_momentum,
                self.w1_confidence,
                50  # default crowd reaction
            )
            
            # Add random variation to scores (-15 to +10)
            # Extract the score from the tuple returned by roll_promo_score
            base_score = quality_roll[0]  # The first element is the score
            variation = random.randint(-15, 10)
            quality_roll = max(30, min(99, base_score + variation))
            
            # Update momentum and confidence based on quality
            momentum_change = (quality_roll - 50) / 10
            self.w1_momentum = max(0, min(100, self.w1_momentum + momentum_change))
            
            confidence_change = (quality_roll - 50) / 15
            self.w1_confidence = max(30, min(70, self.w1_confidence + confidence_change))
            
            # Add to score tracking
            self.w1_scores.append(quality_roll)
        else:
            # Create stats dictionary
            stats = {
                "promo_delivery": self.w2_microphone,
                "charisma": self.w2_charisma,
                "showmanship": self.w2_showmanship,
                "intelligence": self.w2_intelligence,
                "aggression": self.w2_aggression
            }
            
            # Add randomness to create more varied scores
            quality_roll = roll_promo_score(
                stats,
                1,  # beat number
                self.w2_momentum,
                self.w2_confidence,
                50  # default crowd reaction
            )
            
            # Add random variation to scores (-15 to +10)
            # Extract the score from the tuple returned by roll_promo_score
            base_score = quality_roll[0]  # The first element is the score
            variation = random.randint(-15, 10)
            quality_roll = max(30, min(99, base_score + variation))
            
            # Update momentum and confidence based on quality
            momentum_change = (quality_roll - 50) / 10
            self.w2_momentum = max(0, min(100, self.w2_momentum + momentum_change))
            
            confidence_change = (quality_roll - 50) / 15
            self.w2_confidence = max(30, min(70, self.w2_confidence + confidence_change))
            
            # Add to score tracking
            self.w2_scores.append(quality_roll)
        
        # If this is a response, impact the previous speaker's confidence
        if position == "response":
            if quality_roll >= 80:  # Great response
                if speaker == self.wrestler1:
                    self.w2_confidence = max(0, self.w2_confidence - 10)
                    self.w2_momentum = max(0, self.w2_momentum - 5)
                else:
                    self.w1_confidence = max(0, self.w1_confidence - 10)
                    self.w1_momentum = max(0, self.w1_momentum - 5)
        
        # Format as a beat
        beat = {
            "wrestler": speaker,
            "opponent": target,
            "promo_line": promo_line,
            "tone": tone,
            "phase": phase,
            "position": position,
            "score": quality_roll,
            "momentum": speaker_momentum,
            "confidence": speaker_confidence,
            "is_versus_beat": True
        }
        
        self.beats.append(beat)
    
    def _calculate_final_scores(self):
        """Calculate the final scores for the promo battle."""
        # Calculate average scores
        w1_avg = statistics.mean(self.w1_scores) if self.w1_scores else 0
        w2_avg = statistics.mean(self.w2_scores) if self.w2_scores else 0
        
        # Calculate competition bonus (how close the two were)
        score_diff = abs(w1_avg - w2_avg)
        if score_diff < 5:
            competition_bonus = 10  # Very close contest
        elif score_diff < 10:
            competition_bonus = 5   # Somewhat close
        elif score_diff < 20:
            competition_bonus = 2   # One side dominated
        else:
            competition_bonus = 0   # Complete domination
        
        # Calculate quality bonus (how good the promos were overall)
        overall_avg = (w1_avg + w2_avg) / 2
        if overall_avg >= 85:
            quality_bonus = 10  # Excellent promo battle
        elif overall_avg >= 75:
            quality_bonus = 5   # Good promo battle
        elif overall_avg >= 65:
            quality_bonus = 2   # Decent promo battle
        else:
            quality_bonus = 0   # Poor promo battle
        
        # Calculate overall score
        overall_score = (w1_avg + w2_avg) / 2 + competition_bonus + quality_bonus
        
        return {
            "wrestler1_score": w1_avg,
            "wrestler2_score": w2_avg,
            "competition_bonus": competition_bonus,
            "quality_bonus": quality_bonus,
            "overall_score": overall_score
        } 