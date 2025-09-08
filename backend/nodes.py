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
    total_points: int
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
         any(word in ai_response.lower() for word in ['move on', 'next step', 'let\'s', 'now', 'ready to begin', 'move to personal information']))):
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
           any(word in ai_response.lower() for word in ['move on', 'next step', 'let\'s', 'now', 'ready to begin', 'personal information collection complete', 'get your accounts all set up'])) or
          (current_node == "personal_info" and "personal information collection complete" in ai_response.lower()) or
          (current_node == "personal_info" and "get your accounts all set up" in ai_response.lower())):
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
    
    # Check for task completion and update node_tasks
    node_tasks = state["node_tasks"].copy()
    user_msg_lower = user_message.lower()
    
    # Task completion detection
    completion_phrases = [
        "watched", "completed", "finished", "done", "reviewed", "read", "studied", 
        "gone through", "looked at", "checked", "examined", "understood", "finished watching"
    ]
    
    # Welcome Video completion
    if any(phrase in user_msg_lower for phrase in completion_phrases) and \
       ("video" in user_msg_lower or "welcome video" in user_msg_lower):
        node_tasks["welcome_overview"]["welcome_video"] = True
    
    # Company Policies completion
    if any(phrase in user_msg_lower for phrase in completion_phrases) and \
       ("policy" in user_msg_lower or "policies" in user_msg_lower):
        node_tasks["welcome_overview"]["company_policies"] = True
    
    # Culture Quiz completion
    if any(phrase in user_msg_lower for phrase in completion_phrases) and \
       ("quiz" in user_msg_lower or "culture quiz" in user_msg_lower):
        node_tasks["welcome_overview"]["culture_quiz"] = True
    
    # Employee Perks completion (if mentioned)
    if any(phrase in user_msg_lower for phrase in completion_phrases) and \
       ("perks" in user_msg_lower or "benefits" in user_msg_lower):
        # Add employee_perks to node_tasks if not already there
        if "employee_perks" not in node_tasks["welcome_overview"]:
            node_tasks["welcome_overview"]["employee_perks"] = False
        node_tasks["welcome_overview"]["employee_perks"] = True
    
    return {
        **state,
        "chat_history": updated_chat_history,
        "current_node": "welcome_overview",
        "node_tasks": node_tasks
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
    
    # Check for personal info form completion
    node_tasks = state["node_tasks"].copy()
    user_msg_lower = user_message.lower()
    
    # Add personal_info section if not exists
    if "personal_info" not in node_tasks:
        node_tasks["personal_info"] = {
            "personal_info_form": False,
            "emergency_contact": False,
            "legal_forms": False
        }
    
    # Personal Info Form completion
    completion_phrases = [
        "submitted", "completed", "finished", "done", "filled out", "filled in",
        "provided", "entered", "gave", "supplied"
    ]
    
    if any(phrase in user_msg_lower for phrase in completion_phrases) and \
       ("form" in user_msg_lower or "information" in user_msg_lower or "personal info" in user_msg_lower):
        node_tasks["personal_info"]["personal_info_form"] = True
    
    return {
        **state,
        "chat_history": updated_chat_history,
        "current_node": "personal_info",
        "node_tasks": node_tasks
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
    
    # Check for account setup task completion
    node_tasks = state["node_tasks"].copy()
    user_msg_lower = user_message.lower()
    
    # Email setup completion
    if ("password" in user_msg_lower or "username" in user_msg_lower) and \
       ("set" in user_msg_lower or "updated" in user_msg_lower or "changed" in user_msg_lower):
        node_tasks["account_setup"]["email_setup"] = True
    
    # SAP access completion
    if ("sap" in user_msg_lower or "access" in user_msg_lower) and \
       ("granted" in user_msg_lower or "provided" in user_msg_lower or "set up" in user_msg_lower):
        node_tasks["account_setup"]["sap_access"] = True
    
    # Permissions completion
    if ("permissions" in user_msg_lower or "two-factor" in user_msg_lower or "2fa" in user_msg_lower) and \
       ("enabled" in user_msg_lower or "set up" in user_msg_lower or "configured" in user_msg_lower):
        node_tasks["account_setup"]["permissions"] = True
    
    return {
        **state,
        "chat_history": updated_chat_history,
        "current_node": "account_setup",
        "node_tasks": node_tasks
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
