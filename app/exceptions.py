from __future__ import annotations

from fastapi import HTTPException


def warning_400(message: str) -> HTTPException:
    return HTTPException(status_code=400, detail={"warning": message})

