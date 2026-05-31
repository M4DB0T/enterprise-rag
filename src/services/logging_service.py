from src.services.database import get_connection
import json

def save_rag_log(
    request_id: str,
    question: str,
    answer: str,
    retrieval_method: str,
    model_name: str,
    latency_seconds: float,
    retrieved_sources: list
) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
    """
    INSERT INTO rag_logs (
        request_id,
        question,
        answer,
        retrieval_method,
        model_name,
        latency_seconds,
        retrieved_sources
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        request_id,
        question,
        answer,
        retrieval_method,
        model_name,
        latency_seconds,
        json.dumps(retrieved_sources)
    )
)

    conn.commit()
    conn.close()


def get_rag_logs(limit: int = 20) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT question, answer, retrieval_method, model_name, latency_seconds, created_at
        FROM rag_logs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "question": row[0],
            "answer": row[1],
            "retrieval_method": row[2],
            "model_name": row[3],
            "latency_seconds": row[4],
            "created_at": row[5]
        }
        for row in rows
    ]