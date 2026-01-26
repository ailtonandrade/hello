import json
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import jwt
from .db import get_conn

JWT_SECRET = 'change-me-to-a-secure-secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_SECONDS = 60*60*24

def create_jwt(user_id):
    try:
        now = datetime.utcnow()
        payload = {
            'sub': user_id,
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(seconds=JWT_EXP_SECONDS)).timestamp())
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    except Exception:
        s = URLSafeTimedSerializer(JWT_SECRET)
        return s.dumps({'sub': user_id})

def verify_jwt(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        try:
            s = URLSafeTimedSerializer(JWT_SECRET)
            data = s.loads(token, max_age=JWT_EXP_SECONDS)
            return data
        except Exception:
            return None

def create_user(name, email, password, phone, cpf):
    conn = get_conn()
    c = conn.cursor()
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
        c.execute('INSERT INTO users (name,email,password,phone,cpf,is_admin,credits,created_at) VALUES (?,?,?,?,?,?,?,?)',
                  (name, email, hashed, phone, cpf, 0, 0, now))
        conn.commit()
        return c.lastrowid
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
    c.execute('SELECT credits, is_admin FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    if row['is_admin']:
        now = datetime.utcnow().isoformat()
        c.execute('INSERT INTO history (user_id, action, credits_change, file_path, created_at) VALUES (?,?,?,?,?)',
                  (user_id, action, 0, None, now))
        conn.commit()
        hid = c.lastrowid
        conn.close()
        return hid
    if row['credits'] < amount:
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

def get_credits(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT credits, is_admin FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return 0
    if row['is_admin']:
        return 999999999
    return row['credits']

def create_password_reset_for_email(email, expire_minutes=15):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE email = ?', (email,))
    row = c.fetchone()
    if not row:
        conn.close()
        raise ValueError('Email não encontrado')
    user_id = row['id']
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


# Billing / payments helpers
def get_credit_packages():
    conn = get_conn()
    c = conn.cursor()
    rows = c.execute('SELECT * FROM credit_packages ORDER BY id').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_credit_package(package_id):
    conn = get_conn()
    c = conn.cursor()
    row = c.execute('SELECT * FROM credit_packages WHERE id = ?', (package_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_payment(user_id, package_id, stripe_session_id, amount_cents, credits, status='pending', metadata=None):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    meta_json = json.dumps(metadata) if metadata is not None else None
    c.execute('INSERT INTO payments (user_id, package_id, stripe_session_id, amount_cents, credits, status, metadata, created_at) VALUES (?,?,?,?,?,?,?,?)',
              (user_id, package_id, stripe_session_id, amount_cents, credits, status, meta_json, now))
    conn.commit()
    pid = c.lastrowid
    conn.close()
    return pid


def update_payment_status_by_session(stripe_session_id, new_status, metadata=None):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    meta_json = json.dumps(metadata) if metadata is not None else None
    c.execute('SELECT * FROM payments WHERE stripe_session_id = ? ORDER BY id DESC LIMIT 1', (stripe_session_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    c.execute('UPDATE payments SET status = ?, metadata = ?, updated_at = ? WHERE id = ?', (new_status, meta_json, now, row['id']))
    conn.commit()
    # return updated record as dict
    c.execute('SELECT * FROM payments WHERE id = ?', (row['id'],))
    updated = c.fetchone()
    conn.close()
    return dict(updated) if updated else None


def get_payments_for_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    rows = c.execute('SELECT * FROM payments WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
