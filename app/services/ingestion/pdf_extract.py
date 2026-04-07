from __future__ import annotations

import re
from pathlib import Path

import fitz

from app.config import settings


def total_text_length(pdf_path: Path) -> int:
    doc = fitz.open(pdf_path)
    try:
        return sum(len(page.get_text("text") or "") for page in doc)
    finally:
        doc.close()


def needs_ocr(pdf_path: Path) -> bool:
    """텍스트가 거의 없으면 OCR 경로를 탄다."""
    return total_text_length(pdf_path) < settings.OCR_TEXT_THRESHOLD_CHARS


def extract_paragraphs_with_pages(pdf_path: Path) -> list[tuple[int, str]]:
    """페이지별 본문을 문단 단위로 분리한다. 표/제목 구조는 v1에서 텍스트 블록으로 통합 추출."""
    doc = fitz.open(pdf_path)
    out: list[tuple[int, str]] = []
    try:
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            text = page.get_text("text") or ""
            parts = re.split(r"\n\s*\n+", text)
            for part in parts:
                cleaned = part.strip()
                if cleaned:
                    out.append((page_idx + 1, cleaned))
    finally:
        doc.close()
    return out
