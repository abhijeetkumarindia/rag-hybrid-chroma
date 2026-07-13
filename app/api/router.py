from fastapi import APIRouter

from app.api.v1 import document , embedding , chat
api_router = APIRouter()

api_router.include_router(document.router, prefix="/api/v1")
api_router.include_router(embedding.router, prefix="/api/v1")
api_router.include_router(chat.router, prefix="/api/v1")
