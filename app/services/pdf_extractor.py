from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.config import get_config


@dataclass
class ExtractedPage:
    page_number: int
    text: str


def extract_pdf_pages(file_path: str) -> list[ExtractedPage]:
    config = get_config()
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError("pdfplumber is required for PDF extraction") from exc

    pages: list[ExtractedPage] = []
    try:
        pdf = pdfplumber.open(file_path)
    except Exception as exc:
        raise ValueError("PDF is encrypted or password-protected.") from exc

    with pdf:
        for index, page in enumerate(pdf.pages, start=1):
            try:
                text = page.extract_text(layout=True) or ""
            except Exception:
                text = ""
            if not text.strip():
                continue
            text = text.encode("utf-8", errors="replace").decode("utf-8")
            if len(text.strip()) < config.min_page_text_length:
                continue
            pages.append(ExtractedPage(page_number=index, text=text))
    return pages
