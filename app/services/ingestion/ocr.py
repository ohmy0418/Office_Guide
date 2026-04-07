from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from app.config import settings


class OcrFailedError(Exception):
    def __init__(self, message: str, stderr: str | None = None) -> None:
        super().__init__(message)
        self.stderr = stderr


def run_ocrmypdf(input_pdf: Path) -> Path:
    """
    OCRmyPDF로 검색 가능한 텍스트 레이어를 추가한 PDF를 임시 파일로 만든다.
    시스템에 tesseract, ghostscript 등이 설치되어 있어야 한다.
    """
    fd, out_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    out = Path(out_path)
    cmd = [
        "ocrmypdf",
        "-l",
        settings.OCR_LANG,
        "--optimize",
        "0",
        str(input_pdf),
        str(out),
    ]
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise OcrFailedError(
                f"ocrmypdf 실패 (exit {proc.returncode})",
                stderr=proc.stderr,
            )
    except FileNotFoundError as e:
        out.unlink(missing_ok=True)
        raise OcrFailedError(
            "ocrmypdf 실행 파일을 찾을 수 없습니다. OCRmyPDF와 Tesseract 설치를 확인하세요."
        ) from e
    except OcrFailedError:
        out.unlink(missing_ok=True)
        raise
    return out
