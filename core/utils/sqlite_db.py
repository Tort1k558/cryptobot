import sqlite3
import logging
from dataclasses import dataclass

conn = sqlite3.connect("database/users.db")
cursor = conn.cursor()


@dataclass
class User:
    id: int
    username: str
    balance: float
    on_withdraw: float
    language: str
    currency: str
    min_deposit: float
    min_withdraw: float
    referrer: int
    verification: bool
    marketplace_status: bool
    marketplace_strategy: bool
    withdraw_status: bool
    blocked: bool

    @classmethod
    def get_user(cls, user_id):
        cursor.execute(
            f"SELECT username,balance,on_withdraw,language,currency,min_deposit,min_withdraw,referrer,verification, "
            f"marketplace_status, marketplace_strategy, withdraw_status, blocked FROM users WHERE id = {user_id}")
        user_info = cursor.fetchone()
        username = user_info[0]
        balance = user_info[1]
        on_withdraw = user_info[2]
        language = user_info[3]
        currency = user_info[4]
        min_deposit = user_info[5]
        min_withdraw = user_info[6]
        referrer = user_info[7]
        verification = user_info[8]
        marketplace_status = user_info[9]
        marketplace_strategy = user_info[10]
        withdraw_status = user_info[11]
        blocked = user_info[12]

        return cls(user_id, username, balance, on_withdraw, language, currency, min_deposit, min_withdraw, referrer,
                   verification,
                   marketplace_status, marketplace_strategy, withdraw_status,blocked)


def sql_start():
    if conn:
        logging.info("Data base connected")
    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        balance REAL DEFAULT 0.0,
        on_withdraw REAL DEFAULT 0.0,
        language TEXT,
        currency TEXT,
        min_deposit REAL,
        min_withdraw REAL,
        referrer INTEGER,
        verification BOOLEAN DEFAULT 0,
        marketplace_status BOOLEAN DEFAULT 0,
        marketplace_strategy TEXT DEFAULT "real",
        withdraw_status BOOLEAN DEFAULT 0,
        blocked BOOLEAN DEFAULT 0
    )
    """)

        cursor.execute("""CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER, 
        amount REAL,
        profit REAL, 
        asset TEXT, 
        duration int,
        made BOOLEAN
        )
        """)

        cursor.execute("""CREATE TABLE IF NOT EXISTS workers(
            id INTEGER PRIMARY KEY, 
            min_deposit REAL,
            min_withdraw REAL,
            default_language TEXT,
            default_currency TEXT
            )
        """)
        cursor.execute("""CREATE TABLE IF NOT EXISTS promocodes(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                code TEXT,
                id_creator INTEGER,
                balance REAL,
                uses INTEGER
                )
            """)

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_promo_usage (
                user_id INTEGER,
                promo_id INTEGER,
                PRIMARY KEY (user_id, promo_id)
            );
        ''')

        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS delete_unused_promocode
            AFTER UPDATE OF uses ON promocodes
            FOR EACH ROW
            WHEN NEW.uses = 0
            BEGIN
                DELETE FROM promocodes WHERE id = OLD.id;
                DELETE FROM user_promo_usage WHERE promo_id = OLD.id;
            END;
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS currencies (
                name TEXT PRIMARY KEY,
                requisites TEXT
            )
        ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS admins (
                        id INTEGER PRIMARY KEY
                    )
                ''')

        conn.commit()

    except Exception as e:
        logging.error(e)
