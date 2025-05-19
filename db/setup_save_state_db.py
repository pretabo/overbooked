import sqlite3
import os

def db_path(db_name):
    return os.path.join("db", db_name)

def setup_save_state_db():
    conn = sqlite3.connect(db_path("save_state.db"))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS save_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("[Setup] save_state.db ready.")

if __name__ == "__main__":
    setup_save_state_db()
