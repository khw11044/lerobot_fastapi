from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.schema.output_parser import StrOutputParser
from typing import Dict, List
import os
from dotenv import load_dotenv

# 프롬프트와 데이터베이스 유틸리티 임포트
from utils.prompts.prompt import chat_prompt
from utils.databases.database import DatabaseManager

load_dotenv()

class LLMService:
    def __init__(self):
        # OpenAI ChatGPT 모델 초기화
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # 데이터베이스 매니저 초기화
        self.db_manager = DatabaseManager()
        
        # RAG 체인 초기화
        self.chain = self.init_chain()
        
        # 현재 세션 ID
        self.current_session_id = 'default'
    
    def init_chain(self):
        """RAG 체인을 초기화합니다."""
        rag_chat_chain = chat_prompt | self.llm | StrOutputParser()
        return rag_chat_chain
    
    def get_chat_history(self, session_id: str):
        """세션 기록을 가져오는 함수"""
        return SQLChatMessageHistory(
            table_name='chat_messages',
            session_id=session_id,
            connection="sqlite:///chat_history.db",
        )
    
    async def generate_response(self, user_message: str, session_id: str = "default") -> str:
        """사용자 메시지에 대한 AI 응답을 생성합니다."""
        try:
            # 세션 ID 업데이트
            if session_id:
                self.current_session_id = session_id
            
            print(f"[대화 세션ID]: {self.current_session_id}")
            
            # RunnableWithMessageHistory를 사용한 대화형 RAG 체인
            conversational_rag_chain = RunnableWithMessageHistory(      
                self.chain,                                 # 실행할 Runnable 객체
                self.get_chat_history,                      # 세션 기록을 가져오는 함수
                input_messages_key="input",                 # 입력 메시지의 키
                history_messages_key="chat_history",        # 기록 메시지의 키
            )
            
            # AI 응답 생성
            response = await conversational_rag_chain.ainvoke(
                {"input": user_message},
                config={"configurable": {"session_id": self.current_session_id}}
            )
            
            # 데이터베이스에 대화 내용 저장
            self.db_manager.save_conversation(
                session_id=self.current_session_id,
                user_message=user_message,
                ai_response=response
            )
            
            return response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            error_message = "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다."
            
            # 에러도 기록
            self.db_manager.save_conversation(
                session_id=self.current_session_id,
                user_message=user_message,
                ai_response=error_message
            )
            
            return error_message
    
    def clear_history(self, session_id: str = "default"):
        """특정 세션의 대화 히스토리를 초기화합니다."""
        try:
            # SQLChatMessageHistory 초기화
            chat_history = self.get_chat_history(session_id)
            chat_history.clear()
            
            # 커스텀 데이터베이스에서도 삭제
            self.db_manager.clear_session_history(session_id)
            
            print(f"Session {session_id} history cleared.")
        except Exception as e:
            print(f"Error clearing history: {e}")
    
    def get_history(self, session_id: str = "default", limit: int = 10):
        """특정 세션의 대화 히스토리를 반환합니다."""
        try:
            return self.db_manager.get_conversation_history(session_id, limit)
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
    
    def get_all_sessions(self):
        """모든 세션 정보를 반환합니다."""
        try:
            return self.db_manager.get_all_sessions()
        except Exception as e:
            print(f"Error getting sessions: {e}")
            return []