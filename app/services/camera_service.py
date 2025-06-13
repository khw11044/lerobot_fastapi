import cv2
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

class CameraService:
    def __init__(self):
        self.cameras = {}  # 활성 카메라들
        self.executor = ThreadPoolExecutor(max_workers=4)  # 카메라별 스레드
        self.last_frame_time = {}  # 프레임 타이밍 관리
    
    def open_camera(self, camera_id: int):
        """카메라를 열고 초기화합니다."""
        if camera_id not in self.cameras:
            try:
                cap = cv2.VideoCapture(camera_id)
                
                if not cap.isOpened():
                    print(f"Cannot open camera {camera_id}")
                    return False
                
                # 카메라 설정 최적화 (옛날 코드 스타일)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 버퍼 크기 최소화
                
                # 추가 최적화 설정
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # MJPEG 코덱
                
                self.cameras[camera_id] = cap
                self.last_frame_time[camera_id] = time.time()
                print(f"Camera {camera_id} opened successfully")
                return True
                
            except Exception as e:
                print(f"Error opening camera {camera_id}: {e}")
                return False
        
        return True
    
    def close_camera(self, camera_id: int):
        """특정 카메라를 닫습니다."""
        if camera_id in self.cameras:
            try:
                self.cameras[camera_id].release()
                del self.cameras[camera_id]
                if camera_id in self.last_frame_time:
                    del self.last_frame_time[camera_id]
                print(f"Camera {camera_id} closed")
            except Exception as e:
                print(f"Error closing camera {camera_id}: {e}")
    
    def capture_frame_sync(self, camera_id: int):
        """동기적으로 프레임을 캡처합니다 (옛날 코드 스타일)."""
        try:
            if camera_id not in self.cameras:
                if not self.open_camera(camera_id):
                    return None
            
            cap = self.cameras[camera_id]
            ret, frame = cap.read()
            
            if ret:
                # 프레임 타이밍 업데이트
                self.last_frame_time[camera_id] = time.time()
                
                # JPEG 인코딩 (품질 85%)
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
                ret_encode, buffer = cv2.imencode('.jpg', frame, encode_param)
                
                if ret_encode:
                    return buffer.tobytes()
            
            return None
            
        except Exception as e:
            print(f"Error capturing frame from camera {camera_id}: {e}")
            return None
    
    async def get_frame(self, camera_id: int):
        """비동기적으로 프레임을 가져옵니다."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.capture_frame_sync, camera_id)
    
    def get_camera_info(self, camera_id: int):
        """카메라 정보를 반환합니다."""
        if camera_id in self.cameras:
            cap = self.cameras[camera_id]
            return {
                "camera_id": camera_id,
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "fps": cap.get(cv2.CAP_PROP_FPS),
                "fourcc": int(cap.get(cv2.CAP_PROP_FOURCC)),
                "last_frame_time": self.last_frame_time.get(camera_id, 0),
                "is_active": True
            }
        return {"camera_id": camera_id, "is_active": False}
    
    def get_all_cameras_info(self):
        """모든 활성 카메라 정보를 반환합니다."""
        return {camera_id: self.get_camera_info(camera_id) for camera_id in self.cameras.keys()}
    
    def close_all_cameras(self):
        """모든 카메라를 닫습니다."""
        camera_ids = list(self.cameras.keys())
        for camera_id in camera_ids:
            self.close_camera(camera_id)
    
    def cleanup_inactive_cameras(self, timeout=30):
        """비활성 카메라를 정리합니다."""
        current_time = time.time()
        inactive_cameras = []
        
        for camera_id, last_time in self.last_frame_time.items():
            if current_time - last_time > timeout:
                inactive_cameras.append(camera_id)
        
        for camera_id in inactive_cameras:
            print(f"Cleaning up inactive camera {camera_id}")
            self.close_camera(camera_id)
    
    def restart_camera(self, camera_id: int):
        """카메라를 재시작합니다."""
        print(f"Restarting camera {camera_id}")
        self.close_camera(camera_id)
        return self.open_camera(camera_id)
    
    def __del__(self):
        """소멸자에서 모든 카메라를 정리합니다."""
        self.close_all_cameras()
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)