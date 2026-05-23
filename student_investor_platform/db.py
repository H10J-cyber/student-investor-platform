import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / 'data' / 'platform.db'
DB_PATH.parent.mkdir(exist_ok=True)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY,
            name TEXT,
            holdings TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_portfolio(name, holdings):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('INSERT INTO portfolios (name, holdings) VALUES (?, ?)', (name, json.dumps(holdings)))
    conn.commit()
    conn.close()

def list_portfolios():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT id, name, holdings FROM portfolios')
    rows = cur.fetchall()
    conn.close()
    return [(r[0], r[1], json.loads(r[2])) for r in rows]

init_db()
