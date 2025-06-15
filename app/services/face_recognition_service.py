import cv2
import numpy as np
import torch
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
from typing import Optional, Tuple, List
import time

class FaceRecognitionService:
    def __init__(self, similarity_threshold=0.6):
        """
        얼굴 인식 서비스 초기화
        
        Args:
            similarity_threshold (float): 얼굴 유사도 임계값 (0.0-1.0)
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # MTCNN for face detection and alignment
        self.mtcnn = MTCNN(
            keep_all=True,
            device=self.device,
            min_face_size=40,
            thresholds=[0.6, 0.7, 0.7]
        )
        
        # InceptionResnetV1 for face recognition
        self.resnet = InceptionResnetV1(
            pretrained='casia-webface'
        ).eval().to(self.device)
        
        self.similarity_threshold = similarity_threshold
        print(f"얼굴 인식 서비스 초기화 완료 (임계값: {similarity_threshold})")
    
    def extract_face_embedding(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        주어진 바운딩 박스에서 얼굴을 크롭하고 임베딩을 추출합니다.
        
        Args:
            image (np.ndarray): 입력 이미지 (BGR)
            bbox (Tuple): 바운딩 박스 좌표 (x1, y1, x2, y2)
            
        Returns:
            Optional[np.ndarray]: 얼굴 임베딩 벡터 (512차원) 또는 None
        """
        try:
            x1, y1, x2, y2 = bbox
            
            # 바운딩 박스 유효성 검사
            if x2 <= x1 or y2 <= y1:
                return None
            
            # 얼굴 영역 크롭
            face_crop = image[y1:y2, x1:x2]
            
            if face_crop.size == 0:
                return None
            
            # BGR을 RGB로 변환
            face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            face_pil = Image.fromarray(face_rgb)
            
            # MTCNN으로 얼굴 정렬 및 전처리
            face_tensor = self.mtcnn(face_pil)
            
            if face_tensor is None:
                return None
            
            # GPU/CPU로 이동
            face_tensor = face_tensor.to(self.device)
            
            # 임베딩 추출
            with torch.no_grad():
                embedding = self.resnet(face_tensor.unsqueeze(0))
                embedding = embedding.cpu().numpy().flatten()
            
            return embedding
            
        except Exception as e:
            print(f"얼굴 임베딩 추출 오류: {e}")
            return None
    
    def compare_embeddings(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        두 얼굴 임베딩 간의 유사도를 계산합니다.
        
        Args:
            embedding1 (np.ndarray): 첫 번째 얼굴 임베딩
            embedding2 (np.ndarray): 두 번째 얼굴 임베딩
            
        Returns:
            float: 유사도 점수 (0.0-1.0, 높을수록 유사)
        """
        try:
            # 코사인 유사도 계산
            embedding1_norm = embedding1 / np.linalg.norm(embedding1)
            embedding2_norm = embedding2 / np.linalg.norm(embedding2)
            
            similarity = np.dot(embedding1_norm, embedding2_norm)
            
            # -1~1 범위를 0~1로 변환
            similarity = (similarity + 1) / 2
            
            return float(similarity)
            
        except Exception as e:
            print(f"임베딩 비교 오류: {e}")
            return 0.0
    
    def is_same_person(self, embedding1: np.ndarray, embedding2: np.ndarray) -> bool:
        """
        두 얼굴 임베딩이 같은 사람인지 판단합니다.
        
        Args:
            embedding1 (np.ndarray): 첫 번째 얼굴 임베딩
            embedding2 (np.ndarray): 두 번째 얼굴 임베딩
            
        Returns:
            bool: 같은 사람이면 True
        """
        similarity = self.compare_embeddings(embedding1, embedding2)
        return similarity >= self.similarity_threshold
    
    def extract_face_from_frame(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        프레임에서 얼굴 영역만 추출합니다.
        
        Args:
            frame (np.ndarray): 입력 프레임
            bbox (Tuple): 바운딩 박스 좌표
            
        Returns:
            Optional[np.ndarray]: 크롭된 얼굴 이미지 또는 None
        """
        try:
            x1, y1, x2, y2 = bbox
            
            # 유효성 검사
            if x2 <= x1 or y2 <= y1:
                return None
            
            # 얼굴 영역 크롭
            face_crop = frame[y1:y2, x1:x2]
            
            if face_crop.size == 0:
                return None
            
            return face_crop
            
        except Exception as e:
            print(f"얼굴 크롭 오류: {e}")
            return None
    
    def get_embedding_info(self) -> dict:
        """
        임베딩 관련 정보를 반환합니다.
        
        Returns:
            dict: 임베딩 정보
        """
        return {
            "embedding_size": 512,
            "similarity_threshold": self.similarity_threshold,
            "device": str(self.device),
            "model": "InceptionResnetV1 (casia-webface)"
        }

# 전역 인스턴스
face_recognition_service = FaceRecognitionService(similarity_threshold=0.6)