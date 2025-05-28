"""
Custom commentary engine for wrestling promos with improved beat type detection.
This file contains a fixed version of the generate_commentary function.
"""

import random
from src.promo.commentary_engine import (
    get_quality_comment,
    get_special_trigger_comment,
    get_context_comment,
    get_cash_in_commentary,
    get_intro_line,
    get_summary_line,
    determine_line_quality
)

def fixed_generate_commentary(beat):
    """Enhanced version of generate_commentary that properly identifies beat types."""
    
    # Default values
    commentary = {
        'commentary_line': '',
        'score': beat.get('score', 50),
        'promo_line': beat.get('promo_line', ''),
        'is_intro': False,
        'is_summary': False,
        'is_cash_in': '🌟' in beat.get('promo_line', '')
    }
    
    # Only mark as intro if it's specifically an intro or has is_first_beat=True
    if beat.get('is_intro', False) or (beat.get('is_first_beat', False) and not beat.get('wrestler')):
        commentary['is_intro'] = True
        return commentary
        
    # Only mark as summary if it's specifically a summary or has is_last_beat=True
    if beat.get('is_summary', False) or (beat.get('is_last_beat', False) and not beat.get('wrestler')):
        commentary['is_summary'] = True
        return commentary
    
    # Get the score to determine commentary quality
    score = beat.get('score', 50)
    
    # Generate commentary based on score and phase
    phase = beat.get('phase', 'middle')
    
    # Check if this is a versus beat
    versus_mode = beat.get('versus_mode', False)
    
    # Commentary pool by score range
    if versus_mode:
        commentary_pool = {
            'great': [
                "That was a devastating verbal assault!",
                "The audience is going wild for that exchange!",
                "What a brilliant counter-point!",
                "That's how you dominate a verbal confrontation!"
            ],
            'good': [
                "Strong response in this back-and-forth.",
                "The crowd is loving this exchange.",
                "That landed perfectly in this war of words.",
                "Gaining the upper hand in this verbal duel."
            ],
            'average': [
                "This back-and-forth continues.",
                "The verbal jousting continues.",
                "Trading words in the center of the ring.",
                "Neither one backing down in this exchange."
            ],
            'poor': [
                "That response didn't quite land.",
                "Losing ground in this exchange.",
                "The crowd expected a stronger comeback.",
                "Struggling to find the right words."
            ],
            'bad': [
                "Completely outmatched in this exchange.",
                "That verbal jab missed by a mile.",
                "The audience is cringing at that response.",
                "Dropping the ball in this confrontation."
            ]
        }
    else:
        # Standard promo commentary pool by phase and score
        commentary_pool = {
            'opening': {
                'great': [
                    "What a strong opening!",
                    "That's how you kick off a promo!",
                    "Perfect way to start things off!",
                    "The crowd is loving this opening!"
                ],
                'good': [
                    "Solid start to this promo.",
                    "Good energy to begin with.",
                    "Nice opening by the superstar.",
                    "Starting things off on the right foot."
                ],
                'average': [
                    "Let's see where this goes.",
                    "A typical opening.",
                    "The crowd seems interested.",
                    "Starting with the basics."
                ],
                'poor': [
                    "A bit of a slow start.",
                    "Not the strongest opening.",
                    "The crowd isn't quite connecting yet.",
                    "Needs to find a better rhythm."
                ],
                'bad': [
                    "Struggling to get started here.",
                    "The crowd is already restless.",
                    "Not the way you want to begin.",
                    "Completely missing the mark with this opening."
                ]
            },
            'middle': {
                'great': [
                    "The audience is completely captivated!",
                    "This is masterful mic work!",
                    "This promo is on another level!",
                    "We're witnessing something special here!"
                ],
                'good': [
                    "The crowd is really getting into this.",
                    "Strong words from the superstar.",
                    "They're building momentum nicely.",
                    "This promo is hitting all the right notes."
                ],
                'average': [
                    "The audience is paying attention.",
                    "This promo is moving along.",
                    "Keeping the crowd engaged.",
                    "Steady performance on the mic."
                ],
                'poor': [
                    "The crowd's attention is wavering.",
                    "Losing momentum here.",
                    "This promo needs more energy.",
                    "Not quite connecting with the audience."
                ],
                'bad': [
                    "The crowd is turning against this promo.",
                    "This is falling completely flat.",
                    "They've lost the audience entirely.",
                    "This promo is going nowhere fast."
                ]
            },
            'ending': {
                'great': [
                    "What a perfect finish!",
                    "That's how you close a promo!",
                    "The crowd is erupting!",
                    "An absolutely stellar conclusion!"
                ],
                'good': [
                    "Strong finish to this promo.",
                    "Ended on a high note.",
                    "The crowd appreciated that closing.",
                    "Solid way to wrap things up."
                ],
                'average': [
                    "And that concludes the promo.",
                    "A standard finish.",
                    "The crowd seems satisfied.",
                    "Wrapped up as expected."
                ],
                'poor': [
                    "That ending fell a bit flat.",
                    "Needed a stronger conclusion.",
                    "The crowd was expecting more.",
                    "A weak way to finish."
                ],
                'bad': [
                    "That ending completely missed the mark.",
                    "The crowd is disappointed with that finish.",
                    "A terrible way to conclude.",
                    "That promo ended with a whimper, not a bang."
                ]
            }
        }
    
    # Determine quality category based on score
    if score >= 85:
        quality = 'great'
    elif score >= 70:
        quality = 'good'
    elif score >= 50:
        quality = 'average'
    elif score >= 30:
        quality = 'poor'
    else:
        quality = 'bad'
    
    # Select a random commentary line from the appropriate pool
    if versus_mode:
        commentary['commentary_line'] = random.choice(commentary_pool[quality])
    else:
        if phase in commentary_pool and quality in commentary_pool[phase]:
            commentary['commentary_line'] = random.choice(commentary_pool[phase][quality])
        else:
            # Fallback to middle phase if the specified phase isn't found
            commentary['commentary_line'] = random.choice(commentary_pool['middle'][quality])
    
    return commentary 