-- Cloudflare D1 Database Schema for Al-Rizwan Question Paper Software
-- Specs: specs/SOFTWARE-PLAN.md §5 and specs/STORAGE-AND-RAG.md §1

CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    class TEXT NOT NULL,
    subject TEXT NOT NULL,
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
    archived INTEGER DEFAULT 0,
    created_by TEXT,
    created_on TEXT
);

CREATE TABLE IF NOT EXISTS diagrams (
    id TEXT PRIMARY KEY,
    class TEXT,
    subject TEXT,
    chapter TEXT,
    tags TEXT,
    file_path TEXT,
    labels_json TEXT,
    kind TEXT DEFAULT 'figure'
);

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
);

CREATE TABLE IF NOT EXISTS paper_items (
    paper_id TEXT,
    question_id TEXT,
    q_group TEXT,
    order_no INTEGER,
    PRIMARY KEY (paper_id, question_id, order_no)
);

CREATE TABLE IF NOT EXISTS usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT,
    paper_id TEXT,
    exam_name TEXT,
    date TEXT
);

CREATE TABLE IF NOT EXISTS dictionary (
    lang TEXT,
    word TEXT,
    PRIMARY KEY (lang, word)
);

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    role TEXT CHECK(role IN ('admin', 'teacher', 'checker')),
    subjects TEXT,
    token TEXT
);

CREATE TABLE IF NOT EXISTS ai_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT,
    task TEXT,
    model TEXT,
    tokens_in INTEGER,
    tokens_out INTEGER,
    cost_inr REAL,
    cache_hit INTEGER
);

CREATE TABLE IF NOT EXISTS ai_cache (
    hash TEXT PRIMARY KEY,
    task TEXT,
    response_json TEXT
);
