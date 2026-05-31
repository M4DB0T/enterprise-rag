"""FastAPI entrypoint for Enterprise RAG."""

from pathlib import Path

# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles
from src.api.upload import router as upload_router
from src.api.ask import router as ask_router
from src.api.ask_hybrid import router as ask_hybrid_router
from src.rag.bm25_retriever import rebuild_bm25_from_chroma
from src.api.documents import router as documents_router
from src.services.database import initialize_database
from src.api.feedback import router as feedback_router
from src.api.logs import router as logs_router
from src.api.evaluation import router as evaluation_router


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


app = FastAPI(title="Enterprise RAG")
app.include_router(upload_router)
app.include_router(ask_router)
app.include_router(ask_hybrid_router)
app.include_router(documents_router)
app.include_router(feedback_router)
app.include_router(logs_router)
app.include_router(evaluation_router)
app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)



@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "enterprise-rag"}

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/api/home")
def api_home():
    return {
        "message": "Welcome to Enterprise RAG"
    }

@app.on_event("startup")
def startup_event():
    initialize_database()

    chunks_loaded = rebuild_bm25_from_chroma()

    print(f"BM25 index rebuilt with {chunks_loaded} chunks")
