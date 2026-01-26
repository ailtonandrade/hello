import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent.parent / 'app.db'

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT NOT NULL,
        cpf TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        credits INTEGER DEFAULT 0,
        created_at TEXT
    )
    ''')
    try:
        cols = [r[1] for r in c.execute("PRAGMA table_info(users)").fetchall()]
        if 'is_admin' not in cols:
            c.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
    except Exception:
        pass
    c.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_users_cpf ON users(cpf)')
    c.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_users_phone ON users(phone)')
    c.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        action TEXT,
        credits_change INTEGER,
        file_path TEXT,
        created_at TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        data TEXT,
        created_at TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS credit_packages (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        credits INTEGER NOT NULL,
        price_cents INTEGER NOT NULL,
        created_at TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        package_id INTEGER,
        stripe_session_id TEXT,
        amount_cents INTEGER,
        credits INTEGER,
        status TEXT,
        metadata TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS password_resets (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        token TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        used INTEGER DEFAULT 0,
        created_at TEXT
    )
    ''')
    conn.commit()
    # ensure there are some default credit packages
    try:
        existing = c.execute('SELECT COUNT(1) as cnt FROM credit_packages').fetchone()['cnt']
        if existing == 0:
            now = datetime.utcnow().isoformat()
            packages = [
                ('1000 créditos', 1000, 1000),
                ('4000 créditos', 4000, 4000),
                ('9000 créditos', 9000, 9000),
            ]
            for name, credits, price_cents in packages:
                c.execute('INSERT INTO credit_packages (name, credits, price_cents, created_at) VALUES (?,?,?,?)',
                          (name, credits, price_cents, now))
            conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

# initialize on import
init_db()
