import os
import logging

def db_path(db_name):
    """
    Get the path to a database file.
    
    This function returns the path to the database file in the /db directory.
    
    Args:
        db_name: Name of the database file
        
    Returns:
        Full path to the database file
    """
    # Get project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    # Path to the database file
    db_path = os.path.join(project_root, "db", db_name)
    
    return db_path
