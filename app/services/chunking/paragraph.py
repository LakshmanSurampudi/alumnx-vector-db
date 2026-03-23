from __future__ import annotations

import re

from app.config import get_config
from app.services.chunking.base import BaseChunker


def _sentence_split(text: str) -> list[str]:
    try:
        import nltk

        return [segment.strip() for segment in nltk.sent_tokenize(text, language="english") if segment.strip()]
    except Exception:
        parts = re.split(r"(?<=[.!?])\s+", text)
        return [segment.strip() for segment in parts if segment.strip()]


class ParagraphChunker(BaseChunker):
    @property
    def strategy_name(self) -> str:
        return "paragraph"

    def split(self, text: str) -> list[str]:
        cleaned = text.strip()
        if not cleaned:
            return []

        config = get_config()
        max_paragraph_size = config.max_paragraph_size

        candidates = [segment.strip() for segment in cleaned.split("\n\n") if segment.strip()]
        if len(candidates) < 2:
            candidates = [segment.strip() for segment in cleaned.split("\n") if segment.strip()]

        candidates = [segment for segment in candidates if len(segment) >= 10]
        chunks: list[str] = []
        for candidate in candidates:
            if len(candidate) <= max_paragraph_size:
                chunks.append(candidate)
                continue
            sentences = _sentence_split(candidate)
            if not sentences:
                chunks.append(candidate[:max_paragraph_size].strip())
                continue
            current = ""
            for sentence in sentences:
                candidate_chunk = f"{current} {sentence}".strip() if current else sentence
                if len(candidate_chunk) <= max_paragraph_size:
                    current = candidate_chunk
                else:
                    if current:
                        chunks.append(current)
                    current = sentence
            if current:
                chunks.append(current)
        return chunks

