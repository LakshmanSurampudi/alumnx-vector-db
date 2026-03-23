from __future__ import annotations

from abc import ABC, abstractmethod


class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(
        self,
        query_vector: list[float],
        rows: list[dict],
        k: int,
        distance_metric: str = "cosine",
    ) -> list[dict]:
        raise NotImplementedError

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        raise NotImplementedError

