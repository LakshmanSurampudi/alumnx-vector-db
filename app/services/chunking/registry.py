from __future__ import annotations

from app.services.chunking.fixed_length import FixedLengthChunker
from app.services.chunking.paragraph import ParagraphChunker


def get_chunker_registry(chunk_size: int, overlap_size: int) -> dict[str, object]:
    return {
        "fixed_length": FixedLengthChunker(chunk_size, overlap_size),
        "paragraph": ParagraphChunker(chunk_size, overlap_size),
    }

