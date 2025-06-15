import chromadb
import numpy as np
import datetime
from typing import Optional, List, Tuple, Dict
import os

class FaceDatabaseService:
    def __init__(self, db_path='./faces'):
        """
        얼굴 데이터베이스 서비스 초기화
        
        Args:
            db_path (str): ChromaDB 저장 경로
        """
        # ChromaDB 클라이언트 초기화
        self.client = chromadb.PersistentClient(db_path)
        
        # 얼굴 데이터베이스 컬렉션 생성/가져오기
        self.collection = self.client.get_or_create_collection(
            name='face_embeddings',
            metadata={"hnsw:space": "cosine"}  # 코사인 유사도 사용
        )
        
        self.db_path = db_path
        print(f"얼굴 데이터베이스 초기화 완료: {db_path}")
    
    def add_face(self, user_id: str, embedding: np.ndarray) -> bool:
        """
        새로운 얼굴 임베딩을 데이터베이스에 추가합니다.
        
        Args:
            user_id (str): 사용자 ID
            embedding (np.ndarray): 얼굴 임베딩 벡터
            
        Returns:
            bool: 성공 시 True
        """
        try:
            # 현재 시간 추가
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 기존 사용자가 있다면 업데이트, 없다면 추가
            existing_user = self.get_user_embedding(user_id)
            
            if existing_user is not None:
                # 기존 사용자 업데이트
                self.collection.update(
                    ids=[user_id],
                    embeddings=[embedding.tolist()],
                    metadatas=[{
                        "user_id": user_id,
                        "created_at": current_time,
                        "updated_at": current_time
                    }]
                )
                print(f"사용자 {user_id} 얼굴 정보 업데이트됨")
            else:
                # 새 사용자 추가
                self.collection.add(
                    ids=[user_id],
                    embeddings=[embedding.tolist()],
                    metadatas=[{
                        "user_id": user_id,
                        "created_at": current_time,
                        "updated_at": current_time
                    }]
                )
                print(f"새 사용자 {user_id} 얼굴 정보 추가됨")
            
            return True
            
        except Exception as e:
            print(f"얼굴 추가 오류: {e}")
            return False
    
    def search_face(self, embedding: np.ndarray, top_k: int = 1) -> Optional[Tuple[str, float]]:
        """
        주어진 임베딩과 가장 유사한 얼굴을 검색합니다.
        
        Args:
            embedding (np.ndarray): 검색할 얼굴 임베딩
            top_k (int): 반환할 결과 개수
            
        Returns:
            Optional[Tuple[str, float]]: (사용자_ID, 유사도) 또는 None
        """
        try:
            # 등록된 얼굴이 없으면 None 반환
            if self.collection.count() == 0:
                return None
            
            # 유사한 얼굴 검색
            results = self.collection.query(
                query_embeddings=[embedding.tolist()],
                n_results=top_k,
                include=["distances", "metadatas"]
            )
            
            if not results["distances"] or not results["distances"][0]:
                return None
            
            # 거리를 유사도로 변환 (코사인 거리 -> 코사인 유사도)
            distance = results["distances"][0][0]
            similarity = 1.0 - distance  # 코사인 거리를 유사도로 변환
            
            user_id = results["metadatas"][0][0]["user_id"]
            
            print(f"얼굴 검색 결과: {user_id} (유사도: {similarity:.3f})")
            
            return user_id, similarity
            
        except Exception as e:
            print(f"얼굴 검색 오류: {e}")
            return None
    
    def get_user_embedding(self, user_id: str) -> Optional[np.ndarray]:
        """
        특정 사용자의 얼굴 임베딩을 가져옵니다.
        
        Args:
            user_id (str): 사용자 ID
            
        Returns:
            Optional[np.ndarray]: 얼굴 임베딩 또는 None
        """
        try:
            results = self.collection.get(
                ids=[user_id],
                include=["embeddings"]
            )
            
            if not results["embeddings"]:
                return None
            
            embedding = np.array(results["embeddings"][0])
            return embedding
            
        except Exception as e:
            print(f"사용자 임베딩 조회 오류: {e}")
            return None
    
    def delete_user(self, user_id: str) -> bool:
        """
        특정 사용자의 얼굴 정보를 삭제합니다.
        
        Args:
            user_id (str): 사용자 ID
            
        Returns:
            bool: 성공 시 True
        """
        try:
            self.collection.delete(ids=[user_id])
            print(f"사용자 {user_id} 얼굴 정보 삭제됨")
            return True
            
        except Exception as e:
            print(f"사용자 삭제 오류: {e}")
            return False
    
    def get_all_users(self) -> List[Dict]:
        """
        등록된 모든 사용자 정보를 가져옵니다.
        
        Returns:
            List[Dict]: 사용자 정보 리스트
        """
        try:
            results = self.collection.get(
                include=["metadatas"]
            )
            
            if not results["metadatas"]:
                return []
            
            users = []
            for metadata in results["metadatas"]:
                users.append({
                    "user_id": metadata["user_id"],
                    "created_at": metadata.get("created_at", "Unknown"),
                    "updated_at": metadata.get("updated_at", "Unknown")
                })
            
            return users
            
        except Exception as e:
            print(f"사용자 목록 조회 오류: {e}")
            return []
    
    def get_database_info(self) -> Dict:
        """
        데이터베이스 정보를 반환합니다.
        
        Returns:
            Dict: 데이터베이스 정보
        """
        try:
            user_count = self.collection.count()
            users = self.get_all_users()
            
            return {
                "database_path": self.db_path,
                "collection_name": self.collection.name,
                "total_users": user_count,
                "users": users,
                "similarity_metric": "cosine"
            }
            
        except Exception as e:
            print(f"데이터베이스 정보 조회 오류: {e}")
            return {
                "database_path": self.db_path,
                "error": str(e)
            }
    
    def clear_database(self) -> bool:
        """
        모든 얼굴 데이터를 삭제합니다.
        
        Returns:
            bool: 성공 시 True
        """
        try:
            # 모든 데이터 삭제
            all_ids = self.collection.get()["ids"]
            if all_ids:
                self.collection.delete(ids=all_ids)
            
            print("얼굴 데이터베이스가 초기화되었습니다.")
            return True
            
        except Exception as e:
            print(f"데이터베이스 초기화 오류: {e}")
            return False

# 전역 인스턴스
face_database_service = FaceDatabaseService()