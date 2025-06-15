from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import threading
import time
from typing import Optional
from ..services.face_detection_service import face_detection_service

router = APIRouter()

class CameraManager:
    def __init__(self):
        self.camera = None
        self.is_streaming = False
        self.lock = threading.Lock()
    
    def start_camera(self, camera_index: int = 0):
        """카메라를 시작합니다."""
        with self.lock:
            if self.camera is not None:
                self.camera.release()
            
            try:
                self.camera = cv2.VideoCapture(camera_index)
                if not self.camera.isOpened():
                    raise Exception(f"카메라 {camera_index}를 열 수 없습니다.")
                
                # 카메라 설정
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.camera.set(cv2.CAP_PROP_FPS, 30)
                
                self.is_streaming = True
                print(f"카메라 {camera_index} 시작됨 (얼굴 탐지 활성화)")
                return True
                
            except Exception as e:
                print(f"카메라 시작 오류: {e}")
                self.camera = None
                self.is_streaming = False
                return False
    
    def stop_camera(self):
        """카메라를 중지합니다."""
        with self.lock:
            self.is_streaming = False
            if self.camera is not None:
                self.camera.release()
                self.camera = None
                print("카메라 중지됨")
    
    def generate_frames(self):
        """프레임을 생성합니다."""
        frame_count = 0
        
        while self.is_streaming:
            with self.lock:
                if self.camera is None or not self.camera.isOpened():
                    break
                
                success, frame = self.camera.read()
                if not success:
                    print("프레임을 읽을 수 없습니다.")
                    break
                
                # 미러 효과 (좌우 반전)
                # frame = cv2.flip(frame, 1)
                
                # 얼굴 탐지 및 바운딩 박스 그리기 (항상 활성화)
                try:
                    frame = face_detection_service.process_frame(frame)
                except Exception as e:
                    print(f"얼굴 탐지 오류: {e}")
                    # 얼굴 탐지에 실패해도 원본 프레임을 계속 전송
                
                # 프레임을 JPEG로 인코딩
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if not ret:
                    continue
                
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # FPS 조절 (약 30 FPS)
            time.sleep(0.033)
            frame_count += 1

# 전역 카메라 매니저 인스턴스
camera_manager = CameraManager()

@router.get("/stream")
async def video_stream():
    """비디오 스트림을 반환합니다."""
    if not camera_manager.is_streaming:
        # 카메라가 시작되지 않았다면 시작 시도
        if not camera_manager.start_camera():
            raise HTTPException(status_code=500, detail="카메라를 시작할 수 없습니다.")
    
    return StreamingResponse(
        camera_manager.generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.post("/start")
async def start_camera(camera_index: int = 0):
    """카메라를 시작합니다."""
    try:
        success = camera_manager.start_camera(camera_index)
        if success:
            return {"message": f"카메라 {camera_index} 시작됨", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="카메라를 시작할 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_camera():
    """카메라를 중지합니다."""
    try:
        camera_manager.stop_camera()
        return {"message": "카메라 중지됨", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def camera_status():
    """카메라 상태를 반환합니다."""
    return {
        "is_streaming": camera_manager.is_streaming,
        "camera_active": camera_manager.camera is not None and camera_manager.camera.isOpened(),
        "face_detection_enabled": True  # 항상 활성화
    }

@router.get("/face-count")
async def get_face_count():
    """현재 프레임에서 탐지된 얼굴 개수를 반환합니다."""
    try:
        if not camera_manager.is_streaming or camera_manager.camera is None:
            return {"face_count": 0, "message": "카메라가 활성화되지 않음"}
        
        with camera_manager.lock:
            success, frame = camera_manager.camera.read()
            if not success:
                return {"face_count": 0, "message": "프레임을 읽을 수 없음"}
            
            # frame = cv2.flip(frame, 1)
            face_count = face_detection_service.get_face_count(frame)
            
            return {
                "face_count": face_count,
                "message": f"{face_count}개의 얼굴이 탐지됨"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))