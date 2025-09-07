import sqlite3, time, uuid, streamlit as st

DB_PATH = "memory.db"

def init_db():
    
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT, role TEXT, content TEXT, ts REAL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE, plan_text TEXT,
        cal INTEGER, protein_g INTEGER, fat_g INTEGER, carbs_g INTEGER,
        age INTEGER, sex TEXT, height_cm INTEGER, weight_kg REAL,
        activity TEXT, goal TEXT, ts REAL)""")
    con.commit(); con.close()

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

def count_msgs(session_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM messages WHERE session_id=?", (session_id,))
    n = cur.fetchone()[0]; con.close()
    return n

def save_message(session_id, role, content):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO messages VALUES (NULL,?,?,?,?)",
                (session_id, role, content, time.time()))
    con.commit(); con.close()

def load_history(session_id, limit=50):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT role, content FROM messages WHERE session_id=? ORDER BY ts ASC LIMIT ?", 
                (session_id, limit))
    rows = cur.fetchall(); con.close()
    return rows

def save_plan(session_id, plan_dict):
    t = plan_dict["targets"]
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        INSERT INTO plans (session_id, plan_text, cal, protein_g, fat_g, carbs_g,
                           age, sex, height_cm, weight_kg, activity, goal, ts)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(session_id) DO UPDATE SET plan_text=excluded.plan_text
    """, (session_id, plan_dict["text"], t["cal"], t["p"], t["f"], t["c"],
          t["age"], t["sex"], t["h"], t["w"], t["level"], t["goal"], time.time()))
    con.commit(); con.close()

def load_latest_plan(session_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT plan_text FROM plans WHERE session_id=?", (session_id,))
    row = cur.fetchone(); con.close()
    return row
