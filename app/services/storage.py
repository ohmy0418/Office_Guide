from __future__ import annotations

import uuid
from pathlib import Path

from app.config import settings


class LocalStorageService:
    """로컬 디렉터리 기반 최소 스토리지 — MinIO/사내 스토리지는 이후 교체."""

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or settings.STORAGE_ROOT)
        self.root.mkdir(parents=True, exist_ok=True)

    def object_path(self, document_id: uuid.UUID, filename: str) -> Path:
        safe_name = Path(filename).name
        dir_path = self.root / str(document_id)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path / safe_name

    def save_bytes(self, document_id: uuid.UUID, filename: str, data: bytes) -> str:
        path = self.object_path(document_id, filename)
        path.write_bytes(data)
        return str(path.resolve())
