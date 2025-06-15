import time
import threading
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class FaceState:
    """얼굴 상태 정보를 담는 데이터 클래스"""
    has_face: bool = False
    user_id: Optional[str] = None
    is_recognized: bool = False
    last_seen: float = 0.0
    search_performed: bool = False
    bbox: Optional[tuple] = None

class SessionManager:
    def __init__(self, face_timeout: float = 5.0):
        """
        세션 관리자 초기화
        
        Args:
            face_timeout (float): 얼굴 사라짐 후 로그아웃까지의 시간 (초)
        """
        self.face_timeout = face_timeout
        self.face_state = FaceState()
        self.lock = threading.Lock()
        self.pending_user_registration = None  # 등록 대기 중인 사용자 정보
        
        print(f"세션 매니저 초기화 (타임아웃: {face_timeout}초)")
    
    def update_face_detected(self, bbox: tuple) -> bool:
        """
        얼굴이 감지되었을 때 상태를 업데이트합니다.
        
        Args:
            bbox (tuple): 얼굴 바운딩 박스 좌표
            
        Returns:
            bool: 새로운 얼굴이 감지되었으면 True (DB 검색 필요)
        """
        with self.lock:
            current_time = time.time()
            
            # 이전에 얼굴이 없었다면 새로운 얼굴 감지
            if not self.face_state.has_face:
                self.face_state.has_face = True
                self.face_state.last_seen = current_time
                self.face_state.bbox = bbox
                self.face_state.search_performed = False
                
                print("새로운 얼굴 감지됨 - DB 검색 필요")
                return True
            
            # 기존 얼굴이 계속 있는 경우
            self.face_state.last_seen = current_time
            self.face_state.bbox = bbox
            return False
    
    def update_no_face_detected(self) -> bool:
        """
        얼굴이 감지되지 않았을 때 상태를 업데이트합니다.
        
        Returns:
            bool: 로그아웃이 필요하면 True
        """
        with self.lock:
            current_time = time.time()
            
            # 얼굴이 있었는데 없어진 경우
            if self.face_state.has_face:
                # 타임아웃 체크
                if current_time - self.face_state.last_seen >= self.face_timeout:
                    self.reset_face_state()
                    print("얼굴 타임아웃 - 로그아웃 필요")
                    return True
            
            return False
    
    def set_recognized_user(self, user_id: str):
        """
        인식된 사용자 정보를 설정합니다.
        
        Args:
            user_id (str): 인식된 사용자 ID
        """
        with self.lock:
            self.face_state.user_id = user_id
            self.face_state.is_recognized = True
            self.face_state.search_performed = True
            print(f"사용자 인식됨: {user_id}")
    
    def set_unknown_user(self):
        """
        알 수 없는 사용자로 설정합니다.
        """
        with self.lock:
            self.face_state.user_id = None
            self.face_state.is_recognized = False
            self.face_state.search_performed = True
            print("알 수 없는 사용자로 설정됨")
    
    def should_perform_search(self) -> bool:
        """
        DB 검색을 수행해야 하는지 확인합니다.
        
        Returns:
            bool: 검색이 필요하면 True
        """
        with self.lock:
            return (self.face_state.has_face and 
                   not self.face_state.search_performed)
    
    def get_current_face_info(self) -> Dict[str, Any]:
        """
        현재 얼굴 상태 정보를 반환합니다.
        
        Returns:
            Dict: 얼굴 상태 정보
        """
        with self.lock:
            return {
                "has_face": self.face_state.has_face,
                "user_id": self.face_state.user_id,
                "is_recognized": self.face_state.is_recognized,
                "search_performed": self.face_state.search_performed,
                "bbox": self.face_state.bbox,
                "time_since_last_seen": time.time() - self.face_state.last_seen if self.face_state.has_face else None
            }
    
    def get_face_bbox(self) -> Optional[tuple]:
        """
        현재 얼굴의 바운딩 박스를 반환합니다.
        
        Returns:
            Optional[tuple]: 바운딩 박스 좌표 또는 None
        """
        with self.lock:
            return self.face_state.bbox
    
    def get_current_user_id(self) -> Optional[str]:
        """
        현재 인식된 사용자 ID를 반환합니다.
        
        Returns:
            Optional[str]: 사용자 ID 또는 None
        """
        with self.lock:
            return self.face_state.user_id if self.face_state.is_recognized else None
    
    def reset_face_state(self):
        """
        얼굴 상태를 초기화합니다.
        """
        with self.lock:
            self.face_state = FaceState()
            self.pending_user_registration = None
            print("얼굴 상태 초기화됨")
    
    def set_pending_registration(self, user_id: str, bbox: tuple):
        """
        사용자 등록 대기 상태를 설정합니다.
        
        Args:
            user_id (str): 등록할 사용자 ID
            bbox (tuple): 얼굴 바운딩 박스
        """
        with self.lock:
            self.pending_user_registration = {
                "user_id": user_id,
                "bbox": bbox,
                "timestamp": time.time()
            }
            print(f"사용자 등록 대기 중: {user_id}")
    
    def get_pending_registration(self) -> Optional[Dict]:
        """
        대기 중인 사용자 등록 정보를 반환합니다.
        
        Returns:
            Optional[Dict]: 등록 정보 또는 None
        """
        with self.lock:
            return self.pending_user_registration
    
    def clear_pending_registration(self):
        """
        대기 중인 사용자 등록 정보를 삭제합니다.
        """
        with self.lock:
            self.pending_user_registration = None
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        세션 통계 정보를 반환합니다.
        
        Returns:
            Dict: 세션 통계
        """
        with self.lock:
            current_time = time.time()
            return {
                "face_timeout": self.face_timeout,
                "current_state": {
                    "has_face": self.face_state.has_face,
                    "user_id": self.face_state.user_id,
                    "is_recognized": self.face_state.is_recognized,
                    "time_since_last_seen": current_time - self.face_state.last_seen if self.face_state.has_face else None
                },
                "pending_registration": self.pending_user_registration is not None,
                "uptime": current_time
            }

# 전역 인스턴스
session_manager = SessionManager(face_timeout=5.0)