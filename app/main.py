from fastapi import FastAPI

from app.api.v1.router import api_router
from app.config import settings

app = FastAPI(
    title="회사생활가이드 API",
    version="0.1.0",
    description="docs/specify.md 기준 v1 백엔드 골격",
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "office-guide", "docs": "/docs"}
