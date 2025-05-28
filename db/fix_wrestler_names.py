#!/usr/bin/env python3
"""
Utility script to fix any existing wrestlers with empty names or finisher names.
This script:
1. Finds wrestlers with empty names and either deletes them or assigns generic names
2. Finds finishers with empty names and assigns wrestler-specific finisher names
3. Automatically cleans up orphaned finishers and signature moves
"""

import sqlite3
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.utils import db_path

def fix_empty_names(auto_cleanup=True):
    """Find and fix any wrestlers with empty names"""
    conn = sqlite3.connect(db_path("wrestlers.db"))
    conn.execute(f"ATTACH DATABASE '{db_path('finishers.db')}' AS fdb")
    cursor = conn.cursor()
    
    # Find wrestlers with empty names
    cursor.execute("SELECT id FROM wrestlers WHERE name IS NULL OR name = ''")
    empty_name_ids = [row[0] for row in cursor.fetchall()]
    
    if empty_name_ids:
        print(f"Found {len(empty_name_ids)} wrestlers with empty names")
        
        if auto_cleanup:
            # Automatically delete wrestlers with empty names
            for wrestler_id in empty_name_ids:
                # Delete from wrestler_attributes
                cursor.execute("DELETE FROM wrestler_attributes WHERE wrestler_id = ?", (wrestler_id,))
                
                # Delete from wrestler_signature_moves
                cursor.execute("DELETE FROM wrestler_signature_moves WHERE wrestler_id = ?", (wrestler_id,))
                
                # Delete the wrestler
                cursor.execute("DELETE FROM wrestlers WHERE id = ?", (wrestler_id,))
                
                print(f"Deleted wrestler ID {wrestler_id}")
            
            conn.commit()
            print(f"Deleted {len(empty_name_ids)} wrestlers with empty names")
        else:
            # Option: Ask user what to do
            choice = input("Do you want to DELETE these wrestlers? (y/n): ").strip().lower()
            if choice == 'y':
                for wrestler_id in empty_name_ids:
                    # Delete from wrestler_attributes
                    cursor.execute("DELETE FROM wrestler_attributes WHERE wrestler_id = ?", (wrestler_id,))
                    
                    # Delete from wrestler_signature_moves
                    cursor.execute("DELETE FROM wrestler_signature_moves WHERE wrestler_id = ?", (wrestler_id,))
                    
                    # Delete the wrestler
                    cursor.execute("DELETE FROM wrestlers WHERE id = ?", (wrestler_id,))
                    
                    print(f"Deleted wrestler ID {wrestler_id}")
                
                conn.commit()
                print(f"Deleted {len(empty_name_ids)} wrestlers with empty names")
            else:
                # Option 2: Assign generic names to wrestlers with empty names
                print("Assigning generic names to wrestlers with empty names...")
                for i, wrestler_id in enumerate(empty_name_ids):
                    new_name = f"Unnamed Wrestler {i+1}"
                    cursor.execute("UPDATE wrestlers SET name = ? WHERE id = ?", 
                                (new_name, wrestler_id))
                    print(f"Updated wrestler ID {wrestler_id} name to '{new_name}'")
                
                conn.commit()
                print(f"Updated {len(empty_name_ids)} wrestlers with generic names")
    else:
        print("No wrestlers with empty names found.")
    
    # Find wrestlers with empty finisher names
    cursor.execute("""
        SELECT w.id, w.name, f.id
        FROM wrestlers w
        JOIN finishers f ON w.finisher_id = f.id
        WHERE f.name IS NULL OR f.name = ''
    """)
    empty_finisher_rows = cursor.fetchall()
    
    if empty_finisher_rows:
        print(f"Found {len(empty_finisher_rows)} wrestlers with empty finisher names")
        
        for wrestler_id, wrestler_name, finisher_id in empty_finisher_rows:
            # Create finisher name based on wrestler name
            new_finisher_name = f"{wrestler_name}'s Finisher"
            
            # Update the finisher name
            cursor.execute("UPDATE finishers SET name = ? WHERE id = ?", 
                          (new_finisher_name, finisher_id))
            print(f"Updated finisher ID {finisher_id} name to '{new_finisher_name}'")
        
        conn.commit()
        print(f"Updated {len(empty_finisher_rows)} finishers with proper names")
    else:
        print("No wrestlers with empty finisher names found.")
    
    # Check for orphaned finishers and signature moves
    cursor.execute("""
        SELECT f.id, f.name 
        FROM finishers f 
        LEFT JOIN wrestlers w ON f.id = w.finisher_id 
        WHERE w.id IS NULL
    """)
    orphaned_finishers = cursor.fetchall()
    
    if orphaned_finishers:
        print(f"Found {len(orphaned_finishers)} orphaned finishers")
        
        if auto_cleanup:
            # Automatically delete orphaned finishers
            for finisher_id, finisher_name in orphaned_finishers:
                cursor.execute("DELETE FROM finishers WHERE id = ?", (finisher_id,))
                print(f"Deleted orphaned finisher ID {finisher_id} '{finisher_name}'")
            
            conn.commit()
            print(f"Deleted {len(orphaned_finishers)} orphaned finishers")
        else:
            # Ask for confirmation
            choice = input("Do you want to DELETE these orphaned finishers? (y/n): ").strip().lower()
            if choice == 'y':
                for finisher_id, finisher_name in orphaned_finishers:
                    cursor.execute("DELETE FROM finishers WHERE id = ?", (finisher_id,))
                    print(f"Deleted orphaned finisher ID {finisher_id} '{finisher_name}'")
                
                conn.commit()
                print(f"Deleted {len(orphaned_finishers)} orphaned finishers")
    else:
        print("No orphaned finishers found.")
    
    cursor.execute("""
        SELECT sm.id, sm.name 
        FROM signature_moves sm 
        LEFT JOIN wrestler_signature_moves wsm ON sm.id = wsm.signature_move_id 
        WHERE wsm.wrestler_id IS NULL
    """)
    orphaned_signatures = cursor.fetchall()
    
    if orphaned_signatures:
        print(f"Found {len(orphaned_signatures)} orphaned signature moves")
        
        if auto_cleanup:
            # Automatically delete orphaned signature moves
            for sig_id, sig_name in orphaned_signatures:
                cursor.execute("DELETE FROM signature_moves WHERE id = ?", (sig_id,))
                print(f"Deleted orphaned signature move ID {sig_id} '{sig_name}'")
            
            conn.commit()
            print(f"Deleted {len(orphaned_signatures)} orphaned signature moves")
        else:
            # Ask for confirmation
            choice = input("Do you want to DELETE these orphaned signature moves? (y/n): ").strip().lower()
            if choice == 'y':
                for sig_id, sig_name in orphaned_signatures:
                    cursor.execute("DELETE FROM signature_moves WHERE id = ?", (sig_id,))
                    print(f"Deleted orphaned signature move ID {sig_id} '{sig_name}'")
                
                conn.commit()
                print(f"Deleted {len(orphaned_signatures)} orphaned signature moves")
    else:
        print("No orphaned signature moves found.")
    
    conn.close()
    
if __name__ == "__main__":
    print("Fixing wrestler and finisher names in the database...")
    # Run with auto_cleanup=True to automatically clean up without asking for confirmation
    fix_empty_names(auto_cleanup=True)
    print("Done!") 