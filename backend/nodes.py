from typing import Dict, Any, List, TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from datetime import datetime
import uuid
from prompts import get_system_prompt, get_user_prompt, format_chat_history, get_welcome_overview_prompt, get_personal_info_prompt, get_account_setup_prompt

class OnboardingState(TypedDict):
    """State definition for the onboarding workflow"""
    user_id: str
    current_node: str
    node_tasks: Dict[str, Any]
    current_policy: int
    messages: Annotated[List[BaseMessage], "Chat messages"]
    chat_history: List[Dict[str, Any]]
    agent_response: str
    restarted: bool

def process_message_node(state: OnboardingState) -> OnboardingState:
    """Process incoming user message - LLM processing handled in connection layer"""
    return state  # Pass through since LLM processing is done before graph execution

def handle_triggers_node(state: OnboardingState) -> OnboardingState:
    """Handle button triggers and node transitions"""
    ai_response = state["agent_response"]
    current_node = state["current_node"]
    
    # Check for node transitions
    if ("→ personal_info" in ai_response or 
        (current_node == "welcome_overview" and 
         ("personal information" in ai_response.lower() or "personal info" in ai_response.lower()) and 
         any(word in ai_response.lower() for word in ['move on', 'next step', 'let\'s', 'now', 'ready to begin']))):
        # Clean up the response and update node
        clean_response = ai_response.replace("→ personal_info", "").strip()
        return {
            **state,
            "agent_response": clean_response,
            "current_node": "personal_info"
        }
    
    elif ("→ account_setup" in ai_response or 
          (current_node == "personal_info" and 
           ("account setup" in ai_response.lower() or "account set up" in ai_response.lower()) and 
           any(word in ai_response.lower() for word in ['move on', 'next step', 'let\'s', 'now', 'ready to begin', 'personal information collection complete'])) or
          (current_node == "personal_info" and "personal information collection complete" in ai_response.lower())):
        # Clean up the response and update node
        clean_response = ai_response.replace("→ account_setup", "").strip()
        return {
            **state,
            "agent_response": clean_response,
            "current_node": "account_setup"
        }
    
    # Frontend will detect button triggers and show appropriate buttons
    return state

def route_to_node(state: OnboardingState) -> str:
    """Route to the appropriate node based on current state"""
    current_node = state["current_node"]
    
    # Route to appropriate node
    if current_node == "personal_info":
        return "personal_info"
    elif current_node == "account_setup":
        return "account_setup"
    
    # Otherwise, stay in welcome overview
    return "welcome_overview"

def welcome_overview_node(state: OnboardingState) -> OnboardingState:
    """Handle Node 1: Welcome & Company Overview"""
    # Update chat history
    user_message = state["messages"][-2].content if len(state["messages"]) >= 2 else ""
    ai_response = state["agent_response"]
    
    updated_chat_history = state["chat_history"].copy()
    updated_chat_history.append({
        "id": str(uuid.uuid4()),
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })
    updated_chat_history.append({
        "id": str(uuid.uuid4()),
        "role": "agent",
        "content": ai_response,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        **state,
        "chat_history": updated_chat_history,
        "current_node": "welcome_overview"
    }

def personal_info_node(state: OnboardingState) -> OnboardingState:
    """Handle Node 2: Personal Information & Legal Forms"""
    # Update chat history
    user_message = state["messages"][-2].content if len(state["messages"]) >= 2 else ""
    ai_response = state["agent_response"]
    
    updated_chat_history = state["chat_history"].copy()
    updated_chat_history.append({
        "id": str(uuid.uuid4()),
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })
    updated_chat_history.append({
        "id": str(uuid.uuid4()),
        "role": "agent",
        "content": ai_response,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        **state,
        "chat_history": updated_chat_history,
        "current_node": "personal_info"
    }

def account_setup_node(state: OnboardingState) -> OnboardingState:
    """Handle Node 3: Account Setup"""
    # Update chat history
    user_message = state["messages"][-2].content if len(state["messages"]) >= 2 else ""
    ai_response = state["agent_response"]
    
    updated_chat_history = state["chat_history"].copy()
    updated_chat_history.append({
        "id": str(uuid.uuid4()),
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })
    updated_chat_history.append({
        "id": str(uuid.uuid4()),
        "role": "agent",
        "content": ai_response,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        **state,
        "chat_history": updated_chat_history,
        "current_node": "account_setup"
    }

def get_default_tasks() -> Dict[str, Any]:
    """Get default node tasks"""
    return {
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
    }

def get_current_node_prompt(current_node: str) -> str:
    """Get prompt for current node"""
    if current_node == 'welcome_overview':
        return get_welcome_overview_prompt()
    elif current_node == 'personal_info':
        return get_personal_info_prompt()
    elif current_node == 'account_setup':
        return get_account_setup_prompt()
    return ""
