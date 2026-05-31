from fastapi import APIRouter

from src.services.logging_service import get_rag_logs

router = APIRouter()


@router.get("/logs")
def read_logs() -> dict:
    logs = get_rag_logs(limit=20)

    return {
        "logs": logs,
        "count": len(logs)
    }