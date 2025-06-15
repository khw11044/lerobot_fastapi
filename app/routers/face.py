from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from ..services.face_database_service import face_database_service
from ..services.face_recognition_service import face_recognition_service
from ..services.session_manager import session_manager

router = APIRouter()

# 요청 데이터 구조 정의
class UserRegistrationRequest(BaseModel):
    user_id: str

class DeleteUserRequest(BaseModel):
    user_id: str

@router.get("/status")
async def get_face_system_status():
    """얼굴 인식 시스템 상태를 반환합니다."""
    try:
        # 얼굴 인식 서비스 정보
        recognition_info = face_recognition_service.get_embedding_info()
        
        # 데이터베이스 정보
        db_info = face_database_service.get_database_info()
        
        # 세션 정보
        session_info = session_manager.get_session_stats()
        
        # 현재 얼굴 상태
        face_info = session_manager.get_current_face_info()
        
        return {
            "status": "active",
            "recognition_service": recognition_info,
            "database": db_info,
            "session": session_info,
            "current_face": face_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 조회 오류: {str(e)}")

@router.post("/register-current-face")
async def register_current_face(request: UserRegistrationRequest):
    """현재 화면에 있는 얼굴을 등록합니다."""
    try:
        user_id = request.user_id.strip()
        
        if not user_id:
            raise HTTPException(status_code=400, detail="사용자 ID가 비어있습니다.")
        
        if len(user_id) < 2:
            raise HTTPException(status_code=400, detail="사용자 ID는 2글자 이상이어야 합니다.")
        
        # 현재 얼굴 바운딩 박스 가져오기
        bbox = session_manager.get_face_bbox()
        
        if bbox is None:
            raise HTTPException(status_code=400, detail="현재 화면에 얼굴이 감지되지 않습니다.")
        
        # 등록 대기 상태로 설정
        session_manager.set_pending_registration(user_id, bbox)
        
        return {
            "status": "success",
            "message": f"사용자 '{user_id}' 얼굴 등록이 요청되었습니다.",
            "user_id": user_id,
            "next_step": "카메라에서 얼굴을 등록 중입니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"얼굴 등록 오류: {str(e)}")

@router.delete("/users/{user_id}")
async def delete_user_face(user_id: str):
    """특정 사용자의 얼굴 정보를 삭제합니다."""
    try:
        success = face_database_service.delete_user(user_id)
        
        if success:
            return {
                "status": "success",
                "message": f"사용자 '{user_id}' 얼굴 정보가 삭제되었습니다.",
                "user_id": user_id
            }
        else:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 삭제 오류: {str(e)}")

@router.get("/users")
async def get_all_users():
    """등록된 모든 사용자 목록을 반환합니다."""
    try:
        users = face_database_service.get_all_users()
        
        return {
            "status": "success",
            "total_users": len(users),
            "users": users
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 목록 조회 오류: {str(e)}")

@router.get("/current-session")
async def get_current_session():
    """현재 세션 정보를 반환합니다."""
    try:
        face_info = session_manager.get_current_face_info()
        current_user = session_manager.get_current_user_id()
        pending_registration = session_manager.get_pending_registration()
        
        return {
            "status": "success",
            "current_user": current_user,
            "face_detected": face_info["has_face"],
            "is_recognized": face_info["is_recognized"],
            "pending_registration": pending_registration is not None,
            "face_info": face_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 정보 조회 오류: {str(e)}")

@router.post("/reset-session")
async def reset_current_session():
    """현재 세션을 초기화합니다."""
    try:
        session_manager.reset_face_state()
        
        return {
            "status": "success",
            "message": "세션이 초기화되었습니다."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 초기화 오류: {str(e)}")

@router.delete("/database")
async def clear_face_database():
    """얼굴 데이터베이스를 초기화합니다."""
    try:
        success = face_database_service.clear_database()
        
        if success:
            # 세션도 함께 초기화
            session_manager.reset_face_state()
            
            return {
                "status": "success",
                "message": "얼굴 데이터베이스가 초기화되었습니다."
            }
        else:
            raise HTTPException(status_code=500, detail="데이터베이스 초기화에 실패했습니다.")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터베이스 초기화 오류: {str(e)}")

@router.get("/similarity-test/{user_id}")
async def test_similarity_with_current_face(user_id: str):
    """현재 얼굴과 특정 사용자의 유사도를 테스트합니다."""
    try:
        # 현재 얼굴 바운딩 박스 가져오기
        bbox = session_manager.get_face_bbox()
        
        if bbox is None:
            raise HTTPException(status_code=400, detail="현재 화면에 얼굴이 감지되지 않습니다.")
        
        # 등록된 사용자의 임베딩 가져오기
        stored_embedding = face_database_service.get_user_embedding(user_id)
        
        if stored_embedding is None:
            raise HTTPException(status_code=404, detail=f"사용자 '{user_id}'를 찾을 수 없습니다.")
        
        return {
            "status": "pending",
            "message": f"사용자 '{user_id}'와 현재 얼굴의 유사도 테스트가 요청되었습니다.",
            "user_id": user_id,
            "note": "다음 프레임에서 유사도가 계산됩니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"유사도 테스트 오류: {str(e)}")