# pyrefly: ignore [missing-import]
from fastapi import APIRouter
# pyrefly: ignore [missing-import]
from pydantic import BaseModel

from src.rag.embeddings import create_embedding
from src.rag.generator import generate_answer
from src.rag.vector_store import search_similar_chunks
from src.services.chat_history_service import (
    add_message,
    get_chat_history,
    clear_chat_history
)
from src.rag.bm25_retriever import search_bm25
router = APIRouter()


class AskRequest(BaseModel):
    question: str

@router.post("/ask-vector")
def ask_question(request: AskRequest) -> dict:
    history = get_chat_history(limit=10)

    query_embedding = create_embedding(request.question)

    results = search_similar_chunks(
        query_embedding=query_embedding,
        top_k=5
    )
    
    bm25_results = search_bm25(
        query=request.question,
        top_k=5
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    answer = generate_answer(
        question=request.question,
        context_chunks=documents,
        chat_history=history
    )

    add_message("user", request.question)
    add_message("assistant", answer)

    sources = []

    for metadata, distance in zip(metadatas, distances):
        sources.append(
            {
                "filename": metadata.get("filename"),
                "chunk_index": metadata.get("chunk_index"),
                "distance": distance
            }
        )

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources,
        "bm25_results": bm25_results,
        "chat_history": get_chat_history(limit=10)
    }


@router.get("/chat-history")
def read_chat_history() -> dict:
    return {
        "chat_history": get_chat_history(limit=20)
    }


@router.delete("/chat-history")
def delete_chat_history() -> dict:
    clear_chat_history()

    return {
        "message": "Chat history cleared successfully"
    }