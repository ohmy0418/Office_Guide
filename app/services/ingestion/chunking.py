from __future__ import annotations

import re

import tiktoken

from app.config import settings


def _encoding() -> tiktoken.Encoding:
    return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(_encoding().encode(text))


def merge_paragraphs_into_chunks(
    paragraphs: list[tuple[int, str]],
) -> list[dict]:
    """
    (page_1based, text) 목록을 토큰 예산에 맞춰 chunk로 병합한다.
    """
    target = settings.CHUNK_TARGET_TOKENS
    max_t = settings.CHUNK_MAX_TOKENS
    chunks: list[dict] = []
    buf: list[tuple[int, str]] = []

    def flush() -> None:
        nonlocal buf
        if not buf:
            return
        pages = [p for p, _ in buf]
        parts = [t for _, t in buf]
        content = "\n\n".join(parts).strip()
        page_start = min(pages)
        page_end = max(pages)
        heading, heading_path = _guess_heading(content)
        chunks.append(
            {
                "content": content,
                "page_start": page_start,
                "page_end": page_end,
                "heading": heading,
                "heading_path": heading_path,
            }
        )
        buf = []

    for page, text in paragraphs:
        piece = text.strip()
        if not piece:
            continue

        if count_tokens(piece) > max_t:
            flush()
            for sub in _split_oversized(piece, max_t):
                buf.append((page, sub))
                flush()
            continue

        trial_parts = [t for _, t in buf] + [piece]
        trial = "\n\n".join(trial_parts)
        if buf and count_tokens(trial) > max_t:
            flush()
            buf.append((page, piece))
        else:
            buf.append((page, piece))

        merged = "\n\n".join(t for _, t in buf)
        tok = count_tokens(merged)
        if tok >= target:
            flush()
        elif tok > max_t:
            flush()

    flush()
    return chunks


def _guess_heading(content: str) -> tuple[str | None, str | None]:
    first_line = content.split("\n", 1)[0].strip()
    if len(first_line) <= 100 and not first_line.endswith("."):
        if re.match(r"^[\d\.\)\s가-힣A-Za-z·\-]{2,80}$", first_line):
            return first_line, first_line
    return None, None


def _split_oversized(text: str, max_tokens: int) -> list[str]:
    enc = _encoding()
    ids = enc.encode(text)
    if len(ids) <= max_tokens:
        return [text]
    out: list[str] = []
    step = max(1, max_tokens)
    for i in range(0, len(ids), step):
        out.append(enc.decode(ids[i : i + step]))
    return out
