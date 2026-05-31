from fastapi import APIRouter
from pydantic import BaseModel

from src.services.feedback_service import get_feedback, save_feedback

router = APIRouter()


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: str
    comment: str | None = None


@router.post("/feedback")
def create_feedback(request: FeedbackRequest) -> dict:
    save_feedback(
        question=request.question,
        answer=request.answer,
        rating=request.rating,
        comment=request.comment
    )

    return {
        "message": "Feedback saved successfully"
    }


@router.get("/feedback")
def read_feedback() -> dict:
    feedback_items = get_feedback(limit=20)

    return {
        "feedback": feedback_items,
        "count": len(feedback_items)
    }