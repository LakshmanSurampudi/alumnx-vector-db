from __future__ import annotations

from app.services.retrieval.knn import KNNRetriever


def get_retriever_registry() -> dict[str, KNNRetriever]:
    return {
        "knn": KNNRetriever(),
        "ann": KNNRetriever(),
    }

