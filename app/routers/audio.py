from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.audio_service import start_audio_stream, start_speech_recognition
import asyncio
from starlette.websockets import WebSocketState

router = APIRouter()

@router.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    """오디오 스트림과 음성 인식을 위한 WebSocket 엔드포인트"""
    await websocket.accept()
    print("Audio WebSocket connected")
    
    try:
        # asyncio.gather로 두 비동기 작업 병렬 실행
        await asyncio.gather(
            start_audio_stream(websocket),
            start_speech_recognition(websocket)
        )
    except WebSocketDisconnect:
        print("Audio WebSocket disconnected by client.")
    except asyncio.CancelledError:
        print("Audio async task was cancelled.")
    except Exception as e:
        print(f"Audio WebSocket unexpected error: {e}")
    finally:
        # WebSocket 상태 확인 후 안전하게 닫기
        if websocket.application_state == WebSocketState.CONNECTED:
            try:
                await websocket.close()
            except RuntimeError as e:
                print(f"Error during Audio WebSocket close: {e}")
        print("Audio WebSocket closed cleanly.")