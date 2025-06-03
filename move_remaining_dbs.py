#!/usr/bin/env python3
"""
Database Consolidation - Remaining Databases Migration

This script moves any remaining databases in the data directory to the /db directory
and updates their references in the code.
"""

import os
import shutil
import logging
import glob
import fileinput
import re
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("remaining_db_migration.log"),
        logging.StreamHandler()
    ]
)

def get_project_root():
    """Get the absolute path to the project root directory."""
    return os.path.dirname(os.path.abspath(__file__))

def find_remaining_databases():
    """Find any databases that are still in /data but not in /db."""
    root = get_project_root()
    remaining_dbs = []
    
    # Use glob to find all .db files in the data directory (excluding data/db symlink)
    for db_path in glob.glob(os.path.join(root, "data", "**", "*.db"), recursive=True):
        # Skip the data/db symlink directory
        if "/data/db/" in db_path.replace("\\", "/"):
            continue
            
        db_name = os.path.basename(db_path)
        target_path = os.path.join(root, "db", db_name)
        
        remaining_dbs.append((db_path, target_path))
    
    return remaining_dbs

def move_database(source_path, target_path):
    """Move a database file from source to target."""
    # Check if database already exists in target location
    if os.path.exists(target_path):
        # Compare file sizes to see if they're different
        source_size = os.path.getsize(source_path)
        target_size = os.path.getsize(target_path)
        
        if source_size > target_size:
            # Source is larger, backup target and replace
            backup_path = f"{target_path}.bak-{int(os.path.getmtime(target_path))}"
            logging.info(f"Target already exists but source is larger. Backing up target to {backup_path}")
            shutil.copy2(target_path, backup_path)
            shutil.copy2(source_path, target_path)
            return True
        elif target_size > source_size:
            # Target is larger, use that one
            logging.info(f"Target already exists and is larger than source. Keeping target.")
            return False
        else:
            # Same size, check if they're identical
            try:
                # Try to compare databases by opening them
                source_conn = sqlite3.connect(source_path)
                target_conn = sqlite3.connect(target_path)
                
                # Get schema from both databases
                source_tables = source_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                target_tables = target_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                
                if sorted([t[0] for t in source_tables]) != sorted([t[0] for t in target_tables]):
                    # Different schema, prefer the one with more tables
                    if len(source_tables) > len(target_tables):
                        backup_path = f"{target_path}.bak-{int(os.path.getmtime(target_path))}"
                        logging.info(f"Target exists but source has more tables. Backing up target to {backup_path}")
                        shutil.copy2(target_path, backup_path)
                        shutil.copy2(source_path, target_path)
                        return True
                    else:
                        logging.info(f"Target exists and has more tables than source. Keeping target.")
                        return False
                else:
                    # Same schema, keep target
                    logging.info(f"Target exists with identical schema. Keeping target.")
                    return False
                    
            except sqlite3.Error as e:
                # Can't compare databases, assume they're different and keep target
                logging.warning(f"Error comparing databases: {e}. Keeping target.")
                return False
    else:
        # Target doesn't exist, copy source to target
        logging.info(f"Moving database from {source_path} to {target_path}")
        shutil.copy2(source_path, target_path)
        return True

def update_references(source_path, db_name):
    """Update references to the database in code files."""
    root = get_project_root()
    relative_path = os.path.relpath(source_path, root)
    
    # Find all Python files that reference this database
    references = []
    for py_file in glob.glob(os.path.join(root, "**", "*.py"), recursive=True):
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if relative_path in content:
                    references.append(py_file)
        except Exception as e:
            logging.warning(f"Error reading {py_file}: {e}")
    
    # Update references
    for py_file in references:
        try:
            with fileinput.FileInput(py_file, inplace=True) as file:
                for line in file:
                    # Replace the old path with the new path using db_utils
                    if f'self.db_path = "{relative_path}"' in line:
                        print(line.replace(f'self.db_path = "{relative_path}"', f'self.db_path = "{db_name}"'), end='')
                    elif f'self.rivalry_db_path = "{relative_path}"' in line:
                        print(line.replace(f'self.rivalry_db_path = "{relative_path}"', f'self.rivalry_db_path = "{db_name}"'), end='')
                    elif f'"{relative_path}"' in line:
                        print(line.replace(f'"{relative_path}"', f'"db/{db_name}"'), end='')
                    else:
                        print(line, end='')
            
            logging.info(f"Updated references in {py_file}")
        except Exception as e:
            logging.error(f"Error updating references in {py_file}: {e}")

def main():
    """Main function."""
    logging.info("Starting remaining database migration")
    
    # Find remaining databases
    remaining_dbs = find_remaining_databases()
    
    if not remaining_dbs:
        logging.info("No remaining databases found")
        return
    
    logging.info(f"Found {len(remaining_dbs)} remaining databases to migrate")
    
    # Move databases and update references
    for source_path, target_path in remaining_dbs:
        db_name = os.path.basename(source_path)
        logging.info(f"Processing {db_name}")
        
        # Move database
        if move_database(source_path, target_path):
            logging.info(f"Successfully moved {db_name} to /db")
        
        # Update references in code
        update_references(source_path, db_name)
    
    logging.info("Completed remaining database migration")

if __name__ == "__main__":
    main() 