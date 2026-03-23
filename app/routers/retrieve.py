from __future__ import annotations

import logging

from fastapi import APIRouter

from app.errors import error_response
from app.models import RetrieveRequest
from app.services.retrieval_service import retrieve_documents


router = APIRouter()
logger = logging.getLogger("nexvec.retrieve")


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped or stripped.lower() == "string":
        return None
    return stripped


def _strip_embedding_vectors(payload: dict) -> dict:
    for kb_result in payload.get("results", []):
        for strategy_result in kb_result.get("strategy_results", []):
            for chunk in strategy_result.get("chunks", []):
                chunk.pop("embedding_vector", None)
    return payload


@router.post("/retrieve")
def retrieve(request: RetrieveRequest):
    try:
        request.kb_name = _clean_optional_text(request.kb_name)
        request.embedding_model = _clean_optional_text(request.embedding_model)
        logger.info(
            "Retrieve request received query=%r kb_name=%s k=%s algorithm=%s distance_metric=%s embedding_model=%s excludevectors=%s",
            request.query,
            request.kb_name,
            request.k,
            request.retrieval_strategy.algorithm if request.retrieval_strategy else None,
            request.retrieval_strategy.distance_metric if request.retrieval_strategy else None,
            request.embedding_model,
            request.excludevectors,
        )
        response = retrieve_documents(request)
        payload = response.model_dump()
        if request.excludevectors:
            payload = _strip_embedding_vectors(payload)
            logger.info("Embedding vectors excluded from retrieve response")
        logger.info("Retrieve completed kb_count=%s", len(payload.get("results", [])))
        return payload
    except ValueError as exc:
        message = str(exc)
        if message == "EMPTY_QUERY":
            return error_response(400, "EMPTY_QUERY", "The query cannot be empty or whitespace only.")
        if "ann" in message.lower():
            return error_response(400, "INVALID_RETRIEVAL_STRATEGY", message)
        return error_response(400, "INVALID_RETRIEVAL_STRATEGY", message)
    except FileNotFoundError as exc:
        return error_response(404, "KB_NOT_FOUND", f"Knowledge base '{exc.args[0]}' was not found.", {"kb_name": exc.args[0]})
    except Exception as exc:
        return error_response(500, "RETRIEVAL_ERROR", str(exc))
