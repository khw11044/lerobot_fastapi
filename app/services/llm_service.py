from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        # OpenAI ChatGPT 모델 초기화
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # 세션별 대화 히스토리 저장
        self.chat_histories: Dict[str, List] = {}
        
        # 시스템 메시지
        self.system_message = SystemMessage(
            content="당신은 친근하고 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 정확하고 유익한 답변을 제공해주세요."
        )
    
    async def generate_response(self, user_message: str, session_id: str = "default") -> str:
        """사용자 메시지에 대한 AI 응답을 생성합니다."""
        try:
            # 세션 히스토리 가져오기
            if session_id not in self.chat_histories:
                self.chat_histories[session_id] = [self.system_message]
            
            history = self.chat_histories[session_id]
            
            # 사용자 메시지 추가
            history.append(HumanMessage(content=user_message))
            
            # AI 응답 생성
            response = await self.llm.ainvoke(history)
            
            # AI 응답을 히스토리에 추가
            history.append(AIMessage(content=response.content))
            
            # 히스토리가 너무 길어지면 최근 20개 메시지만 유지
            if len(history) > 21:  # system message + 20개 메시지
                self.chat_histories[session_id] = [self.system_message] + history[-20:]
            
            return response.content
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다."
    
    def clear_history(self, session_id: str = "default"):
        """특정 세션의 대화 히스토리를 초기화합니다."""
        if session_id in self.chat_histories:
            self.chat_histories[session_id] = [self.system_message]
    
    def get_history(self, session_id: str = "default") -> List:
        """특정 세션의 대화 히스토리를 반환합니다."""
        return self.chat_histories.get(session_id, [self.system_message])