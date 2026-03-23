from __future__ import annotations

from app.services.chunking.base import BaseChunker


class FixedLengthChunker(BaseChunker):
    @property
    def strategy_name(self) -> str:
        return "fixed_length"

    def split(self, text: str) -> list[str]:
        cleaned = text.strip()
        if not cleaned:
            return []
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.overlap_size < 0:
            raise ValueError("overlap_size must be non-negative")
        if self.overlap_size >= self.chunk_size:
            raise ValueError("overlap_size must be smaller than chunk_size")

        chunks: list[str] = []
        step = self.chunk_size - self.overlap_size
        for start in range(0, len(cleaned), step):
            chunk = cleaned[start : start + self.chunk_size].strip()
            if chunk:
                chunks.append(chunk)
        return chunks

