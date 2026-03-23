from __future__ import annotations

from fastapi import APIRouter

from app.config import get_config


router = APIRouter()


@router.get("/chunking-strategies")
def list_chunking_strategies() -> dict:
    config = get_config()
    return {
        "strategies": [
            {
                "name": "fixed_length",
                "description": "Splits text into fixed-size chunks with overlap.",
                "parameters": ["chunk_size", "overlap_size"],
            },
            {
                "name": "paragraph",
                "description": "Splits text along paragraph boundaries.",
                "parameters": ["chunk_size"],
            },
        ]
    }

