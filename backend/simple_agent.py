from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from datetime import datetime
import uuid
import json
from config import settings
from prompts import get_system_prompt, get_user_prompt, format_chat_history, get_welcome_overview_prompt, get_account_setup_prompt

class SimpleHRAgent:
    """Simple HR Agent - clean and self-contained"""
    
    def __init__(self, gemini_api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=0.3,
            google_api_key=gemini_api_key
        )
    
    def get_default_state(self) -> Dict[str, Any]:
        """Get default user state"""
        return {
            'current_node': 'welcome_overview',
            'node_tasks': {
                'welcome_overview': {
                    'welcome_video': False,
                    'company_policies': False,
                    'culture_quiz': False
                },
                'account_setup': {
                    'email_setup': False,
                    'sap_access': False,
                    'permissions': False
                }
            },
            'current_policy': 0,  # Track which policy user is reviewing (0-3)
            'chat_history': [],
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_current_node_prompt(self, current_node: str) -> str:
        """Get prompt for current node"""
        if current_node == 'welcome_overview':
            return get_welcome_overview_prompt()
        elif current_node == 'account_setup':
            return get_account_setup_prompt()
        return ""
    
    def check_node_transition(self, ai_response: str, current_node: str) -> str:
        """Check if we should transition to next node"""
        if "→ account_setup" in ai_response:
            return 'account_setup'
        return current_node
    
    def chat(self, user_message: str, user_id: str, chat_history: list = None, db_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process chat message with database state persistence"""
        try:
            # Validate input
            if not user_message or not user_message.strip():
                raise ValueError("Empty message")
            
            # Clean input
            clean_message = user_message.strip()
            
            # Check for restart command
            if clean_message.lower() in ['restart', 'reset', 'start over']:
                return {
                    "agent_response": "Welcome to SAP! Let's start by introducing you to our culture and values.\n\n Take your time — I'll guide you step by step!",
                    "current_node": 'welcome_overview',
                    "node_tasks": self.get_default_state()['node_tasks'],
                    "chat_history": [],
                    "restarted": True
                }
            
            # Use provided database state or default
            if db_state:
                current_node = db_state.get('current_node', 'welcome_overview')
                node_tasks = db_state.get('node_tasks', self.get_default_state()['node_tasks'])
                existing_chat_history = db_state.get('chat_history', [])
            else:
                current_node = 'welcome_overview'
                node_tasks = self.get_default_state()['node_tasks']
                existing_chat_history = []
            
            # Get current node prompt
            node_prompt = self.get_current_node_prompt(current_node)
            
            # Create prompt
            system_prompt = get_system_prompt()
            user_prompt = get_user_prompt(clean_message)
            history_context = format_chat_history(existing_chat_history)
            
            full_prompt = f"{system_prompt}\n\n{node_prompt}\n\nCurrent Node: {current_node}\n\n{history_context}{user_prompt}"
            
            # Get AI response
            response = self.llm.invoke([HumanMessage(content=full_prompt)])
            ai_response = response.content.strip()
            
            
            # Handle policy acknowledgment
            if "reviewed" in clean_message.lower() and any(policy in clean_message.lower() for policy in ['company policies', 'policies']):
                ai_response = "Excellent! You've reviewed all company policies. Let's move on to the Culture Quiz. Click the button below to start: SHOW_CULTURE_QUIZ_BUTTON"
            
            # Handle policy review flow
            elif "company policies" in ai_response.lower() and "review" in ai_response.lower() and "button" in ai_response.lower():
                ai_response = "Great! Let's review SAP's Company Policies. Click the button below to open the policy viewer: SHOW_COMPANY_POLICIES_BUTTON"
            
            # Handle culture quiz flow
            elif "culture quiz" in ai_response.lower() and ("ready" in ai_response.lower() or "start" in ai_response.lower()):
                ai_response = "Great! Let's start the Culture Quiz. Click the button below to begin: SHOW_CULTURE_QUIZ_BUTTON"
            
            # Handle quiz completion
            elif "quiz" in clean_message.lower() and ("completed" in clean_message.lower() or "finished" in clean_message.lower()):
                ai_response = "Congratulations! You've completed the Culture Quiz. You're now ready to move on to Account Setup. Let's configure your accounts and permissions!"
            
            # Handle quiz skipping
            elif "quiz" in clean_message.lower() and "skipped" in clean_message.lower():
                ai_response = "I notice you skipped the Culture Quiz. Would you like to try it again, or shall we move on to Account Setup?"
            
            # Check for node transition
            new_current_node = self.check_node_transition(ai_response, current_node)
            
            # Create updated chat history
            updated_chat_history = existing_chat_history.copy()
            updated_chat_history.append({
                "id": str(uuid.uuid4()),
                "type": "user",
                "text": clean_message,
                "timestamp": datetime.now().isoformat()
            })
            updated_chat_history.append({
                "id": str(uuid.uuid4()),
                "type": "agent",
                "text": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "agent_response": ai_response,
                "current_node": new_current_node,
                "current_policy": db_state.get('current_policy', 0) if db_state else 0,
                "node_tasks": node_tasks,
                "chat_history": updated_chat_history
            }
            
        except Exception as e:
            # Return error response
            error_response = "Sorry, I encountered an error. Please try again."
            
            return {
                "agent_response": error_response,
                "current_node": 'welcome_overview',
                "node_tasks": self.get_default_state()['node_tasks'],
                "chat_history": []
            }
