import sqlite3

DB_NAME = 'orders.db'
DB_BANNED_USERS = 'banned_users.db'

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
    with sqlite3.connect(DB_BANNED_USERS) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS banned_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                username TEXT,
                banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def add_order(telegram_id: int, username: str, name: str, wish: str, tz: str, status: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (telegram_id, username, name, wish, tz, status) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (telegram_id, username, name, wish, tz,status))
        conn.commit()


def pop_order(order_id: int, telegram_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM orders WHERE id = ? AND telegram_id = ?', (order_id,telegram_id))
        conn.commit()
        return cursor.rowcount > 0

def user_get_order_id(telegram_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, wish, tz FROM orders WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchall()

def ban_user_id(telegram_id: int):
    with sqlite3.connect(DB_BANNED_USERS) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO banned_users(telegram_id)"
                       "VALUES (?)", (telegram_id,))
        conn.commit()

def check_on_ban(telegram_id:int):
    with sqlite3.connect(DB_BANNED_USERS) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM banned_users WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchone()

def get_active_orders_count(telegram_id: int) -> int:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orders WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchone()[0]