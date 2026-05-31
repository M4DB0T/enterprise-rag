from pathlib import Path
from uuid import uuid4

# pyrefly: ignore [missing-import]
import chromadb


CHROMA_DIR = Path("artifacts/chroma_db")
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_or_create_collection(
    name="enterprise_rag_documents"
)


def store_chunks(
    chunks: list[str],
    embeddings: list[list[float]],
    filename: str,
    document_id: str
) -> int:
    """
    Store text chunks and their embeddings in ChromaDB.
    """

    ids = [
        f"{document_id}_{index}"
        for index in range(len(chunks))
    ]

    metadatas = [
        {
            "document_id": document_id,
            "filename": filename,
            "chunk_index": index
        }
        for index in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)

def search_similar_chunks(
    query_embedding: list[float],
    top_k: int = 5
) -> dict:
    """
    Search ChromaDB for chunks most similar to the user's question.
    """

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results
def get_all_chunks() -> list[str]:
    results = collection.get()
    documents = results.get("documents", [])
    return documents

def document_exists(document_id: str) -> bool:
    results = collection.get(
        where={
            "document_id": document_id
        },
        limit=1
    )

    ids = results.get("ids", [])

    return len(ids) > 0

def list_documents() -> list[dict]:
    results = collection.get()

    metadatas = results.get("metadatas", [])

    documents = {}

    for metadata in metadatas:
        document_id = metadata.get("document_id")
        filename = metadata.get("filename")

        if document_id not in documents:
            documents[document_id] = {
                "document_id": document_id,
                "filename": filename,
                "chunk_count": 0
            }

        documents[document_id]["chunk_count"] += 1

    return list(documents.values())

def delete_document(document_id: str) -> int:
    results = collection.get(
        where={
            "document_id": document_id
        }
    )

    ids = results.get("ids", [])

    if not ids:
        return 0

    collection.delete(ids=ids)

    return len(ids)