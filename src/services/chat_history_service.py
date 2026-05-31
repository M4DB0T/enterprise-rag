import sqlite3
from pathlib import Path


DB_PATH = Path("artifacts/chat_history.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def add_message(role: str, content: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chat_history (role, content)
        VALUES (?, ?)
        """,
        (role, content)
    )

    conn.commit()
    conn.close()


def get_chat_history(limit: int = 10) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT role, content, created_at
        FROM chat_history
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()

    conn.close()

    history = [
        {
            "role": row[0],
            "content": row[1],
            "timestamp": row[2]
        }
        for row in rows
    ]

    return list(reversed(history))


def clear_chat_history() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM chat_history")

    conn.commit()
    conn.close()