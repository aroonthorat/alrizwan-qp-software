import os
import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DB_DIR / "qp.sqlite"

def get_db_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id TEXT PRIMARY KEY,
        class TEXT,
        subject TEXT,
        chapter TEXT,
        section TEXT,
        lang TEXT DEFAULT 'en',
        type TEXT NOT NULL,
        sub_type TEXT,
        marks REAL NOT NULL,
        text TEXT NOT NULL,
        options_json TEXT,
        answer_json TEXT,
        diagram_id TEXT,
        needs_source INTEGER DEFAULT 0,
        difficulty TEXT DEFAULT 'medium',
        grammar_checked INTEGER DEFAULT 0,
        created_by TEXT,
        created_on TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS diagrams (
        id TEXT PRIMARY KEY,
        class TEXT,
        subject TEXT,
        chapter TEXT,
        tags TEXT,
        file_path TEXT,
        labels_json TEXT,
        kind TEXT DEFAULT 'figure'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS papers (
        id TEXT PRIMARY KEY,
        school TEXT,
        class TEXT,
        subject TEXT,
        exam_name TEXT,
        month_year TEXT,
        marks INTEGER,
        time TEXT,
        template TEXT,
        created_by TEXT,
        created_on TEXT,
        docx_path TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS paper_items (
        paper_id TEXT,
        question_id TEXT,
        q_group TEXT,
        order_no INTEGER,
        PRIMARY KEY (paper_id, question_id, order_no)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id TEXT,
        paper_id TEXT,
        exam_name TEXT,
        date TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS dictionary (
        lang TEXT,
        word TEXT,
        PRIMARY KEY (lang, word)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        role TEXT,
        subjects TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ai_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        task TEXT,
        model TEXT,
        tokens_in INTEGER,
        tokens_out INTEGER,
        cost_inr REAL,
        cache_hit INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ai_cache (
        hash TEXT PRIMARY KEY,
        task TEXT,
        response_json TEXT
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)
