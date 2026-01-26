import json
from datetime import datetime
from .db import get_conn

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

def update_template_admin(tid, name, data_dict):
    conn = get_conn()
    c = conn.cursor()
    data = json.dumps(data_dict)
    c.execute('UPDATE templates SET name = ?, data = ? WHERE id = ?', (name, data, tid))
    conn.commit()
    conn.close()

def delete_template(tid, user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM templates WHERE id = ? AND user_id = ?', (tid, user_id))
    conn.commit()
    conn.close()

def delete_template_admin(tid):
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM templates WHERE id = ?', (tid,))
    conn.commit()
    conn.close()
