from __future__ import annotations

import re

# docs/specify.md 8.2 정규화 예시 + 확장 초안
_SYNONYMS: list[tuple[str, str]] = [
    (r"법카", "법인카드"),
    (r"반차", "반일연차"),
    (r"여비", "출장비"),
    (r"재택", "재택근무"),
    (r"연차\s*쓰", "연차 사용"),
]

_WS = re.compile(r"\s+")


def normalize_question(text: str) -> str:
    """동의어·표기 통일(규칙 기반)."""
    out = text.strip()
    for pattern, repl in _SYNONYMS:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    out = _WS.sub(" ", out)
    return out
