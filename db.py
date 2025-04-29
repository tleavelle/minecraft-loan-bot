# db.py
import sqlite3

DB_FILE = "loans.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Ensure required tables exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS linked_users (
        discord_id TEXT PRIMARY KEY,
        mc_ign TEXT UNIQUE
    )
    ''')

    conn.commit()
    conn.close()
