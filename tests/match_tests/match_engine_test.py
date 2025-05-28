#!/usr/bin/env python3
"""
Test script for the match engine with move tracking
"""

import os
import sys
import sqlite3
import random
from match_engine import load_wrestler_by_id
from match_engine_utils import select_progressive_manoeuvre, move_success
from db.utils import db_path


def run_simple_match(w1, w2):
    """Run a simplified match between two wrestlers"""
    print(f"Match: {w1['name']} vs {w2['name']}")
    
    turns = 20
    move_log = []
    
    for turn in range(1, turns + 1):
        # Select a move
        name, move_type, damage, difficulty = select_progressive_manoeuvre(turn)
        
        # Determine which wrestler is attacking
        if turn % 2 == 1:
            attacker, defender = w1, w2
        else:
            attacker, defender = w2, w1
        
        # Check if move succeeds
        try:
            from match_engine_utils import move_success
            success, score, chance = move_success(attacker, move_type, difficulty)
        except Exception as e:
            print(f"Error with move_success: {e}")
            success = random.random() > 0.3
            score = random.random()
            chance = 0.7
        
        # Log the move
        move_entry = {
            "wrestler_id": attacker.get("id", None),
            "move_name": name,
            "move_type": move_type,
            "category": "regular",
            "success": success,
            "experience": 0  # Will be populated later
        }
        move_log.append(move_entry)
        
        # Print the result
        result = "succeeds" if success else "fails"
        print(f"Turn {turn}: {attacker['name']} {result} with {name}")
    
    # Print move report
    print("\n===== MATCH MOVE USAGE REPORT =====")
    print(f"{w1['name']} vs {w2['name']}")
    print("=" * 40)
    
    # Group moves by wrestler
    moves_by_wrestler = {}
    for move_entry in move_log:
        wrestler_id = move_entry.get("wrestler_id")
        wrestler_name = w1["name"] if wrestler_id == w1["id"] else w2["name"]
        
        if wrestler_name not in moves_by_wrestler:
            moves_by_wrestler[wrestler_name] = {
                "signature": [],
                "finisher": [],
                "regular": {
                    "grapple": [],
                    "strike": [],
                    "slam": [],
                    "submission": [],
                    "aerial": [],
                    "other": []
                },
                "totals": {
                    "success": 0,
                    "fail": 0,
                    "total": 0
                }
            }
        
        # Add the move to the appropriate category
        move_name = move_entry["move_name"]
        move_success = move_entry["success"]
        move_type = move_entry.get("move_type", "other")
        move_category = move_entry.get("category", "regular")
        
        # Update totals
        moves_by_wrestler[wrestler_name]["totals"]["total"] += 1
        if move_success:
            moves_by_wrestler[wrestler_name]["totals"]["success"] += 1
        else:
            moves_by_wrestler[wrestler_name]["totals"]["fail"] += 1
        
        # Store move details
        move_record = {
            "name": move_name,
            "success": move_success,
            "experience": move_entry.get("experience", 0)
        }
        
        if move_category == "signature":
            moves_by_wrestler[wrestler_name]["signature"].append(move_record)
        elif move_category == "finisher":
            moves_by_wrestler[wrestler_name]["finisher"].append(move_record)
        else:
            # Add to regular moves by type
            if move_type in moves_by_wrestler[wrestler_name]["regular"]:
                moves_by_wrestler[wrestler_name]["regular"][move_type].append(move_record)
            else:
                moves_by_wrestler[wrestler_name]["regular"]["other"].append(move_record)
    
    # Print report for each wrestler
    for wrestler_name, move_data in moves_by_wrestler.items():
        total_moves = move_data["totals"]["total"]
        success_moves = move_data["totals"]["success"]
        success_rate = (success_moves / total_moves * 100) if total_moves > 0 else 0
        
        print(f"\n{wrestler_name}'s Moves:")
        print(f"Total moves: {total_moves} | Success rate: {success_rate:.1f}%")
        
        # Print signature moves
        if move_data["signature"]:
            print("\n  Signature Moves:")
            for move in move_data["signature"]:
                result = "✅ HIT" if move["success"] else "❌ MISS"
                print(f"    {move['name']} - {result} (Exp: {move['experience']})")
        
        # Print finisher moves
        if move_data["finisher"]:
            print("\n  Finisher Moves:")
            for move in move_data["finisher"]:
                result = "✅ HIT" if move["success"] else "❌ MISS"
                print(f"    {move['name']} - {result} (Exp: {move['experience']})")
        
        # Print regular moves by type
        print("\n  Regular Moves:")
        for move_type, moves in move_data["regular"].items():
            if moves:
                print(f"\n    {move_type.upper()}:")
                for move in moves:
                    result = "✅ HIT" if move["success"] else "❌ MISS"
                    print(f"      {move['name']} - {result} (Exp: {move['experience']})")
        
        print("-" * 40)


def test_match():
    """Run a test match between two wrestlers"""
    print("Loading wrestlers...")
    
    # Get two random wrestlers
    conn = sqlite3.connect(db_path("wrestlers.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM wrestlers ORDER BY RANDOM() LIMIT 2")
    wrestlers = cursor.fetchall()
    conn.close()
    
    if len(wrestlers) < 2:
        print("Not enough wrestlers in the database")
        return
    
    w1_id, w1_name = wrestlers[0]
    w2_id, w2_name = wrestlers[1]
    
    print(f"Selected wrestlers: {w1_name} vs {w2_name}")
    
    # Load full wrestler data
    w1 = load_wrestler_by_id(w1_id)
    w2 = load_wrestler_by_id(w2_id)
    
    if not w1 or not w2:
        print("Failed to load wrestler data")
        return
    
    # Run the simplified match
    print("\n=== MATCH START ===\n")
    run_simple_match(w1, w2)
    print("\n=== MATCH END ===\n")


if __name__ == "__main__":
    test_match() 