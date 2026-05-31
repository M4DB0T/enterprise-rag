from fastapi import APIRouter
from pydantic import BaseModel
import time
from uuid import uuid4


from src.services.logging_service import save_rag_log
from src.rag.generator import generate_answer
from src.rag.hybrid_retriever import hybrid_search
from src.services.chat_history_service import (
    add_message,
    get_chat_history,
)
from src.rag.reranker import rerank_chunks

router = APIRouter()


class AskRequest(BaseModel):
    question: str


@router.post("/ask-hybrid")
def ask_hybrid(request: AskRequest) -> dict:
    start_time = time.time()
    request_id = str(uuid4())
    history = get_chat_history(limit=10)

    retrieved_results = hybrid_search(
        question=request.question,
        top_k=10
    )

    reranked_results = rerank_chunks(
        question=request.question,
        retrieved_results=retrieved_results,
        top_k=5
    )

    documents = [
        result["text"]
        for result in reranked_results
    ]

    sources = []

    for result in reranked_results:
        metadata = result.get("metadata") or {}

        sources.append(
            {
                "filename": metadata.get("filename"),
                "chunk_index": metadata.get("chunk_index"),
                "vector_distance": result.get("vector_distance"),
                "vector_score": result.get("vector_score"),
                "bm25_score": result.get("bm25_score"),
                "bm25_normalized_score": result.get("bm25_normalized_score"),
                "hybrid_score": result.get("hybrid_score"),
                "reranker_score": result.get("reranker_score"),
                "retrieval_source": result.get("source")
            }
        )

    answer = generate_answer(
        question=request.question,
        context_chunks=documents,
        chat_history=history
    )
    latency_seconds = time.time() - start_time

    save_rag_log(
        request_id=request_id,
        question=request.question,
        answer=answer,
        retrieval_method="hybrid",
        model_name="gpt-4.1-mini",
        latency_seconds=latency_seconds,
        retrieved_sources=sources
    )

    add_message("user", request.question)
    add_message("assistant", answer)

    return {
        "request_id": request_id,
        "question": request.question,
        "answer": answer,
        "sources": sources,
        "retrieval_method": "hybrid",
        "chat_history": get_chat_history(limit=10)
    }
