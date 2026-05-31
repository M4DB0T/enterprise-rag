from src.services.database import get_connection


def save_feedback(
    question: str,
    answer: str,
    rating: str,
    comment: str | None = None
) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO feedback (question, answer, rating, comment)
        VALUES (?, ?, ?, ?)
        """,
        (question, answer, rating, comment)
    )

    conn.commit()
    conn.close()


def get_feedback(limit: int = 20) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT question, answer, rating, comment, created_at
        FROM feedback
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()

    feedback_items = [
        {
            "question": row[0],
            "answer": row[1],
            "rating": row[2],
            "comment": row[3],
            "created_at": row[4]
        }
        for row in rows
    ]

    return feedback_items