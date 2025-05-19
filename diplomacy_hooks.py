# diplomacy_hooks.py

def handle_match_relationship_effects(wrestler1, wrestler2, match_result, diplomacy_system):
    """
    Analyze match result stats and adjust diplomacy between the two wrestlers.

    wrestler1, wrestler2: Wrestler objects (dicts)
    match_result: dict containing match statistics
    diplomacy_system: instance of DiplomacySystem
    """
    quality = match_result.get('quality', 50)
    drama = match_result.get('drama_score', 50)
    blood = match_result.get('blood', False)
    injury = match_result.get('injury', False)

    # Base respect adjustment for any competitive match
    if drama >= 80:
        diplomacy_system.adjust_relationship(wrestler1, wrestler2, "Epic Match - Respect Earned", +10)
    elif drama <= 40:
        diplomacy_system.adjust_relationship(wrestler1, wrestler2, "Squash Match - Resentment", -5)

    # Blood amplifies grudges
    if blood:
        diplomacy_system.adjust_relationship(wrestler1, wrestler2, "Bloody Battle - Rivalry Deepens", -10)

    # Injuries cause bad blood
    if injury:
        diplomacy_system.adjust_relationship(wrestler1, wrestler2, "Injury Incident - Hatred Spikes", -20)

    # Title Matches (optional)
    if match_result.get('is_title_match', False):
        if drama >= 70:
            diplomacy_system.adjust_relationship(wrestler1, wrestler2, "Title War - Respect Grows", +15)
        else:
            diplomacy_system.adjust_relationship(wrestler1, wrestler2, "Title Loss Resentment", -10)

    # Rematch bonus (optional if tracked)
    if match_result.get('is_rematch', False):
        diplomacy_system.adjust_relationship(wrestler1, wrestler2, "Ongoing Rivalry", -5)

    # Debug log
    print(f"Diplomacy updated between {wrestler1['name']} and {wrestler2['name']} after match.")
