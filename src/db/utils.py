import os

def db_path(db_filename):
    """Return the full path to a database file."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base_dir, "data", "db", db_filename) 