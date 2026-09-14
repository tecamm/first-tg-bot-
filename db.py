import sqlite3

DB_NAME = 'orders.db'

def create_table():

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                username TEXT,
                name TEXT,
                wish TEXT,
                tz TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def add_order(telegram_id: int, username: str, name: str, wish: str, tz: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (telegram_id, username, name, wish, tz) 
            VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, username, name, wish, tz))
        conn.commit()