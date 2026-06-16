import sqlite3
import os
from config import Config

def get_db_connection():
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(Config.DATABASE, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database using the schema.sql file if database tables do not exist."""
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(Config.DATABASE), exist_ok=True)
    
    conn = get_db_connection()
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()
