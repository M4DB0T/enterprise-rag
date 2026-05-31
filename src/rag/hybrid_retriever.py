from src.rag.bm25_retriever import search_bm25
from src.rag.embeddings import create_embedding
from src.rag.vector_store import search_similar_chunks


def _vector_distance_to_score(distance: float | None) -> float:
    if distance is None:
        return 0.0

    return 1 / (1 + distance)


def _normalize_bm25_score(score: float, max_score: float) -> float:
    if max_score == 0:
        return 0.0

    return score / max_score


def hybrid_search(
    question: str,
    top_k: int = 5,
    vector_weight: float = 0.7,
    bm25_weight: float = 0.3
) -> list[dict]:
    query_embedding = create_embedding(question)

    vector_results = search_similar_chunks(
        query_embedding=query_embedding,
        top_k=top_k * 2
    )

    documents = vector_results.get("documents", [[]])[0]
    metadatas = vector_results.get("metadatas", [[]])[0]
    distances = vector_results.get("distances", [[]])[0]

    combined_results = {}

    for document, metadata, distance in zip(documents, metadatas, distances):
        vector_score = _vector_distance_to_score(distance)

        combined_results[document] = {
            "text": document,
            "metadata": metadata,
            "vector_distance": distance,
            "vector_score": vector_score,
            "bm25_score": 0.0,
            "bm25_normalized_score": 0.0,
            "hybrid_score": 0.0,
            "source": "vector"
        }

    bm25_results = search_bm25(
        query=question,
        top_k=top_k * 2
    )

    max_bm25_score = max(
        [result["score"] for result in bm25_results],
        default=0.0
    )

    for result in bm25_results:
        text = result["text"]
        bm25_score = result["score"]
        bm25_normalized_score = _normalize_bm25_score(
            score=bm25_score,
            max_score=max_bm25_score
        )

        if text in combined_results:
            combined_results[text]["bm25_score"] = bm25_score
            combined_results[text]["bm25_normalized_score"] = bm25_normalized_score
            combined_results[text]["source"] = "hybrid"
        else:
            combined_results[text] = {
                "text": text,
                "metadata": {},
                "vector_distance": None,
                "vector_score": 0.0,
                "bm25_score": bm25_score,
                "bm25_normalized_score": bm25_normalized_score,
                "hybrid_score": 0.0,
                "source": "bm25"
            }

    for result in combined_results.values():
        result["hybrid_score"] = (
            vector_weight * result["vector_score"]
            + bm25_weight * result["bm25_normalized_score"]
        )

    ranked_results = sorted(
        combined_results.values(),
        key=lambda result: result["hybrid_score"],
        reverse=True
    )

    return ranked_results[:top_k]