from __future__ import annotations

import logging
from collections import defaultdict

import numpy as np

from app.config import get_config
from app.models import KBResult, ChunkResult, RetrieveRequest, RetrieveResponse, RetrievalStrategy, StrategyGroupResult
from app.services.embedding.embedder import GeminiEmbedder
from app.services.retrieval.registry import get_retriever_registry
from app.services.store.jsonl_store import JSONLStore


SUPPORTED_ALGORITHMS = {"knn"}
SUPPORTED_DISTANCE_METRICS = {"cosine", "dot_product"}
logger = logging.getLogger("nexvec.retrieval")


def _default_retrieval_strategy() -> RetrievalStrategy:
    config = get_config()
    return RetrievalStrategy(
        algorithm=config.default_retrieval_strategy.get("algorithm", "knn"),
        distance_metric=config.default_retrieval_strategy.get("distance_metric", "cosine"),
    )


def _validate_retrieval_strategy(strategy: RetrievalStrategy) -> RetrievalStrategy:
    if strategy.algorithm == "ann":
        raise ValueError("WARNING: Retrieval algorithm 'ann' is not supported in Phase 1.")
    if strategy.algorithm not in SUPPORTED_ALGORITHMS:
        raise ValueError(f"Unsupported retrieval algorithm: {strategy.algorithm}")
    if strategy.distance_metric not in SUPPORTED_DISTANCE_METRICS:
        raise ValueError(f"Unsupported distance metric: {strategy.distance_metric}")
    return strategy


def _normalize(vector: list[float]) -> list[float]:
    array = np.asarray(vector, dtype=float)
    norm = np.linalg.norm(array)
    if norm == 0:
        return [0.0 for _ in vector]
    return (array / norm).astype(float).tolist()


def _to_chunk_results(rows: list[dict]) -> list[ChunkResult]:
    return [
        ChunkResult(
            chunk_id=row["chunk_id"],
            similarity_score=row["similarity_score"],
            chunk_text=row["chunk_text"],
            embedding_vector=row["embedding_vector"],
            source_filename=row["source_filename"],
            chunk_index=row["chunk_index"],
            page_number=row.get("page_number"),
            created_at=row["created_at"],
        )
        for row in rows
    ]


def _run_group(rows: list[dict], query: str, k: int, strategy: RetrievalStrategy, model: str, chunking_strategy: str) -> StrategyGroupResult:
    embedder = GeminiEmbedder(model)
    logger.info(
        "Retrieving group chunking_strategy=%s model=%s row_count=%s k=%s metric=%s",
        chunking_strategy,
        model,
        len(rows),
        k,
        strategy.distance_metric,
    )
    query_vector = embedder.embed_query(query)
    if strategy.distance_metric == "cosine":
        query_vector = _normalize(query_vector)
        for row in rows:
            row["normalised_vector"] = row.get("normalised_vector") or _normalize(row["embedding_vector"])
    retriever = get_retriever_registry()["knn"]
    top_rows = retriever.retrieve(query_vector=query_vector, rows=rows, k=k, distance_metric=strategy.distance_metric)
    return StrategyGroupResult(
        chunking_strategy=chunking_strategy,
        embedding_model=model,
        chunks=_to_chunk_results(top_rows),
    )


def _group_rows(rows: list[dict], embedding_model: str | None) -> dict[tuple[str, str], list[dict]]:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if embedding_model and row.get("embedding_model") != embedding_model:
            continue
        groups[(row["chunking_strategy"], row["embedding_model"])].append(row)
    return groups


def _kb_strategy_results(rows: list[dict], query: str, k: int, strategy: RetrievalStrategy, embedding_model: str | None) -> list[StrategyGroupResult]:
    if embedding_model:
        grouped = defaultdict(list)
        for row in rows:
            if row.get("embedding_model") == embedding_model:
                grouped[row["chunking_strategy"]].append(row)
        return [
            _run_group(group_rows, query, k, strategy, embedding_model, chunking_strategy)
            for chunking_strategy, group_rows in sorted(grouped.items())
        ]

    grouped = _group_rows(rows, None)
    return [
        _run_group(group_rows, query, k, strategy, model, chunking_strategy)
        for (chunking_strategy, model), group_rows in sorted(grouped.items())
    ]


def retrieve_documents(request: RetrieveRequest) -> RetrieveResponse:
    config = get_config()
    strategy = request.retrieval_strategy or _default_retrieval_strategy()
    strategy = _validate_retrieval_strategy(strategy)
    k = request.k or config.knn_k
    store = JSONLStore()
    logger.info("Retrieve pipeline started query=%r kb_name=%s k=%s embedding_model=%s", request.query, request.kb_name, k, request.embedding_model)

    if not request.query.strip():
        raise ValueError("EMPTY_QUERY")

    if request.kb_name:
        kb_name = request.kb_name
        kb_path = store.kb_path(kb_name)
        if not kb_path.exists():
            raise FileNotFoundError(kb_name)
        rows = [row for row in store.read_rows(kb_name) if row.get("is_active")]
        logger.info("Loaded kb_name=%s active_rows=%s", kb_name, len(rows))
        strategy_results = _kb_strategy_results(rows, request.query, k, strategy, request.embedding_model)
        return RetrieveResponse(
            query=request.query,
            retrieval_strategy_used=strategy,
            k_used=k,
            results=[KBResult(kb_name=kb_name, strategy_results=strategy_results)],
        )

    kb_results: list[KBResult] = []
    kb_files = store.list_kb_files()
    if not kb_files:
        logger.info("No knowledge base files found in vector store")
        return RetrieveResponse(
            query=request.query,
            retrieval_strategy_used=strategy,
            k_used=k,
            results=[],
        )

    for file_path in kb_files:
        kb_name = file_path.stem
        rows = [row for row in store.read_rows(kb_name) if row.get("is_active")]
        logger.info("Loaded kb_name=%s active_rows=%s", kb_name, len(rows))
        strategy_results = _kb_strategy_results(rows, request.query, k, strategy, request.embedding_model)
        kb_results.append(KBResult(kb_name=kb_name, strategy_results=strategy_results))

    logger.info("Retrieve pipeline completed kb_count=%s", len(kb_results))
    return RetrieveResponse(
        query=request.query,
        retrieval_strategy_used=strategy,
        k_used=k,
        results=kb_results,
    )
