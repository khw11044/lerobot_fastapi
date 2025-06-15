import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple

class FaceDetectionService:
    def __init__(self, detection_confidence=0.5):
        """
        얼굴 탐지 서비스 초기화 (항상 활성화)
        
        Args:
            detection_confidence (float): 얼굴 탐지 신뢰도 임계값 (0.0-1.0)
        """
        # Mediapipe Face Detection 초기화
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0,  # 0: 2m 이내 근거리 모델, 1: 5m 이내 원거리 모델
            min_detection_confidence=detection_confidence
        )
        
        # 그리기용 유틸리티
        self.mp_drawing = mp.solutions.drawing_utils
        print("얼굴 탐지 서비스가 활성화되었습니다.")
        
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        이미지에서 얼굴을 탐지하고 바운딩 박스 좌표를 반환합니다.
        
        Args:
            image (np.ndarray): 입력 이미지 (BGR 형식)
            
        Returns:
            List[Tuple[int, int, int, int]]: 바운딩 박스 좌표 리스트 [(x1, y1, x2, y2), ...]
        """
        # BGR을 RGB로 변환 (Mediapipe는 RGB를 사용)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 얼굴 탐지 수행
        results = self.face_detection.process(image_rgb)
        
        bboxes = []
        if results.detections:
            h, w, _ = image.shape
            
            for detection in results.detections:
                # 상대 좌표를 절대 좌표로 변환
                bbox = detection.location_data.relative_bounding_box
                x1 = int(bbox.xmin * w)
                y1 = int(bbox.ymin * h)
                x2 = int((bbox.xmin + bbox.width) * w)
                y2 = int((bbox.ymin + bbox.height) * h)
                
                # 좌표가 이미지 범위를 벗어나지 않도록 클리핑
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w, x2)
                y2 = min(h, y2)
                
                bboxes.append((x1, y1, x2, y2))
                
        return bboxes
    
    def draw_face_boxes(self, image: np.ndarray, bboxes: List[Tuple[int, int, int, int]], 
                       color: Tuple[int, int, int] = (0, 0, 255), thickness: int = 2) -> np.ndarray:
        """
        이미지에 얼굴 바운딩 박스를 그립니다.
        
        Args:
            image (np.ndarray): 입력 이미지
            bboxes (List[Tuple]): 바운딩 박스 좌표 리스트
            color (Tuple[int, int, int]): 바운딩 박스 색상 (BGR)
            thickness (int): 선 두께
            
        Returns:
            np.ndarray: 바운딩 박스가 그려진 이미지
        """
        annotated_image = image.copy()
        
        for bbox in bboxes:
            x1, y1, x2, y2 = bbox
            
            # 빨간색 바운딩 박스 그리기
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, thickness)
            
            # 선택적으로 "Face" 라벨 추가 (작게)
            cv2.putText(annotated_image, "Face", (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, thickness)
        
        return annotated_image
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        프레임을 처리하여 얼굴 탐지 및 바운딩 박스 그리기를 수행합니다.
        
        Args:
            frame (np.ndarray): 입력 프레임
            
        Returns:
            np.ndarray: 처리된 프레임
        """
        # 얼굴 탐지
        bboxes = self.detect_faces(frame)
        
        # 바운딩 박스 그리기
        processed_frame = self.draw_face_boxes(frame, bboxes)
        
        return processed_frame
    
    def get_face_count(self, frame: np.ndarray) -> int:
        """
        프레임에서 탐지된 얼굴 개수를 반환합니다.
        
        Args:
            frame (np.ndarray): 입력 프레임
            
        Returns:
            int: 탐지된 얼굴 개수
        """
        bboxes = self.detect_faces(frame)
        return len(bboxes)
    
    def close(self):
        """리소스를 해제합니다."""
        if hasattr(self, 'face_detection') and self.face_detection is not None:
            try:
                self.face_detection.close()
                self.face_detection = None
            except Exception as e:
                print(f"Face detection cleanup error: {e}")

# 전역 인스턴스 (싱글톤 패턴)
face_detection_service = FaceDetectionService()