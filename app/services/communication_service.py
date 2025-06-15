import socket
import threading
import time
from typing import Optional
from ..config import config

class CommunicationService:
    """로봇 제어 PC와의 UDP 통신을 담당하는 서비스"""
    
    def __init__(self):
        self.socket: Optional[socket.socket] = None
        self.is_connected = False
        self.robot_address = config.get_robot_address()
        
    def _create_socket(self) -> socket.socket:
        """UDP 소켓을 생성합니다."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(config.UDP_TIMEOUT)
            return sock
        except Exception as e:
            print(f"소켓 생성 오류: {e}")
            raise
    
    def send_message(self, message: str) -> bool:
        """로봇 제어 PC에 메시지를 전송합니다."""
        try:
            # 소켓 생성 (UDP는 연결 상태가 없으므로 매번 새로 생성)
            sock = self._create_socket()
            
            # 메시지를 UTF-8로 인코딩
            encoded_message = message.encode('utf-8')
            
            # 메시지 전송
            sock.sendto(encoded_message, self.robot_address)
            
            print(f"[UDP 전송 성공] {self.robot_address} -> {message[:100]}...")
            
            # 소켓 종료
            sock.close()
            
            return True
            
        except socket.timeout:
            print(f"[UDP 전송 실패] 타임아웃 - {self.robot_address}")
            return False
        except ConnectionRefusedError:
            print(f"[UDP 전송 실패] 연결 거부 - {self.robot_address}")
            return False
        except Exception as e:
            print(f"[UDP 전송 실패] 오류: {e}")
            return False
    
    def send_message_async(self, message: str):
        """비동기적으로 메시지를 전송합니다 (별도 스레드)."""
        def _send():
            self.send_message(message)
        
        thread = threading.Thread(target=_send, daemon=True)
        thread.start()
    
    def test_connection(self) -> bool:
        """로봇 제어 PC와의 연결을 테스트합니다."""
        test_message = "TEST_CONNECTION"
        return self.send_message(test_message)
    
    def get_status(self) -> dict:
        """통신 상태 정보를 반환합니다."""
        return {
            "robot_ip": self.robot_address[0],
            "robot_port": self.robot_address[1],
            "timeout": config.UDP_TIMEOUT,
            "last_test": time.time()
        }

# 전역 통신 서비스 인스턴스
communication_service = CommunicationService()