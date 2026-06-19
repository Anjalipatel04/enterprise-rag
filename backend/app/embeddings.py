from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from .config import get_settings


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(get_settings().embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    vectors = model.encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
    return np.asarray(vectors, dtype=np.float32).tolist()


def embedding_dimension() -> int:
    model = get_embedding_model()
    return int(model.get_sentence_embedding_dimension())
