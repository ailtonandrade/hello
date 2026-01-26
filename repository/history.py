from .db import get_conn
from datetime import datetime

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

def log_history(user_id, action, credits_change=0, file_path=None):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute('INSERT INTO history (user_id, action, credits_change, file_path, created_at) VALUES (?,?,?,?,?)',
              (user_id, action, credits_change, file_path, now))
    conn.commit()
    hid = c.lastrowid
    conn.close()
    return hid
