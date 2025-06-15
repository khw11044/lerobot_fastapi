from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from .routers import chatbot, camera, robot
import os

app = FastAPI(title="LLM 챗봇 with 로봇 제어 & 얼굴 인식", version="1.1.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# 라우터 등록
app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(camera.router, prefix="/camera", tags=["Camera"])  # 얼굴 인식 기능 포함
app.include_router(robot.router, prefix="/robot", tags=["Robot"])

# 메인 페이지 서빙
@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "LLM 챗봇 서버가 정상 작동 중입니다.",
        "features": [
            "AI 챗봇",
            "실시간 카메라 (얼굴 인식 자동 활성화)",
            "로봇 제어 통신"
        ]
    }

# 앱 종료 시 리소스 정리
@app.on_event("shutdown")
async def shutdown_event():
    # 카메라 리소스 정리
    from .routers.camera import camera_manager
    camera_manager.stop_camera()
    
    # 얼굴 탐지 서비스 정리
    from .services.face_detection_service import face_detection_service
    face_detection_service.close()
    
    print("애플리케이션이 정상적으로 종료되었습니다.")