from fastapi import APIRouter

from src.rag.bm25_retriever import rebuild_bm25_from_chroma
from src.rag.vector_store import delete_document, list_documents

router = APIRouter()


@router.get("/documents")
def get_documents() -> dict:
    documents = list_documents()

    return {
        "documents": documents,
        "count": len(documents)
    }


@router.delete("/documents/{document_id}")
def remove_document(document_id: str) -> dict:
    deleted_chunks = delete_document(document_id)

    if deleted_chunks == 0:
        return {
            "message": "Document not found",
            "document_id": document_id,
            "deleted_chunks": 0
        }

    bm25_chunks_loaded = rebuild_bm25_from_chroma()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
        "deleted_chunks": deleted_chunks,
        "bm25_chunks_loaded": bm25_chunks_loaded
    }