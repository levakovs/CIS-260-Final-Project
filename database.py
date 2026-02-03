import sqlite3

DB_NAME = "inventory.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS laptops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_tag TEXT UNIQUE NOT NULL,
            serial_number TEXT UNIQUE NOT NULL,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT
        );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("database created/updated successfully")
