from __future__ import annotations

from typing import Iterable

from app.config import get_config


class GeminiEmbedder:
    def __init__(self, model: str | None = None) -> None:
        self.config = get_config()
        self.model = model or self.config.embedding_model

    def _client(self):
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
        except ImportError as exc:
            raise RuntimeError("langchain-google-genai is required for embedding") from exc
        return GoogleGenerativeAIEmbeddings(model=self.model)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        client = self._client()
        vectors: list[list[float]] = []
        for start in range(0, len(texts), 100):
            batch = texts[start : start + 100]
            vectors.extend(
                client.embed_documents(
                    batch,
                    output_dimensionality=self.config.output_dimensionality,
                )
            )
        return vectors

    def embed_query(self, text: str) -> list[float]:
        client = self._client()
        return client.embed_query(
            text,
            output_dimensionality=self.config.output_dimensionality,
        )

