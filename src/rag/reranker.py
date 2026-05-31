from sentence_transformers import CrossEncoder


RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_reranker: CrossEncoder | None = None


def get_reranker() -> CrossEncoder:
    global _reranker

    if _reranker is None:
        _reranker = CrossEncoder(RERANKER_MODEL_NAME)

    return _reranker


def rerank_chunks(
    question: str,
    retrieved_results: list[dict],
    top_k: int = 5
) -> list[dict]:
    if not retrieved_results:
        return []

    pairs = [
        [question, result["text"]]
        for result in retrieved_results
    ]

    scores = get_reranker().predict(pairs)

    reranked_results = []

    for result, score in zip(retrieved_results, scores):
        result["reranker_score"] = float(score)
        reranked_results.append(result)

    reranked_results = sorted(
        reranked_results,
        key=lambda result: result["reranker_score"],
        reverse=True
    )

    return reranked_results[:top_k]
