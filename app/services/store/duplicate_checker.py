from __future__ import annotations


def find_duplicate_rows(rows: list[dict], source_filename: str, chunking_strategy: str, embedding_model: str) -> list[dict]:
    return [
        row
        for row in rows
        if row.get("is_active")
        and row.get("source_filename") == source_filename
        and row.get("chunking_strategy") == chunking_strategy
        and row.get("embedding_model") == embedding_model
    ]

