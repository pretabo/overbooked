import os

def db_path(filename):
    # Get the absolute path to the db directory
    db_dir = os.path.dirname(os.path.abspath(__file__))
    # Join with the specified filename
    return os.path.join(db_dir, filename)
