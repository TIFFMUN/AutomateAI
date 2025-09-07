from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from datetime import datetime
import uuid
from config import settings
from prompts import get_system_prompt, get_user_prompt, format_chat_history

class SimpleHRAgent:
    """Simple HR Agent - clean and self-contained"""
    
    def __init__(self, gemini_api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=0.3,
            google_api_key=gemini_api_key
        )
    
    def chat(self, user_message: str, chat_history: list = None) -> Dict[str, Any]:
        """Process chat message"""
        try:
            # Validate input
            if not user_message or not user_message.strip():
                raise ValueError("Empty message")
            
            # Clean input
            clean_message = user_message.strip()
            
            # Create prompt
            system_prompt = get_system_prompt()
            user_prompt = get_user_prompt(clean_message)
            history_context = format_chat_history(chat_history or [])
            
            full_prompt = f"{system_prompt}\n\n{history_context}{user_prompt}"
            
            # Get AI response
            response = self.llm.invoke([HumanMessage(content=full_prompt)])
            ai_response = response.content.strip()
            
            # Create message objects
            user_msg = {
                "id": str(uuid.uuid4()),
                "type": "user",
                "text": clean_message,
                "timestamp": datetime.now().isoformat()
            }
            
            agent_msg = {
                "id": str(uuid.uuid4()),
                "type": "agent",
                "text": ai_response,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update chat history
            if chat_history is None:
                chat_history = []
            
            chat_history.extend([user_msg, agent_msg])
            
            return {
                "messages": chat_history,
                "agent_response": ai_response
            }
            
        except Exception as e:
            error_msg = {
                "id": str(uuid.uuid4()),
                "type": "agent",
                "text": "Sorry, I encountered an error. Please try again.",
                "timestamp": datetime.now().isoformat()
            }
            
            chat_history = chat_history or []
            chat_history.append(error_msg)
            
            return {
                "messages": chat_history,
                "agent_response": "Sorry, I encountered an error. Please try again."
            }
