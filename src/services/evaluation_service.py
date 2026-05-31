import json
from pathlib import Path
from openai import OpenAI
import os
import json

from src.rag.generator import generate_answer
from src.rag.hybrid_retriever import hybrid_search


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def load_evaluation_dataset(
    file_path: str
) -> list[dict]:

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def simple_contains_score(
    expected_answer: str,
    generated_answer: str
) -> bool:

    return (
        expected_answer.lower()
        in generated_answer.lower()
    )

def evaluate_hybrid(dataset_path: str):
    dataset = load_evaluation_dataset(
        dataset_path
    )

    results = []

    correct = 0

    for item in dataset:

        question = item["question"]
        expected_answer = item["expected_answer"]

        retrieved_results = hybrid_search(
            question=question,
            top_k=5
        )

        documents = [
            result["text"]
            for result in retrieved_results
        ]

        generated_answer = generate_answer(
            question=question,
            context_chunks=documents
        )

        passed = simple_contains_score(
            expected_answer=expected_answer,
            generated_answer=generated_answer
        )

        if passed:
            correct += 1

        results.append(
            {
                "question": question,
                "expected_answer": expected_answer,
                "generated_answer": generated_answer,
                "passed": passed
            }
        )

    accuracy = (
        correct / len(dataset)
        if dataset
        else 0
    )

    return {
        "accuracy": accuracy,
        "correct": correct,
        "total": len(dataset),
        "results": results
    }

def judge_answer(
    question: str,
    expected_answer: str,
    generated_answer: str
) -> dict:

    prompt = f"""
You are evaluating a RAG system.

Question:
{question}

Expected Answer:
{expected_answer}

Generated Answer:
{generated_answer}

Determine if the generated answer is factually correct.

Return JSON only:

{{
    "correct": true,
    "score": 0.0-1.0,
    "reason": "short explanation"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    judge_text = response.choices[0].message.content

    try:
        return json.loads(judge_text)
    except json.JSONDecodeError:
        return {
            "correct": False,
            "score": 0.0,
            "reason": "Judge response was not valid JSON.",
            "raw_response": judge_text
        }


def evaluate_hybrid_with_judge(
    dataset_path: str
) -> dict:
    dataset = load_evaluation_dataset(dataset_path)

    results = []
    correct = 0
    total_score = 0.0

    for item in dataset:
        question = item["question"]
        expected_answer = item["expected_answer"]

        retrieved_results = hybrid_search(
            question=question,
            top_k=5
        )

        documents = [
            result["text"]
            for result in retrieved_results
        ]

        generated_answer = generate_answer(
            question=question,
            context_chunks=documents
        )

        judge_result = judge_answer(
            question=question,
            expected_answer=expected_answer,
            generated_answer=generated_answer
        )

        is_correct = judge_result.get("correct", False)
        score = judge_result.get("score", 0.0)

        if is_correct:
            correct += 1

        total_score += score

        results.append(
            {
                "question": question,
                "expected_answer": expected_answer,
                "generated_answer": generated_answer,
                "judge_result": judge_result,
                "retrieved_sources": [
                    {
                        "filename": result.get("metadata", {}).get("filename"),
                        "chunk_index": result.get("metadata", {}).get("chunk_index"),
                        "hybrid_score": result.get("hybrid_score"),
                        "reranker_score": result.get("reranker_score")
                    }
                    for result in retrieved_results
                ]
            }
        )

    accuracy = correct / len(dataset) if dataset else 0
    average_score = total_score / len(dataset) if dataset else 0

    return {
        "evaluation_method": "hybrid_rag_with_gpt_judge",
        "accuracy": accuracy,
        "average_score": average_score,
        "correct": correct,
        "total": len(dataset),
        "results": results
    }