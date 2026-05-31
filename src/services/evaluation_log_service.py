import json

from src.services.database import get_connection


def save_evaluation_run(
    evaluation_method: str,
    accuracy: float,
    average_score: float,
    correct: int,
    total: int,
    results: list[dict]
) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO evaluation_runs (
            evaluation_method,
            accuracy,
            average_score,
            correct,
            total,
            results_json
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            evaluation_method,
            accuracy,
            average_score,
            correct,
            total,
            json.dumps(results)
        )
    )

    conn.commit()
    conn.close()


def get_evaluation_runs(limit: int = 10) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT evaluation_method, accuracy, average_score, correct, total, results_json, created_at
        FROM evaluation_runs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "evaluation_method": row[0],
            "accuracy": row[1],
            "average_score": row[2],
            "correct": row[3],
            "total": row[4],
            "results": json.loads(row[5]),
            "created_at": row[6]
        }
        for row in rows
    ]