import cv2
import numpy as np
from PIL import Image
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1


class FaceService:
    """
    얼굴을 인식하고 빨간색 바운딩 박스를 그리는 서비스.
    임베딩은 수행하지만 DB 저장 기능은 포함하지 않음.
    """
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.mtcnn = MTCNN(keep_all=True, device=self.device)
        self.resnet = InceptionResnetV1(pretrained='casia-webface').eval().to(self.device)

    def detect_faces(self, frame):
        """
        얼굴을 탐지하고 바운딩 박스를 반환합니다.
        """
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes, _ = self.mtcnn.detect(img_rgb)
        return boxes

    def get_embeddings(self, frame, boxes):
        """
        얼굴 영역을 임베딩 벡터로 변환합니다.
        (DB 저장 기능 없음)
        """
        embeddings = []
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            face = frame[y1:y2, x1:x2]
            if face.size == 0:
                continue
            face_rgb = Image.fromarray(cv2.cvtColor(face, cv2.COLOR_BGR2RGB))
            face_tensor = self.mtcnn(face_rgb)
            if face_tensor is not None:
                with torch.no_grad():
                    embedding = self.resnet(face_tensor.unsqueeze(0).to(self.device))
                    embeddings.append(embedding.cpu().numpy()[0])
        return embeddings

    def detect_and_draw(self, frame):
        """
        얼굴을 탐지하고 빨간색 박스를 그린 프레임을 반환합니다.
        """
        boxes = self.detect_faces(frame)
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        return frame


# 싱글톤 인스턴스 생성
face_service = FaceService()