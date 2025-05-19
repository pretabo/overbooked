# promo_engine.py

from promo.promo_engine_helpers import *
import random
import statistics

class PromoEngine:
    def __init__(self, wrestler, crowd_reaction=50, tone="boast", theme="legacy"):
        # Extract wrestler stats directly from the wrestler object
        self.stats = {
            "promo_delivery": wrestler.get("promo_delivery", 10),
            "fan_engagement": wrestler.get("fan_engagement", 10),
            "entrance_presence": wrestler.get("entrance_presence", 10),
            "presence_under_fire": wrestler.get("presence_under_fire", 10),
            "confidence": wrestler.get("confidence", 10),
            "focus": wrestler.get("focus", 10),
            "resilience": wrestler.get("resilience", 10),
            "adaptability": wrestler.get("adaptability", 10),
            "risk_assessment": wrestler.get("risk_assessment", 10),
            "determination": wrestler.get("determination", 10),
            "reputation": wrestler.get("reputation", 10)
        }
        self.crowd_reaction = crowd_reaction
        self.momentum = 0
        self.confidence = self.stats.get("confidence", 50)
        self.phase = "beginning"
        self.beat_number = 0
        self.beats = []
        self.max_beats = random.randint(24, 49)  # Variable promo length
        self.end_beats_remaining = 0
        self.streak_info = {"count": 0, "quality": 0, "last_score": 0}
        self.end_cash_in_done = False  # Track if we've done the end phase cash-in
        self.tone = tone  # Store the promo tone
        self.theme = theme  # Store the promo theme

    def simulate(self):
        """Run a full promo simulation."""
        # Add intro beat
        intro_beat = {
            "tone": self.tone,
            "theme": self.theme,
            "phase": "opening",  # Changed from "beginning" to "opening" to match promo line buckets
            "momentum": self.momentum,
            "confidence": self.confidence,
            "is_first_beat": True,
            "score": 0
        }
        self.beats.append(intro_beat)
        
        while True:
            self.beat_number += 1
            cashed_in = False

            if self.phase == "beginning":
                beat = generate_beginning_beat(self.stats, self.beat_number, self.momentum, self.confidence, self.crowd_reaction)
                beat["phase"] = "opening"  # Map "beginning" phase to "opening" for promo lines
                if self.beat_number >= 3:
                    self.phase = "middle"
            elif self.phase == "middle":
                if should_start_end_phase(self.beat_number, self.max_beats, self.stats, self.momentum):
                    self.phase = "end"
                    self.end_beats_remaining = random.randint(3, 5)  # Variable end length
                    
                    # Do the end phase cash-in if we have momentum
                    if self.momentum > 0:
                        old_momentum = self.momentum
                        old_confidence = self.confidence
                        confidence_boost = self.momentum * 0.5  # Convert momentum to confidence at 50% rate
                        self.confidence = min(100, self.confidence + confidence_boost)
                        self.momentum = 0
                        cashed_in = True
                        self.end_cash_in_done = True
                else:
                    # Store current values before potential cash-in
                    old_momentum = self.momentum
                    old_confidence = self.confidence
                    
                    # Check for potential momentum cash-in
                    new_confidence, new_momentum, cashed_in = maybe_cash_in_momentum(
                        self.momentum, self.confidence, self.stats, self.beat_number
                    )
                    
                    if cashed_in:
                        self.confidence = new_confidence
                        self.momentum = new_momentum

                beat = generate_regular_beat(self.stats, self.beat_number, self.momentum, self.confidence, self.crowd_reaction, self.streak_info)
                beat["phase"] = "middle"  # Ensure middle phase is set
                
                if cashed_in:
                    # For cash-ins, store the pre-cash-in values and flag
                    beat["pre_cash_in_momentum"] = old_momentum
                    beat["pre_cash_in_confidence"] = old_confidence
                    beat["cash_in_used"] = True
                    beat["confidence_boost"] = self.confidence - old_confidence
            elif self.phase == "end":
                beat = generate_end_beat(self.stats, self.beat_number, self.momentum, self.confidence, self.crowd_reaction, self.streak_info)
                beat["phase"] = "ending"  # Map "end" phase to "ending" for promo lines
                self.end_beats_remaining -= 1
                if self.end_beats_remaining <= 0:
                    break
            else:
                break

            # Add tone and theme to the beat
            beat["tone"] = self.tone
            beat["theme"] = self.theme

            # Update streak info based on the beat's score
            score = beat.get("score", 0)
            if score >= 70:  # Good or better
                if self.streak_info["last_score"] >= 70:
                    self.streak_info["count"] += 1
                    self.streak_info["quality"] += score
                else:
                    self.streak_info["count"] = 1
                    self.streak_info["quality"] = score
            else:
                self.streak_info["count"] = 0
                self.streak_info["quality"] = 0
            self.streak_info["last_score"] = score

            beat["momentum_meter"] = self.momentum
            beat["confidence_level"] = self.confidence
            beat["streak_info"] = dict(self.streak_info)  # Store a copy of streak info

            self._apply_beat(beat)
            
        # Calculate final quality based on the last few beats
        final_scores = [b.get("score", 0) for b in self.beats[-3:]]  # Last 3 beats
        avg_final_score = sum(final_scores) / len(final_scores)
        
        if avg_final_score >= 90:
            final_quality = "perfect"
        elif avg_final_score >= 80:
            final_quality = "excellent"
        elif avg_final_score >= 70:
            final_quality = "good"
        elif avg_final_score >= 50:
            final_quality = "neutral"
        elif avg_final_score >= 30:
            final_quality = "bad"
        elif avg_final_score >= 10:
            final_quality = "terrible"
        else:
            final_quality = "flop"
            
        # Add summary beat
        summary_beat = {
            "tone": self.tone,
            "theme": self.theme,
            "phase": "ending",  # Use "ending" for consistency with promo line buckets
            "momentum": self.momentum,
            "confidence": self.confidence,
            "is_last_beat": True,
            "final_quality": final_quality,
            "score": avg_final_score
        }
        self.beats.append(summary_beat)

        return self._calculate_final_result()

    def _apply_beat(self, beat):
        # Apply momentum change if not a cash-in
        if not beat.get("cash_in_used", False):
            momentum_gain = beat.get("momentum", 0) - self.momentum
            beat["momentum_gain"] = momentum_gain
            self.momentum = max(0, min(100, beat.get("momentum", 0)))
        else:
            # For cash-ins, show the actual momentum spent and confidence gained
            pre_cash_in_momentum = beat.get("pre_cash_in_momentum", 0)
            pre_cash_in_confidence = beat.get("pre_cash_in_confidence", 0)
            
            # Always show the momentum spent and confidence gained
            beat["momentum_gain"] = -pre_cash_in_momentum  # Make it negative to show spent
            beat["confidence_boost"] = self.confidence - pre_cash_in_confidence
            self.momentum = 0  # Reset momentum after cash-in
            
        self.confidence = beat.get("confidence", self.confidence)
        beat["momentum"] = self.momentum
        beat["confidence"] = self.confidence
        
        # Calculate rolling rating for this beat
        scores = [b.get("score", 0) for b in self.beats] + [beat.get("score", 0)]
        weighted_scores = []
        for score in scores:
            if score >= 85:  # Excellent scores get 2x weight
                weighted_scores.extend([score, score])
            elif score >= 70:  # Good scores get 1.5x weight
                weighted_scores.extend([score, score * 0.5])
            else:
                weighted_scores.append(score)
        
        avg_score = sum(weighted_scores) / len(weighted_scores)
        score_std = statistics.stdev(scores) if len(scores) > 1 else 0
        consistency_bonus = max(0, (20 - score_std) / 20) * 5
        
        # Calculate finish bonus based on last 3 beats
        finish_bonus = 0
        if len(scores) >= 3:
            final_beats_avg = sum(scores[-3:]) / 3
            if final_beats_avg >= 85:
                finish_bonus = 5
            elif final_beats_avg >= 70:
                finish_bonus = 3
        
        rolling_rating = avg_score + consistency_bonus + finish_bonus
        rolling_rating = max(0, min(100, rolling_rating))
        beat["rolling_rating"] = round(rolling_rating, 2)
        
        # Convert rating to stars (0-5 stars, can go over 5 for exceptional performances)
        star_rating = (rolling_rating / 20)  # 100 rating = 5 stars
        beat["star_rating"] = round(star_rating, 2)
        
        self.beats.append(beat)

    def _calculate_final_result(self):
        scores = [b["score"] for b in self.beats]
        
        # Calculate weighted average giving more weight to high scores
        weighted_scores = []
        for score in scores:
            if score >= 85:  # Excellent scores get 2x weight
                weighted_scores.extend([score, score])
            elif score >= 70:  # Good scores get 1.5x weight
                weighted_scores.extend([score, score * 0.5])
            else:
                weighted_scores.append(score)
        
        avg_score = sum(weighted_scores) / len(weighted_scores)
        
        # Bonus for consistency
        score_std = statistics.stdev(scores) if len(scores) > 1 else 0
        consistency_bonus = max(0, (20 - score_std) / 20) * 5  # Up to +5 points for consistency
        
        # Bonus for strong finish (last 3 beats)
        finish_bonus = 0
        if len(scores) >= 3:
            final_beats_avg = sum(scores[-3:]) / 3
            if final_beats_avg >= 85:
                finish_bonus = 5
            elif final_beats_avg >= 70:
                finish_bonus = 3
        
        final_rating = avg_score + consistency_bonus + finish_bonus
        final_rating = max(0, min(100, final_rating))
        
        return {
            "final_rating": round(final_rating, 2),
            "avg_score": avg_score,
            "consistency_bonus": consistency_bonus,
            "finish_bonus": finish_bonus,
            "beats": self.beats
        }
