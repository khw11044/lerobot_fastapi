import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """애플리케이션 설정 관리"""
    
    # OpenAI 설정
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # 로봇 제어 PC 통신 설정
    ROBOT_PC_IP = os.getenv("ROBOT_PC_IP", "192.168.1.100")
    ROBOT_PC_PORT = int(os.getenv("ROBOT_PC_PORT", 8888))
    
    # UDP 통신 설정
    UDP_TIMEOUT = 5.0  # 초
    UDP_BUFFER_SIZE = 1024
    
    @classmethod
    def get_robot_address(cls):
        """로봇 제어 PC 주소 반환"""
        return (cls.ROBOT_PC_IP, cls.ROBOT_PC_PORT)

# 전역 설정 인스턴스
config = Config()