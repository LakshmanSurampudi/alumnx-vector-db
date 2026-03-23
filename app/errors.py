from __future__ import annotations

from fastapi.responses import JSONResponse


def error_response(status_code: int, error: str, message: str, detail: dict | None = None) -> JSONResponse:
    payload = {"error": error, "message": message}
    if detail is not None:
        payload["detail"] = detail
    return JSONResponse(status_code=status_code, content=payload)

