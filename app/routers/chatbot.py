from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.llm_service import LLMService

router = APIRouter()
llm_service = LLMService()

# 요청 데이터 구조 정의
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

@router.post("/chat")
async def chat(request: ChatRequest):
    """사용자 메시지를 받아서 AI 응답을 반환합니다."""
    try:
        print(f'[사용자 ({request.session_id})] {request.message}')
        
        # AI 응답 생성
        response = await llm_service.generate_response(request.message, request.session_id)
        
        print(f'[AI] {response}')
        
        return {"response": response}
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear")
async def clear_chat(session_id: str = "default"):
    """채팅 기록을 초기화합니다."""
    try:
        llm_service.clear_history(session_id)
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))