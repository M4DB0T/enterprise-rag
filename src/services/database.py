import sqlite3
from pathlib import Path


DB_PATH = Path("artifacts/chat_history.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        rating TEXT NOT NULL,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rag_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        retrieval_method TEXT NOT NULL,
        model_name TEXT,
        latency_seconds REAL,
        retrieved_sources TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluation_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evaluation_method TEXT NOT NULL,
        accuracy REAL,
        average_score REAL,
        correct INTEGER,
        total INTEGER,
        results_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()