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
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT
        )
    """)
    
    # Add missing columns if they don't exist
    try:
        conn.execute("SELECT content FROM comments LIMIT 1")
    except:
        conn.execute("ALTER TABLE comments ADD COLUMN content TEXT")
    
    # Add id column if it doesn't exist
    try:
        conn.execute("SELECT id FROM comments LIMIT 1")
    except:
        # SQLite doesn't support adding PRIMARY KEY AUTOINCREMENT to existing table
        # So we need to recreate the table
        conn.execute("ALTER TABLE comments RENAME TO comments_old")
        conn.execute("""
            CREATE TABLE comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT
            )
        """)
        # Copy data from old table to new table (excluding user)
        conn.execute("""
            INSERT INTO comments (title, content)
            SELECT title, content FROM comments_old
        """)
        conn.execute("DROP TABLE comments_old")
    
    conn.commit()
    conn.close()