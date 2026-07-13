from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.chat_service import stream_chat

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/stream")
def chat(query: str):
    return StreamingResponse(
        stream_chat(query),
        media_type="text/plain",
    )