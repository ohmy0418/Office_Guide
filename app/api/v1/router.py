from fastapi import APIRouter

from app.api.v1 import documents, health, questions

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(questions.router, tags=["questions"])
