from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.communication_service import communication_service
from ..config import config

router = APIRouter()

# 요청 데이터 구조 정의
class ManualMessageRequest(BaseModel):
    message: str

class TestConnectionRequest(BaseModel):
    test_message: str = "TEST_CONNECTION_FROM_MANUAL"

@router.get("/status")
async def get_robot_status():
    """로봇 통신 상태를 반환합니다."""
    try:
        status = communication_service.get_status()
        return {
            "status": "online",
            "robot_config": status,
            "message": "로봇 통신 서비스가 활성화되어 있습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 확인 오류: {str(e)}")

@router.post("/test-connection")
async def test_robot_connection(request: TestConnectionRequest):
    """로봇 제어 PC와의 연결을 테스트합니다."""
    try:
        success = communication_service.send_message(request.test_message)
        
        if success:
            return {
                "status": "success",
                "message": f"테스트 메시지가 {config.ROBOT_PC_IP}:{config.ROBOT_PC_PORT}로 전송되었습니다.",
                "sent_message": request.test_message
            }
        else:
            return {
                "status": "failed",
                "message": "로봇 제어 PC와의 통신에 실패했습니다.",
                "robot_address": f"{config.ROBOT_PC_IP}:{config.ROBOT_PC_PORT}"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"연결 테스트 오류: {str(e)}")

@router.post("/send-manual-message")
async def send_manual_message(request: ManualMessageRequest):
    """수동으로 메시지를 로봇 제어 PC에 전송합니다."""
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="메시지가 비어있습니다.")
        
        success = communication_service.send_message(request.message)
        
        if success:
            return {
                "status": "success",
                "message": "메시지가 성공적으로 전송되었습니다.",
                "sent_message": request.message,
                "robot_address": f"{config.ROBOT_PC_IP}:{config.ROBOT_PC_PORT}"
            }
        else:
            return {
                "status": "failed",
                "message": "메시지 전송에 실패했습니다.",
                "robot_address": f"{config.ROBOT_PC_IP}:{config.ROBOT_PC_PORT}"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메시지 전송 오류: {str(e)}")

@router.get("/config")
async def get_robot_config():
    """현재 로봇 통신 설정을 반환합니다."""
    try:
        return {
            "robot_ip": config.ROBOT_PC_IP,
            "robot_port": config.ROBOT_PC_PORT,
            "udp_timeout": config.UDP_TIMEOUT,
            "udp_buffer_size": config.UDP_BUFFER_SIZE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"설정 조회 오류: {str(e)}")