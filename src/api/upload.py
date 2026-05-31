from pathlib import Path

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, File, UploadFile

from src.rag.chunker import chunk_text
from src.services.pdf_service import extract_text_from_pdf
from src.rag.embeddings import create_embeddings
from src.rag.vector_store import store_chunks
from src.rag.bm25_retriever import build_bm25_index
from src.rag.vector_store import document_exists
from src.rag.vector_store import get_all_chunks

router = APIRouter()

RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

def create_document_id(filename: str) -> str:
    return (
        filename.lower()
        .replace(".pdf", "")
        .replace(" ", "_")
        .replace("-", "_")
    )

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)) -> dict:

    if not file.filename.lower().endswith(".pdf"):
        return {
            "error": "Only PDF files are allowed"
        }

    document_id = create_document_id(file.filename)
    if document_exists(document_id):
        return {
            "message": "Document already exists. Upload skipped.",
            "document_id": document_id,
            "filename": file.filename
        }
        
    file_path = RAW_DATA_DIR / file.filename

    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    extracted_text = extract_text_from_pdf(str(file_path))

    chunks = chunk_text(extracted_text)
    build_bm25_index(chunks)

    embeddings = create_embeddings(chunks)
    stored_chunks = store_chunks(
        chunks=chunks,
        embeddings=embeddings,
        filename=file.filename,
        document_id=document_id
    )

    build_bm25_index(get_all_chunks())
    build_bm25_index(chunks)

    return {
    "message": "PDF uploaded, text extracted, chunked, and embedded successfully",
    "document_id": document_id,
    "filename": file.filename,
    "saved_to": str(file_path),
    "characters_extracted": len(extracted_text),
    "chunks_created": len(chunks),
    "embeddings_created": len(embeddings),
    "embedding_dimension": len(embeddings[0]) if embeddings else 0,
    "first_chunk_preview": chunks[0][:500] if chunks else ""
}