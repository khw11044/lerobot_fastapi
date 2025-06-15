from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from .routers import chatbot, camera, robot, face
import os

# FastAPI 애플리케이션 초기화
app = FastAPI(
    title="LLM 챗봇 with 로봇 제어 & 얼굴 인식", 
    version="2.0.0",
    description="AI 챗봇, 실시간 카메라, 얼굴 인식 자동 로그인, 로봇 제어 통신을 지원하는 통합 시스템"
)

# CORS 미들웨어 설정 (모든 도메인에서 접근 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # 모든 도메인 허용
    allow_credentials=True,        # 쿠키/인증 정보 허용
    allow_methods=["*"],           # 모든 HTTP 메소드 허용
    allow_headers=["*"],           # 모든 헤더 허용
)

# 정적 파일 서빙 설정 (HTML, CSS, JS 파일들)
app.mount("/static", StaticFiles(directory="static"), name="static")

# API 라우터 등록
app.include_router(
    chatbot.router, 
    prefix="/chatbot", 
    tags=["Chatbot"],
    responses={404: {"description": "Chatbot endpoint not found"}}
)

app.include_router(
    camera.router, 
    prefix="/camera", 
    tags=["Camera & Face Detection"],
    responses={404: {"description": "Camera endpoint not found"}}
)

app.include_router(
    robot.router, 
    prefix="/robot", 
    tags=["Robot Control"],
    responses={404: {"description": "Robot endpoint not found"}}
)

app.include_router(
    face.router, 
    prefix="/face", 
    tags=["Face Recognition"],
    responses={404: {"description": "Face recognition endpoint not found"}}
)

# 루트 경로 - 메인 페이지 서빙
@app.get("/", response_class=HTMLResponse, summary="메인 페이지")
async def get_index():
    """
    메인 웹 페이지를 반환합니다.
    
    Returns:
        HTMLResponse: index.html 파일 내용
    """
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>404 - index.html 파일을 찾을 수 없습니다.</h1>", 
            status_code=404
        )
    except Exception as e:
        return HTMLResponse(
            content=f"<h1>500 - 서버 오류: {str(e)}</h1>", 
            status_code=500
        )

# 헬스 체크 엔드포인트
@app.get("/health", summary="서버 상태 확인")
async def health_check():
    """
    서버의 현재 상태와 사용 가능한 기능들을 반환합니다.
    
    Returns:
        dict: 서버 상태 정보
    """
    return {
        "status": "healthy",
        "message": "LLM 챗봇 서버가 정상 작동 중입니다.",
        "version": "2.0.0",
        "features": [
            "AI 챗봇 (OpenAI GPT-4o-mini)",
            "실시간 카메라 스트리밍",
            "얼굴 탐지 및 인식 (MediaPipe + FaceNet)",
            "자동 얼굴 인식 로그인/로그아웃",
            "ChromaDB 기반 얼굴 데이터베이스", 
            "세션 기반 대화 기록 관리",
            "UDP 기반 로봇 제어 통신"
        ],
        "endpoints": {
            "chatbot": "/chatbot/*",
            "camera": "/camera/*", 
            "robot": "/robot/*",
            "face": "/face/*",
            "docs": "/docs",
            "health": "/health"
        }
    }

# API 문서 정보 업데이트
@app.get("/info", summary="시스템 정보")
async def get_system_info():
    """
    시스템의 상세 정보를 반환합니다.
    
    Returns:
        dict: 시스템 상세 정보
    """
    return {
        "system": {
            "name": "AI 로봇 사탕가게 시스템",
            "version": "2.0.0",
            "description": "얼굴 인식 기반 자동 로그인과 로봇 제어가 가능한 AI 챗봇 시스템"
        },
        "technologies": {
            "backend": "FastAPI",
            "ai_model": "OpenAI GPT-4o-mini",
            "face_detection": "MediaPipe",
            "face_recognition": "FaceNet (facenet-pytorch)",
            "face_database": "ChromaDB",
            "chat_database": "SQLite",
            "communication": "UDP Socket",
            "frontend": "Vanilla JavaScript + HTML5 + CSS3"
        },
        "capabilities": {
            "face_recognition": {
                "detection": "Real-time face detection",
                "recognition": "FaceNet-based face recognition", 
                "database": "ChromaDB vector storage",
                "auto_login": "Automatic login/logout based on face recognition",
                "session_management": "5-second timeout for face disappearance"
            },
            "chatbot": {
                "model": "OpenAI GPT-4o-mini",
                "memory": "Session-based conversation history",
                "specialization": "Robot candy shop assistant",
                "order_processing": "Automatic order detection and robot communication"
            },
            "robot_control": {
                "protocol": "UDP",
                "format": "String message transmission",
                "trigger": "Order detection in chat responses"
            }
        }
    }

# 앱 시작 이벤트
@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 시 초기화 작업을 수행합니다.
    """
    print("=" * 60)
    print("🤖 AI 로봇 사탕가게 시스템 시작")
    print("=" * 60)
    print("📋 시스템 초기화 중...")
    
    # 서비스들 초기화 확인
    try:
        from .services.face_detection_service import face_detection_service
        from .services.face_recognition_service import face_recognition_service  
        from .services.face_database_service import face_database_service
        from .services.session_manager import session_manager
        from .services.communication_service import communication_service
        
        print("✅ 얼굴 탐지 서비스 활성화")
        print("✅ 얼굴 인식 서비스 활성화") 
        print("✅ 얼굴 데이터베이스 활성화")
        print("✅ 세션 매니저 활성화")
        print("✅ 로봇 통신 서비스 활성화")
        
    except Exception as e:
        print(f"⚠️ 서비스 초기화 중 오류 발생: {e}")
    
    print("🚀 서버가 성공적으로 시작되었습니다!")
    print("🌐 웹 인터페이스: http://localhost:8000")
    print("📖 API 문서: http://localhost:8000/docs")
    print("=" * 60)

# 앱 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    """
    애플리케이션 종료 시 리소스 정리를 수행합니다.
    """
    print("\n" + "=" * 60)
    print("🛑 시스템 종료 중...")
    print("=" * 60)
    
    try:
        # 카메라 리소스 정리
        from .routers.camera import camera_manager
        camera_manager.stop_camera()
        print("✅ 카메라 리소스 정리 완료")
        
        # 얼굴 탐지 서비스 정리
        from .services.face_detection_service import face_detection_service
        face_detection_service.close()
        print("✅ 얼굴 탐지 서비스 정리 완료")
        
        # 세션 매니저 정리
        from .services.session_manager import session_manager
        session_manager.reset_face_state()
        print("✅ 세션 매니저 정리 완료")
        
        print("🎯 모든 리소스 정리 완료")
        
    except Exception as e:
        print(f"⚠️ 리소스 정리 중 오류 발생: {e}")
    
    print("👋 애플리케이션이 정상적으로 종료되었습니다.")
    print("=" * 60)

# 예외 처리 핸들러
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """404 에러 핸들러"""
    return HTMLResponse(
        content="""
        <html>
            <head><title>404 - 페이지를 찾을 수 없습니다</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1>404 - 페이지를 찾을 수 없습니다</h1>
                <p>요청하신 페이지가 존재하지 않습니다.</p>
                <a href="/" style="color: #0b93f6;">메인 페이지로 돌아가기</a>
            </body>
        </html>
        """,
        status_code=404
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """500 에러 핸들러"""
    return HTMLResponse(
        content="""
        <html>
            <head><title>500 - 서버 오류</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1>500 - 서버 내부 오류</h1>
                <p>서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.</p>
                <a href="/" style="color: #0b93f6;">메인 페이지로 돌아가기</a>
            </body>
        </html>
        """,
        status_code=500
    )