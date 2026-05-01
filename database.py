import sqlite3

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            user TEXT
        )
    """)
    
    # Add missing columns if they don't exist
    try:
        conn.execute("SELECT content FROM entries LIMIT 1")
    except:
        conn.execute("ALTER TABLE entries ADD COLUMN content TEXT")
    
    try:
        conn.execute("SELECT user FROM entries LIMIT 1")
    except:
        conn.execute("ALTER TABLE entries ADD COLUMN user TEXT")
    
    # Add id column if it doesn't exist
    try:
        conn.execute("SELECT id FROM entries LIMIT 1")
    except:
        # SQLite doesn't support adding PRIMARY KEY AUTOINCREMENT to existing table
        # So we need to recreate the table
        conn.execute("ALTER TABLE entries RENAME TO entries_old")
        conn.execute("""
            CREATE TABLE entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                user TEXT
            )
        """)
        # Copy data from old table to new table
        conn.execute("""
            INSERT INTO entries (title, content, user)
            SELECT title, content, user FROM entries_old
        """)
        conn.execute("DROP TABLE entries_old")
    
    conn.commit()
    conn.close()