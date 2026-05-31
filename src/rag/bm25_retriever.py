from rank_bm25 import BM25Okapi
from src.rag.vector_store import get_all_chunks

bm25_index = None
bm25_chunks = []


def build_bm25_index(chunks: list[str]) -> None:
    global bm25_index, bm25_chunks

    bm25_chunks = chunks

    tokenized_chunks = [
        chunk.lower().split()
        for chunk in chunks
    ]

    bm25_index = BM25Okapi(tokenized_chunks)


def search_bm25(query: str, top_k: int = 5) -> list[dict]:
    if bm25_index is None:
        return []

    tokenized_query = query.lower().split()

    scores = bm25_index.get_scores(tokenized_query)

    ranked_results = sorted(
        enumerate(scores),
        key=lambda item: item[1],
        reverse=True
    )

    results = []

    for index, score in ranked_results[:top_k]:
        results.append(
            {
                "text": bm25_chunks[index],
                "score": float(score),
                "source": "bm25"
            }
        )

    return results

def rebuild_bm25_from_chroma() -> int:
    chunks = get_all_chunks()

    if not chunks:
        return 0

    build_bm25_index(chunks)

    return len(chunks)