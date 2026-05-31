from fastapi import APIRouter
from pydantic import BaseModel



from src.services.evaluation_service import (
    evaluate_hybrid
)
from src.services.evaluation_service import judge_answer
from src.services.evaluation_service import (
    load_evaluation_dataset
)
from src.services.evaluation_service import evaluate_hybrid_with_judge
from src.services.evaluation_log_service import (
    get_evaluation_runs,
    save_evaluation_run,
)



class JudgeRequest(BaseModel):
    question: str
    expected_answer: str
    generated_answer: str


router = APIRouter()


@router.get("/evaluation-dataset")
def get_dataset():

    dataset = load_evaluation_dataset(
        "data/evaluation/cv_eval.json"
    )

    return {
        "questions": len(dataset),
        "dataset": dataset
    }

@router.post("/evaluate-hybrid")
def run_hybrid_evaluation():

    results = evaluate_hybrid(
        "data/evaluation/cv_eval.json"
    )

    return results

@router.post("/judge-answer")
def test_judge_answer(request: JudgeRequest) -> dict:
    judge_result = judge_answer(
        question=request.question,
        expected_answer=request.expected_answer,
        generated_answer=request.generated_answer
    )

    return {
        "judge_result": judge_result
    }


@router.post("/evaluate-hybrid-judge")
def run_hybrid_judge_evaluation() -> dict:
    results = evaluate_hybrid_with_judge(
        "data/evaluation/cv_eval.json"
    )

    save_evaluation_run(
        evaluation_method=results["evaluation_method"],
        accuracy=results["accuracy"],
        average_score=results["average_score"],
        correct=results["correct"],
        total=results["total"],
        results=results["results"]
    )

    return results

@router.get("/evaluation-runs")
def read_evaluation_runs() -> dict:
    runs = get_evaluation_runs(limit=10)

    return {
        "evaluation_runs": runs,
        "count": len(runs)
    }