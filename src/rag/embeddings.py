# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def create_embedding(text: str) -> list[float]:
    """
    Convert one text into one embedding vector.
    """

    embedding = get_embedding_model().encode(text)

    return embedding.tolist()


def create_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Convert many text chunks into embedding vectors.
    """

    embeddings = get_embedding_model().encode(texts)

    return embeddings.tolist()
