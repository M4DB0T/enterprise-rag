"""FastAPI entrypoint for Enterprise RAG."""

# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from src.api.upload import router as upload_router
from src.api.ask import router as ask_router
from src.api.ask_hybrid import router as ask_hybrid_router
from src.rag.bm25_retriever import rebuild_bm25_from_chroma
from src.api.documents import router as documents_router
from src.services.database import initialize_database
from src.api.feedback import router as feedback_router
from src.api.logs import router as logs_router
from src.api.evaluation import router as evaluation_router



app = FastAPI(title="Enterprise RAG")
app.include_router(upload_router)
app.include_router(ask_router)
app.include_router(ask_hybrid_router)
app.include_router(documents_router)
app.include_router(feedback_router)
app.include_router(logs_router)
app.include_router(evaluation_router)



@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "enterprise-rag"}

@app.get("/")
def home():
    return {
        "message": "Welcome to Enterprise RAG"
    }

@app.on_event("startup")
def startup_event():
    initialize_database()

    chunks_loaded = rebuild_bm25_from_chroma()

    print(f"BM25 index rebuilt with {chunks_loaded} chunks")