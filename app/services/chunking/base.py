from __future__ import annotations

from abc import ABC, abstractmethod


class BaseChunker(ABC):
    def __init__(self, chunk_size: int, overlap_size: int) -> None:
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size

    @abstractmethod
    def split(self, text: str) -> list[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        raise NotImplementedError

