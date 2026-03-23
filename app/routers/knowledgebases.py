from __future__ import annotations

from fastapi import APIRouter

from app.services.store.jsonl_store import JSONLStore


router = APIRouter()


@router.get("/knowledgebases")
def list_knowledgebases() -> dict:
    store = JSONLStore()
    kb_names = [path.stem for path in store.list_kb_files()]
    return {"knowledgebases": kb_names}

