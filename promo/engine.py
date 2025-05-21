"""
Simplified promo engine interface for testing and debugging.
"""

import random
import time
import logging
from promo.promo_engine import PromoEngine

def generate_promo(wrestler, focus=10, difficulty=10, style="boast", theme="legacy"):
    """
    Generate a promo for a wrestler.
    
    Args:
        wrestler: Wrestler data dictionary
        focus: Focus level of the wrestler (1-20)
        difficulty: Difficulty of the promo (1-20)
        style: Style of the promo (boast, callout, etc.)
        theme: Theme of the promo (legacy, revenge, etc.)
    
    Returns:
        A string containing the generated promo text
    """
    start_time = time.time()
    logging.info(f"Generating promo for {wrestler['name']} (Focus: {focus}, Difficulty: {difficulty})")
    
    # Prepare the wrestler with additional parameters needed for promos
    enhanced_wrestler = wrestler.copy()
    enhanced_wrestler["focus"] = focus
    enhanced_wrestler["promo_delivery"] = random.randint(8, 15)
    enhanced_wrestler["fan_engagement"] = random.randint(8, 15)
    enhanced_wrestler["entrance_presence"] = random.randint(8, 15)
    enhanced_wrestler["presence_under_fire"] = random.randint(8, 15)
    enhanced_wrestler["confidence"] = random.randint(8, 15)
    enhanced_wrestler["resilience"] = random.randint(8, 15)
    enhanced_wrestler["adaptability"] = random.randint(8, 15)
    enhanced_wrestler["risk_assessment"] = random.randint(8, 15)
    enhanced_wrestler["determination"] = random.randint(8, 15)
    
    # Try to use PromoEngine or fall back to simple template
    try:
        promo_engine = PromoEngine(enhanced_wrestler, crowd_reaction=50, tone=style, theme=theme)
        result = promo_engine.simulate()
        promo_text = f"[{wrestler['name']}]: "
        
        # Generate sample promo text
        promo_lines = []
        
        # Add introduction
        promo_lines.append(f"Let me tell you something about {wrestler['name']}!")
        
        # Add body based on style and theme
        if style == "boast":
            promo_lines.append(f"I am the greatest {theme} wrestler to ever step in this ring!")
            promo_lines.append(f"Nobody can match my {wrestler.get('strength', 'power')} or my {wrestler.get('charisma', 'charisma')}!")
        elif style == "callout":
            promo_lines.append(f"I'm calling out anyone who thinks they can take me on!")
            promo_lines.append(f"You think you understand {theme}? You don't know what it means until you face me!")
        else:
            promo_lines.append(f"This business is all about {theme}, and I embody that every single day!")
            
        # Add conclusion
        promo_lines.append(f"And that's why they call me {wrestler['name']}!")
        
        # Join all the lines with proper spacing
        promo_text += " ".join(promo_lines)
    except Exception as e:
        logging.error(f"Error generating promo with PromoEngine: {e}")
        # Fallback to a simple template
        promo_text = f"[{wrestler['name']}]: Listen up! I am {wrestler['name']} and I am here to dominate this ring!"
    
    duration = time.time() - start_time
    logging.info(f"Promo generation completed in {duration:.2f}s")
    
    return promo_text 