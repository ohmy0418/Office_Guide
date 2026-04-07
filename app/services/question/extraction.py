from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractedEntities:
    """docs/specify.md 8.2 추출 대상."""

    person_names: list[str] = field(default_factory=list)
    departments: list[str] = field(default_factory=list)
    document_hints: list[str] = field(default_factory=list)
    time_expressions: list[str] = field(default_factory=list)
    condition_values: list[str] = field(default_factory=list)
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "person_names": self.person_names,
            "departments": self.departments,
            "document_hints": self.document_hints,
            "time_expressions": self.time_expressions,
            "condition_values": self.condition_values,
            "emails": self.emails,
            "phones": self.phones,
        }


_DEPARTMENT = re.compile(
    r"([\w가-힣·\-\d]{2,30}(?:팀|부|실|본부|센터|과|처|원|국|단))",
)
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE = re.compile(
    r"(?:\+82[-\s]?)?(?:0\d{1,2}[-\s]?\d{3,4}[-\s]?\d{4})",
)
_TIME = re.compile(
    r"(올해|작년|내년|최신|현재|금일|당일|이번\s*달|지난달|오늘|어제|202\d년|20\d\d[-/]\d{1,2})",
)
_CONDITION = re.compile(
    r"(\d{1,4}(?:,\d{3})*(?:\.\d+)?)\s*(?:원|만원|일|시간|km|m|명|건|%|퍼센트)",
)
_NAME_CTX = re.compile(
    r"(?:담당(?:자|팀)?|매니저|팀장|과장|부장|이름|직원)\s*[:：]?\s*([가-힣]{2,4})\b|"
    r"\b([가-힣]{2,4})\s*(?:님|씨)(?=\s|$|[,，])",
)
_DOC_FRAGMENT = re.compile(
    r"([\w가-힣·\s]{2,40}?(?:규정|지침|가이드|매뉴얼|방침|절차|정책|기준))",
)


def extract_entities(text: str) -> ExtractedEntities:
    """규칙 기반 최소 추출."""
    e = ExtractedEntities()
    e.emails = list(dict.fromkeys(_EMAIL.findall(text)))
    e.phones = list(dict.fromkeys(_PHONE.findall(text)))
    e.time_expressions = list(dict.fromkeys(_TIME.findall(text)))
    e.condition_values = [m.group(1) for m in _CONDITION.finditer(text)]

    for m in _DEPARTMENT.finditer(text):
        val = m.group(1).strip()
        if val not in e.departments:
            e.departments.append(val)

    for m in _DOC_FRAGMENT.finditer(text):
        hint = m.group(1).strip()
        if len(hint) >= 2 and hint not in e.document_hints:
            e.document_hints.append(hint[:200])

    for m in _NAME_CTX.finditer(text):
        name = m.group(1) or m.group(2)
        if name and name not in e.person_names:
            e.person_names.append(name)

    return e
