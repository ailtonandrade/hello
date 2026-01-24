import sqlite3
import os
import jwt
import random
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import timedelta
from pathlib import Path
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = Path(__file__).parent / 'app.db'

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# JWT configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'change-me-to-a-secure-secret')
JWT_ALGORITHM = 'HS256'
JWT_EXP_SECONDS = int(os.environ.get('JWT_EXP_SECONDS', 60*60*24))

def create_jwt(user_id):
    # Prefer PyJWT when available (provides standard JWT encoding).
    try:
        if hasattr(jwt, 'encode'):
            now = datetime.utcnow()
            payload = {
                'sub': user_id,
                'iat': int(now.timestamp()),
                'exp': int((now + timedelta(seconds=JWT_EXP_SECONDS)).timestamp())
            }
            return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    except Exception:
        pass
    # Fallback: use itsdangerous URLSafeTimedSerializer for signed tokens
    s = URLSafeTimedSerializer(JWT_SECRET)
    return s.dumps({'sub': user_id})

def verify_jwt(token):
    # Try PyJWT decode first if available
    try:
        if hasattr(jwt, 'decode'):
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
    except Exception:
        pass
    # Fallback: itsdangerous (uses max_age)
    try:
        s = URLSafeTimedSerializer(JWT_SECRET)
        data = s.loads(token, max_age=JWT_EXP_SECONDS)
        return data
    except (BadSignature, SignatureExpired):
        return None
    except Exception:
        return None

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
        credits INTEGER DEFAULT 0,
        created_at TEXT
    )
    ''')
    # ensure cpf is unique
    c.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_users_cpf ON users(cpf)')
    # ensure phone is unique
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
    CREATE TABLE IF NOT EXISTS prompt_keys (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        prompt_ollama TEXT,
        prompt_positive TEXT,
        prompt_negative TEXT,
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
    conn.close()

init_db()

def create_user(name, email, password, phone, cpf):
    conn = get_conn()
    c = conn.cursor()
    # check existing email, cpf or phone
    c.execute('SELECT id FROM users WHERE email = ?', (email,))
    if c.fetchone():
        conn.close()
        raise ValueError('Email já cadastrado')
    c.execute('SELECT id FROM users WHERE cpf = ?', (cpf,))
    if c.fetchone():
        conn.close()
        raise ValueError('CPF já cadastrado')
    c.execute('SELECT id FROM users WHERE phone = ?', (phone,))
    if c.fetchone():
        conn.close()
        raise ValueError('Telefone já cadastrado')

    hashed = generate_password_hash(password)
    now = datetime.utcnow().isoformat()
    try:
        c.execute('INSERT INTO users (name,email,password,phone,cpf,credits,created_at) VALUES (?,?,?,?,?,?,?)',
                  (name, email, hashed, phone, cpf, 0, now))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError as e:
        msg = str(e).lower()
        if 'email' in msg:
            raise ValueError('Email já cadastrado')
        if 'cpf' in msg:
            raise ValueError('CPF já cadastrado')
        if 'phone' in msg or 'unique' in msg:
            raise ValueError('Telefone já cadastrado')
        raise
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    if check_password_hash(row['password'], password):
        return dict(row)
    return None

def get_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def add_credits(user_id, amount, action='purchase'):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE users SET credits = credits + ? WHERE id = ?', (amount, user_id))
    now = datetime.utcnow().isoformat()
    c.execute('INSERT INTO history (user_id, action, credits_change, file_path, created_at) VALUES (?,?,?,?,?)',
              (user_id, action, amount, None, now))
    conn.commit()
    hid = c.lastrowid
    conn.close()
    return hid

def consume_credits(user_id, amount, action='generation'):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT credits FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    if not row or row['credits'] < amount:
        conn.close()
        return None
    c.execute('UPDATE users SET credits = credits - ? WHERE id = ?', (amount, user_id))
    now = datetime.utcnow().isoformat()
    c.execute('INSERT INTO history (user_id, action, credits_change, file_path, created_at) VALUES (?,?,?,?,?)',
              (user_id, action, -amount, None, now))
    conn.commit()
    hid = c.lastrowid
    conn.close()
    return hid

def update_history_file(history_id, file_path):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE history SET file_path = ? WHERE id = ?', (str(file_path), history_id))
    conn.commit()
    conn.close()

def get_history_for_user(user_id, limit=50):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?', (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_credits(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT credits FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row['credits'] if row else 0


def create_password_reset_for_email(email, expire_minutes=15):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE email = ?', (email,))
    row = c.fetchone()
    if not row:
        conn.close()
        raise ValueError('Email não encontrado')
    user_id = row['id']
    # generate 5-digit token
    token = f"{random.randint(0,99999):05d}"
    now = datetime.utcnow()
    expires_at = (now + timedelta(minutes=expire_minutes)).isoformat()
    created_at = now.isoformat()
    c.execute('INSERT INTO password_resets (user_id, token, expires_at, used, created_at) VALUES (?,?,?,?,?)',
              (user_id, token, expires_at, 0, created_at))
    conn.commit()
    conn.close()
    return token


def verify_and_consume_password_reset(email, token):
    # returns user_id if token valid and marks it used, otherwise None
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE email = ?', (email,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    user_id = row['id']
    now = datetime.utcnow().isoformat()
    c.execute('SELECT id, expires_at, used FROM password_resets WHERE user_id = ? AND token = ? ORDER BY id DESC LIMIT 1', (user_id, token))
    pr = c.fetchone()
    if not pr:
        conn.close()
        return None
    if pr['used']:
        conn.close()
        return None
    try:
        exp = pr['expires_at']
        if datetime.fromisoformat(exp) < datetime.utcnow():
            conn.close()
            return None
    except Exception:
        conn.close()
        return None
    # mark used
    c.execute('UPDATE password_resets SET used = 1 WHERE id = ?', (pr['id'],))
    conn.commit()
    conn.close()
    return user_id


def set_password(user_id, new_password):
    conn = get_conn()
    c = conn.cursor()
    hashed = generate_password_hash(new_password)
    c.execute('UPDATE users SET password = ? WHERE id = ?', (hashed, user_id))
    conn.commit()
    conn.close()


import json

def create_prompt_key(user_id, name, prompt_ollama=None, prompt_positive=None, prompt_negative=None):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute('INSERT INTO prompt_keys (user_id, name, prompt_ollama, prompt_positive, prompt_negative, created_at) VALUES (?,?,?,?,?,?)',
              (user_id, name, prompt_ollama, prompt_positive, prompt_negative, now))
    conn.commit()
    pkid = c.lastrowid
    conn.close()
    return pkid

def get_prompt_keys_for_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM prompt_keys WHERE user_id = ? ORDER BY id DESC', (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_prompt_key(pk_id, user_id=None):
    conn = get_conn()
    c = conn.cursor()
    if user_id:
        c.execute('SELECT * FROM prompt_keys WHERE id = ? AND user_id = ?', (pk_id, user_id))
    else:
        c.execute('SELECT * FROM prompt_keys WHERE id = ?', (pk_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_prompt_key(pk_id, user_id, name, prompt_ollama, prompt_positive, prompt_negative):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE prompt_keys SET name = ?, prompt_ollama = ?, prompt_positive = ?, prompt_negative = ? WHERE id = ? AND user_id = ?',
              (name, prompt_ollama, prompt_positive, prompt_negative, pk_id, user_id))
    conn.commit()
    conn.close()

def delete_prompt_key(pk_id, user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM prompt_keys WHERE id = ? AND user_id = ?', (pk_id, user_id))
    conn.commit()
    conn.close()

def create_template(user_id, name, data_dict):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    data = json.dumps(data_dict)
    c.execute('INSERT INTO templates (user_id, name, data, created_at) VALUES (?,?,?,?)', (user_id, name, data, now))
    conn.commit()
    tid = c.lastrowid
    conn.close()
    return tid

def get_templates_for_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM templates WHERE user_id = ? ORDER BY id DESC', (user_id,))
    rows = c.fetchall()
    conn.close()
    res = []
    for r in rows:
        d = dict(r)
        try:
            d['data'] = json.loads(d['data']) if d.get('data') else {}
        except Exception:
            d['data'] = {}
        res.append(d)
    return res

def get_template(tid, user_id=None):
    conn = get_conn()
    c = conn.cursor()
    if user_id:
        c.execute('SELECT * FROM templates WHERE id = ? AND user_id = ?', (tid, user_id))
    else:
        c.execute('SELECT * FROM templates WHERE id = ?', (tid,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    try:
        d['data'] = json.loads(d['data']) if d.get('data') else {}
    except Exception:
        d['data'] = {}
    return d

def update_template(tid, user_id, name, data_dict):
    conn = get_conn()
    c = conn.cursor()
    data = json.dumps(data_dict)
    c.execute('UPDATE templates SET name = ?, data = ? WHERE id = ? AND user_id = ?', (name, data, tid, user_id))
    conn.commit()
    conn.close()

def delete_template(tid, user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM templates WHERE id = ? AND user_id = ?', (tid, user_id))
    conn.commit()
    conn.close()
