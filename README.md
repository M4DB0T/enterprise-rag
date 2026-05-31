# Enterprise RAG

Enterprise RAG is a FastAPI-based retrieval augmented generation service for uploading PDF documents, indexing them with vector and keyword retrieval, and answering questions with source-aware responses.

## Key Features

- PDF upload and text extraction
- Recursive text chunking for long documents
- Sentence-transformer embeddings with persistent ChromaDB storage
- BM25 keyword retrieval and hybrid vector search
- Cross-encoder reranking for stronger answer context
- OpenAI-powered answer generation
- Chat history, feedback, request logs, and evaluation endpoints
- Docker and Docker Compose support

## Architecture Flow

```text
PDF upload
  -> text extraction
  -> chunking
  -> embeddings
  -> ChromaDB vector store
  -> vector/BM25 hybrid retrieval
  -> reranking
  -> OpenAI answer generation
  -> API response with sources
```

## Tech Stack

- Python, FastAPI, Uvicorn
- OpenAI API
- ChromaDB
- Sentence Transformers
- Rank BM25
- SQLite for local logs and chat history
- Docker and Docker Compose

## API Endpoints

- `GET /health` - service health check
- `POST /upload` - upload and index a PDF
- `POST /ask-vector` - answer using vector search
- `POST /ask-hybrid` - answer using hybrid retrieval and reranking
- `GET /documents` - list indexed documents
- `DELETE /documents/{document_id}` - remove a document from the index
- `GET /chat-history` - read recent chat history
- `DELETE /chat-history` - clear chat history
- `POST /feedback` - save user feedback
- `GET /feedback` - read saved feedback
- `GET /logs` - read RAG request logs
- `POST /evaluate-hybrid` - run a local evaluation dataset
- `POST /evaluate-hybrid-judge` - evaluate answers with an LLM judge
- `GET /evaluation-runs` - read recent evaluation runs

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Add your OpenAI API key to `.env`, then start the API:

```bash
uvicorn src.main:app --reload
```

Open `http://localhost:8000/docs` for the interactive API docs.

## Run With Docker

```bash
docker build -t enterprise-rag .
docker run --env-file .env -p 8000:8000 enterprise-rag
```

## Run With Docker Compose

```bash
docker compose up --build
```

Docker Compose reads `OPENAI_API_KEY` from your shell or local `.env` file.

## Example API Usage

Upload a PDF:

```bash
curl -X POST "http://localhost:8000/upload" ^
  -F "file=@sample.pdf"
```

Ask a question:

```bash
curl -X POST "http://localhost:8000/ask-hybrid" ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"What are the main points in this document?\"}"
```

## Folder Structure

```text
enterprise-rag/
  src/
    api/          FastAPI routers
    rag/          chunking, embeddings, retrieval, reranking, generation
    services/     database, logs, feedback, evaluation helpers
  data/
    evaluation/   sample evaluation data
    raw/          local uploads, ignored by git
  artifacts/      local ChromaDB and SQLite files, ignored by git
  tests/          test suite
  Dockerfile
  docker-compose.yml
```

## AI Engineering Highlights

- Designs an end-to-end RAG pipeline from ingestion to answer generation
- Combines semantic, keyword, and reranking retrieval strategies
- Separates API, retrieval, and service concerns for maintainability
- Uses local persistence while keeping generated data out of version control
- Includes evaluation and observability primitives for iterative RAG quality work

## Future Improvements

- Add authentication and role-based document access
- Add streaming responses
- Add async background ingestion jobs
- Expand automated tests for retrieval and API workflows
- Add deployment manifests for cloud hosting
