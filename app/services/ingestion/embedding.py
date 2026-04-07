from __future__ import annotations

from openai import OpenAI

from app.config import settings


class EmbeddingError(Exception):
    pass


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not settings.OPENAI_API_KEY:
        raise EmbeddingError("OPENAI_API_KEY가 설정되어 있지 않습니다.")
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    vectors: list[list[float]] = []
    batch_size = 64
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=batch,
        )
        for item in sorted(resp.data, key=lambda x: x.index):
            vectors.append(list(item.embedding))
    return vectors
