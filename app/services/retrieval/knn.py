from __future__ import annotations

import numpy as np

from app.services.retrieval.base import BaseRetriever


class KNNRetriever(BaseRetriever):
    @property
    def strategy_name(self) -> str:
        return "knn"

    def retrieve(
        self,
        query_vector: list[float],
        rows: list[dict],
        k: int,
        distance_metric: str = "cosine",
    ) -> list[dict]:
        if not rows:
            return []
        if k <= 0:
            return []

        query = np.asarray(query_vector, dtype=float)
        if distance_metric == "cosine":
            norm = np.linalg.norm(query)
            if norm > 0:
                query = query / norm
        scored: list[dict] = []

        if distance_metric == "cosine":
            for row in rows:
                vector = np.asarray(row["normalised_vector"], dtype=float)
                score = float(np.dot(query, vector))
                scored.append({**row, "similarity_score": score})
        elif distance_metric == "dot_product":
            for row in rows:
                vector = np.asarray(row["embedding_vector"], dtype=float)
                score = float(np.dot(query, vector))
                scored.append({**row, "similarity_score": score})
        else:
            raise ValueError(f"Unsupported distance metric: {distance_metric}")

        scored.sort(key=lambda item: item["similarity_score"], reverse=True)
        return scored[:k]
