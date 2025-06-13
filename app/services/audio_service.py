import asyncio
from fastapi import WebSocket
from starlette.websockets import WebSocketState
import json

async def start_audio_stream(websocket: WebSocket):
    """
    브라우저에서 오디오 데이터를 받아서 처리하는 함수.
    실제 오디오 처리는 클라이언트(브라우저)에서 수행됩니다.
    """
    print("Audio stream started (browser-based)")
    
    try:
        while websocket.application_state == WebSocketState.CONNECTED:
            # 브라우저에서 오는 오디오 데이터를 기다립니다
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Audio stream error: {e}")


async def start_speech_recognition(websocket: WebSocket):
    """
    브라우저 Web Speech API를 통한 음성 인식.
    실제 음성 인식은 클라이언트에서 수행되고 결과만 서버로 전송됩니다.
    """
    print("Speech recognition started (browser-based)")
    
    try:
        while websocket.application_state == WebSocketState.CONNECTED:
            try:
                # 클라이언트에서 오는 메시지를 대기
                data = await websocket.receive_text()
                
                # 클라이언트에서 보낸 음성 인식 결과 처리
                if data.startswith("speech_result:"):
                    text = data.replace("speech_result:", "")
                    print(f"Received speech result: {text}")
                    # 다시 클라이언트로 전송 (다른 연결된 클라이언트들을 위해)
                    await websocket.send_text(f"text:{text}")
                    
                elif data.startswith("speech_error:"):
                    error = data.replace("speech_error:", "")
                    print(f"Speech recognition error: {error}")
                    await websocket.send_text(f"error:{error}")
                    
                elif data.startswith("volume:"):
                    # 볼륨 데이터를 그대로 에코
                    await websocket.send_text(data)
                    
            except Exception as e:
                if websocket.application_state == WebSocketState.CONNECTED:
                    print(f"Error receiving data: {e}")
                break
                
    except Exception as e:
        print(f"Speech recognition error: {e}")
    
    print("Speech recognition ended")