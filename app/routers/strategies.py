from __future__ import annotations

from fastapi import APIRouter


router = APIRouter()


@router.get("/retrieval-strategies")
def list_retrieval_strategies() -> dict:
    return {
        "algorithms": [
            {
                "name": "knn",
                "description": "Exhaustive nearest-neighbour search over in-memory vectors.",
                "is_default": True,
            },
            {
                "name": "ann",
                "description": "Not supported in Phase 1. Requests using ann return HTTP 400.",
                "is_default": False,
            },
        ],
        "distance_metrics": [
            {
                "name": "cosine",
                "description": "Cosine similarity using normalised vectors.",
                "is_default": True,
            },
            {
                "name": "dot_product",
                "description": "Raw dot product over embedding vectors.",
                "is_default": False,
            },
        ],
    }

