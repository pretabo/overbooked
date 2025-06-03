"""
Centralized Database Utilities for Overbooked

This module provides standardized utilities for database access across the application.
All code should use these utilities rather than hardcoding database paths or creating
custom db_path functions.
"""

import os
import sqlite3
import logging

def get_db_path(db_name):
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

def get_connection(db_name):
    """
    Get a connection to a database.
    
    Args:
        db_name: Name of the database file
        
    Returns:
        SQLite connection object
    """
    path = get_db_path(db_name)
    
    try:
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row  # Enable row factory for named columns
        return conn
    except sqlite3.Error as e:
        logging.error(f"Error connecting to database {db_name}: {e}")
        raise

def execute_query(db_name, query, params=None):
    """
    Execute a query on a database.
    
    Args:
        db_name: Name of the database file
        query: SQL query to execute
        params: Parameters for the query
        
    Returns:
        List of results
    """
    conn = get_connection(db_name)
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        conn.commit()
        return results
    except sqlite3.Error as e:
        logging.error(f"Error executing query on {db_name}: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def execute_update(db_name, query, params=None):
    """
    Execute an update on a database.
    
    Args:
        db_name: Name of the database file
        query: SQL query to execute
        params: Parameters for the query
        
    Returns:
        Number of rows affected
    """
    conn = get_connection(db_name)
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        affected_rows = cursor.rowcount
        conn.commit()
        return affected_rows
    except sqlite3.Error as e:
        logging.error(f"Error executing update on {db_name}: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def execute_script(db_name, script):
    """
    Execute a SQL script on a database.
    
    Args:
        db_name: Name of the database file
        script: SQL script to execute
        
    Returns:
        True if successful
    """
    conn = get_connection(db_name)
    
    try:
        conn.executescript(script)
        conn.commit()
        return True
    except sqlite3.Error as e:
        logging.error(f"Error executing script on {db_name}: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def table_exists(db_name, table_name):
    """
    Check if a table exists in a database.
    
    Args:
        db_name: Name of the database file
        table_name: Name of the table to check
        
    Returns:
        True if the table exists
    """
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
    result = execute_query(db_name, query, (table_name,))
    return len(result) > 0

def column_exists(db_name, table_name, column_name):
    """
    Check if a column exists in a table.
    
    Args:
        db_name: Name of the database file
        table_name: Name of the table to check
        column_name: Name of the column to check
        
    Returns:
        True if the column exists
    """
    query = f"PRAGMA table_info({table_name})"
    columns = execute_query(db_name, query)
    
    for column in columns:
        if column['name'] == column_name:
            return True
            
    return False

def create_database_if_not_exists(db_name):
    """
    Create a database if it doesn't exist.
    
    Args:
        db_name: Name of the database file
        
    Returns:
        True if successful
    """
    path = get_db_path(db_name)
    
    # If the database file doesn't exist, create it
    if not os.path.exists(path):
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Create an empty database file
            conn = sqlite3.connect(path)
            conn.close()
            
            logging.info(f"Created new database: {db_name}")
            return True
        except Exception as e:
            logging.error(f"Error creating database {db_name}: {e}")
            raise
    
    return True 