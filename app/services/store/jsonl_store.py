from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.config import get_config


class JSONLStore:
    def __init__(self) -> None:
        self.config = get_config()

    def ensure_store_path(self) -> None:
        self.config.vector_store_path.mkdir(parents=True, exist_ok=True)

    def kb_path(self, kb_name: str) -> Path:
        self.ensure_store_path()
        return self.config.vector_store_path / f"{kb_name}.jsonl"

    def list_kb_files(self) -> list[Path]:
        self.ensure_store_path()
        return sorted(self.config.vector_store_path.glob("*.jsonl"))

    def read_rows(self, kb_name: str) -> list[dict[str, Any]]:
        path = self.kb_path(kb_name)
        if not path.exists():
            return []
        rows: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def write_rows(self, kb_name: str, rows: list[dict[str, Any]]) -> None:
        path = self.kb_path(kb_name)
        existing = self.read_rows(kb_name)
        merged = existing + rows
        with path.open("w", encoding="utf-8") as handle:
            for row in merged:
                handle.write(json.dumps(row, ensure_ascii=False))
                handle.write("\n")

    def update_rows(self, kb_name: str, updated_rows: list[dict[str, Any]]) -> None:
        path = self.kb_path(kb_name)
        with path.open("w", encoding="utf-8") as handle:
            for row in updated_rows:
                handle.write(json.dumps(row, ensure_ascii=False))
                handle.write("\n")

