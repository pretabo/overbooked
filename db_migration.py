#!/usr/bin/env python3
"""
Database Migration Script for Overbooked

This script consolidates database files from multiple locations into a single
location (/db) to avoid confusion and data inconsistency.

Tasks:
1. Compare database files between /data/db and /db
2. Merge or copy newer files to /db
3. Update references in the codebase
4. Create a centralized db_path function
"""

import os
import shutil
import sqlite3
import datetime
import logging
import glob
import re
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("db_migration.log"),
        logging.StreamHandler()
    ]
)

def get_project_root():
    """Get the absolute path to the project root directory."""
    # Assuming this script is in the project root
    return os.path.dirname(os.path.abspath(__file__))

def get_db_paths():
    """Get absolute paths to the database directories."""
    root = get_project_root()
    return {
        "db": os.path.join(root, "db"),
        "data_db": os.path.join(root, "data", "db"),
        "src_db": os.path.join(root, "src", "db")
    }

def ensure_directory_exists(dir_path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logging.info(f"Created directory: {dir_path}")

def get_db_file_info(file_path):
    """Get information about a database file."""
    if not os.path.exists(file_path):
        return None
    
    stats = os.stat(file_path)
    modified_time = datetime.datetime.fromtimestamp(stats.st_mtime)
    size = stats.st_size
    
    # Check if it's a valid SQLite database
    is_valid = False
    try:
        conn = sqlite3.connect(file_path)
        conn.execute("SELECT 1")
        is_valid = True
        conn.close()
    except sqlite3.Error:
        pass
    
    return {
        "path": file_path,
        "modified": modified_time,
        "size": size,
        "is_valid": is_valid
    }

def compare_db_files():
    """Compare database files between /data/db and /db directories."""
    db_paths = get_db_paths()
    ensure_directory_exists(db_paths["db"])
    
    # Get all .db files from both directories
    data_db_files = glob.glob(os.path.join(db_paths["data_db"], "*.db"))
    db_files = glob.glob(os.path.join(db_paths["db"], "*.db"))
    
    all_db_names = set()
    for file_path in data_db_files + db_files:
        all_db_names.add(os.path.basename(file_path))
    
    comparison = {}
    for db_name in all_db_names:
        data_db_path = os.path.join(db_paths["data_db"], db_name)
        db_path = os.path.join(db_paths["db"], db_name)
        
        data_db_info = get_db_file_info(data_db_path)
        db_info = get_db_file_info(db_path)
        
        comparison[db_name] = {
            "data_db": data_db_info,
            "db": db_info
        }
    
    return comparison

def get_migration_plan(comparison):
    """Determine which files to migrate and how."""
    migration_plan = []
    
    for db_name, info in comparison.items():
        data_db_info = info["data_db"]
        db_info = info["db"]
        
        # Skip if file doesn't exist in /data/db
        if data_db_info is None:
            continue
            
        # If file doesn't exist in /db, copy it
        if db_info is None:
            migration_plan.append({
                "db_name": db_name,
                "action": "copy",
                "source": "data_db",
                "reason": "Missing in /db"
            })
        # If file in /data/db is newer, copy it
        elif data_db_info["modified"] > db_info["modified"]:
            migration_plan.append({
                "db_name": db_name,
                "action": "copy",
                "source": "data_db",
                "reason": f"Newer in /data/db ({data_db_info['modified']} vs {db_info['modified']})"
            })
        # If file in /data/db has more data (bigger size), merge them
        elif data_db_info["size"] > db_info["size"] and data_db_info["is_valid"] and db_info["is_valid"]:
            migration_plan.append({
                "db_name": db_name,
                "action": "merge",
                "source": "data_db",
                "reason": f"Larger in /data/db ({data_db_info['size']} vs {db_info['size']})"
            })
    
    return migration_plan

def execute_migration_plan(migration_plan):
    """Execute the migration plan."""
    db_paths = get_db_paths()
    
    for item in migration_plan:
        db_name = item["db_name"]
        action = item["action"]
        source = item["source"]
        reason = item["reason"]
        
        source_path = os.path.join(db_paths[source], db_name)
        target_path = os.path.join(db_paths["db"], db_name)
        
        logging.info(f"Migrating {db_name}: {action} - {reason}")
        
        if action == "copy":
            # Backup the target file if it exists
            if os.path.exists(target_path):
                backup_path = f"{target_path}.bak-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                shutil.copy2(target_path, backup_path)
                logging.info(f"  Backed up existing file to {backup_path}")
            
            # Copy the source file to the target
            shutil.copy2(source_path, target_path)
            logging.info(f"  Copied {source_path} to {target_path}")
        
        elif action == "merge":
            # This is a simplistic approach - for real merging, you'd need
            # to analyze schema and merge data carefully
            backup_path = f"{target_path}.bak-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.copy2(target_path, backup_path)
            logging.info(f"  Backed up existing file to {backup_path}")
            
            # For now, just copy the larger file
            shutil.copy2(source_path, target_path)
            logging.info(f"  Copied {source_path} to {target_path} (merge not implemented)")
    
    logging.info("Migration complete")

def update_db_path_function():
    """Create a centralized db_path function in src/db/utils.py."""
    db_paths = get_db_paths()
    utils_path = os.path.join(db_paths["src_db"], "utils.py")
    
    utils_content = """import os
import logging

def db_path(db_name):
    \"\"\"
    Get the path to a database file.
    
    This function returns the path to the database file in the /db directory.
    
    Args:
        db_name: Name of the database file
        
    Returns:
        Full path to the database file
    \"\"\"
    # Get project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    # Path to the database file
    db_path = os.path.join(project_root, "db", db_name)
    
    return db_path
"""
    
    # Backup the existing file
    if os.path.exists(utils_path):
        backup_path = f"{utils_path}.bak-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(utils_path, backup_path)
        logging.info(f"Backed up existing utils.py to {backup_path}")
    
    # Write the new content
    with open(utils_path, 'w') as f:
        f.write(utils_content)
    
    logging.info(f"Updated db_path function in {utils_path}")

def find_db_path_references():
    """Find all references to db_path in the codebase."""
    root = get_project_root()
    references = []
    
    # Find all Python files
    for py_file in glob.glob(os.path.join(root, "**", "*.py"), recursive=True):
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            try:
                content = f.read()
                
                # Check if file contains a db_path function or calls one
                if re.search(r'def\s+db_path\s*\(', content) or re.search(r'db_path\s*\(', content):
                    references.append(py_file)
            except Exception as e:
                logging.warning(f"Error reading {py_file}: {e}")
    
    return references

def create_symlink():
    """Create a symlink from /data/db to /db for backward compatibility."""
    db_paths = get_db_paths()
    
    # Remove /data/db if it exists
    if os.path.exists(db_paths["data_db"]):
        if os.path.islink(db_paths["data_db"]):
            os.remove(db_paths["data_db"])
        else:
            # Rename it to data/db.bak
            backup_path = f"{db_paths['data_db']}.bak-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            os.rename(db_paths["data_db"], backup_path)
            logging.info(f"Renamed {db_paths['data_db']} to {backup_path}")
    
    # Create parent directory if it doesn't exist
    data_dir = os.path.dirname(db_paths["data_db"])
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Create the symlink
    os.symlink(db_paths["db"], db_paths["data_db"])
    logging.info(f"Created symlink from {db_paths['data_db']} to {db_paths['db']}")

def main():
    """Main function to execute the migration."""
    logging.info("Starting database migration")
    
    # Step 1: Compare database files
    logging.info("Comparing database files")
    comparison = compare_db_files()
    
    # Step 2: Generate migration plan
    logging.info("Generating migration plan")
    migration_plan = get_migration_plan(comparison)
    
    # Log the migration plan
    for item in migration_plan:
        logging.info(f"Plan: {item['db_name']} - {item['action']} - {item['reason']}")
    
    # Step 3: Execute migration plan
    logging.info("Executing migration plan")
    execute_migration_plan(migration_plan)
    
    # Step 4: Update db_path function
    logging.info("Updating db_path function")
    update_db_path_function()
    
    # Step 5: Find all references to db_path
    logging.info("Finding references to db_path")
    references = find_db_path_references()
    logging.info(f"Found {len(references)} files with db_path references")
    for ref in references:
        logging.info(f"  {ref}")
    
    # Step 6: Create symlink for backward compatibility
    logging.info("Creating symlink for backward compatibility")
    create_symlink()
    
    logging.info("Migration completed successfully")
    logging.info("")
    logging.info("NEXT STEPS:")
    logging.info("1. Review the migration log file (db_migration.log)")
    logging.info("2. Test the application to ensure it works with the new database setup")
    logging.info("3. Review the files with db_path references and update them as needed")
    logging.info("4. Remove the symlink once all code is updated")

if __name__ == "__main__":
    main() 