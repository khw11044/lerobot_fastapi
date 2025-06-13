import sqlite3
import os
from typing import List, Tuple
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "chat_history.db"):
        """데이터베이스 매니저 초기화"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 및 테이블 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 채팅 기록 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 세션 테이블 생성 (사용자 정보)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_active DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def save_conversation(self, session_id: str, user_message: str, ai_response: str):
        """대화 내용을 데이터베이스에 저장"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 대화 내용 저장
            cursor.execute("""
                INSERT INTO chat_history (session_id, user_message, ai_response)
                VALUES (?, ?, ?)
            """, (session_id, user_message, ai_response))
            
            # 세션 정보 업데이트 또는 생성
            cursor.execute("""
                INSERT OR REPLACE INTO sessions (session_id, last_active)
                VALUES (?, CURRENT_TIMESTAMP)
            """, (session_id,))
            
            conn.commit()
    
    def get_conversation_history(self, session_id: str, limit: int = 20) -> List[Tuple[str, str, str]]:
        """특정 세션의 대화 기록을 가져옴"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_message, ai_response, timestamp
                FROM chat_history
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            
            return cursor.fetchall()
    
    def clear_session_history(self, session_id: str):
        """특정 세션의 대화 기록을 삭제"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM chat_history
                WHERE session_id = ?
            """, (session_id,))
            
            conn.commit()
    
    def get_all_sessions(self) -> List[Tuple[str, str, str]]:
        """모든 세션 정보를 가져옴"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, created_at, last_active
                FROM sessions
                ORDER BY last_active DESC
            """)
            
            return cursor.fetchall()
    
    def delete_old_sessions(self, days: int = 30):
        """오래된 세션을 삭제 (기본 30일)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM chat_history
                WHERE session_id IN (
                    SELECT session_id FROM sessions
                    WHERE last_active < datetime('now', '-{} days')
                )
            """.format(days))
            
            cursor.execute("""
                DELETE FROM sessions
                WHERE last_active < datetime('now', '-{} days')
            """.format(days))
            
            conn.commit()