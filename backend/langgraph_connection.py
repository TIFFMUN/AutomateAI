from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END
from config import settings
from nodes import (
    process_message_node,
    handle_triggers_node,
    welcome_overview_node,
    personal_info_node,
    account_setup_node,
    route_to_node,
    get_default_tasks,
    OnboardingState
)

class LangGraphConnection:
    """LangGraph connection manager for SAP onboarding"""
    
    def __init__(self, openai_api_key: str):
        if not openai_api_key or openai_api_key.strip() == "":
            print("WARNING: OpenAI API key is not configured!")
            print("Please set OPENAI_API_KEY in your .env file")
        
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,
            openai_api_key=openai_api_key
        )
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(OnboardingState)
        
        # Add nodes
        workflow.add_node("welcome_overview", welcome_overview_node)
        workflow.add_node("personal_info", personal_info_node)
        workflow.add_node("account_setup", account_setup_node)
        workflow.add_node("process_message", process_message_node)
        workflow.add_node("handle_triggers", handle_triggers_node)
        
        # Add edges with conditional routing
        workflow.add_edge("process_message", "handle_triggers")
        workflow.add_conditional_edges(
            "handle_triggers",
            route_to_node,
            {
                "welcome_overview": "welcome_overview",
                "personal_info": "personal_info",
                "account_setup": "account_setup",
                "end": END
            }
        )
        workflow.add_edge("welcome_overview", END)
        workflow.add_edge("personal_info", END)
        workflow.add_edge("account_setup", END)
        
        # Set entry point
        workflow.set_entry_point("process_message")
        
        return workflow.compile()
    
    def _get_fallback_response(self, user_message: str, current_node: str, chat_history: list) -> str:
        """Intelligent fallback responses when LLM is unavailable"""
        user_msg_lower = user_message.lower()
        
        # Welcome Overview Node fallbacks
        if current_node == 'welcome_overview':
            return "I'm here to help with your SAP onboarding. What would you like to know?"
        
        # Personal Information Node fallbacks
        elif current_node == 'personal_info':
            return "Let's collect your personal information and complete required legal forms. Any questions about the information collection process before we begin?"
        
        # Account Setup Node fallbacks
        elif current_node == 'account_setup':
            return "Now let's set up your IT accounts and security. I'll assign you a 6-digit username and then we'll reset your password. Your assigned username is 123456. Let's start with resetting your password. What would you like your new password to be?"
        
        # Default response
        return "I'm here to help with your SAP onboarding. What would you like to know?"
    
    def process_chat(self, user_message: str, user_id: str, chat_history: list = None, db_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process chat message using LangGraph"""
        try:
            # Validate input
            if not user_message or not user_message.strip():
                raise ValueError("Empty message")
            
            # Clean input
            clean_message = user_message.strip()
            
            # Check for restart command first
            if clean_message.lower() in ['restart', 'reset', 'start over']:
                return {
                    "agent_response": "Welcome to SAP! Let's get you set up. I'll guide you step by step!",
                    "current_node": 'welcome_overview',
                    "current_policy": 0,
                    "node_tasks": get_default_tasks(),
                    "chat_history": [],
                    "restarted": True
                }
            
            # Use provided database state or default
            if db_state:
                current_node = db_state.get('current_node', 'welcome_overview')
                node_tasks = db_state.get('node_tasks', get_default_tasks())
                existing_chat_history = db_state.get('chat_history', [])
                current_policy = db_state.get('current_policy', 0)
            else:
                current_node = 'welcome_overview'
                node_tasks = get_default_tasks()
                existing_chat_history = []
                current_policy = 0
            
            # Handle LLM processing before graph execution
            ai_response = self._process_with_llm(clean_message, current_node, existing_chat_history)
            
            # Create initial state
            initial_state = OnboardingState(
                user_id=user_id,
                current_node=current_node,
                node_tasks=node_tasks,
                current_policy=current_policy,
                messages=[HumanMessage(content=clean_message), AIMessage(content=ai_response)],
                chat_history=existing_chat_history,
                agent_response=ai_response,
                restarted=False
            )
            
            # Run the graph
            result = self.graph.invoke(initial_state)
            
            # Return formatted response
            return {
                "agent_response": result["agent_response"],
                "current_node": result["current_node"],
                "current_policy": result["current_policy"],
                "node_tasks": result["node_tasks"],
                "chat_history": result["chat_history"],
                "restarted": result.get("restarted", False)
            }
            
        except Exception as e:
            # Return error response
            error_response = "Sorry, I encountered an error. Please try again."
            
            return {
                "agent_response": error_response,
                "current_node": 'welcome_overview',
                "current_policy": 0,
                "node_tasks": get_default_tasks(),
                "chat_history": [],
                "restarted": False
            }
    
    def _process_with_llm(self, user_message: str, current_node: str, chat_history: list) -> str:
        """Process message with LLM or fallback responses"""
        try:
            from prompts import get_system_prompt, get_user_prompt, format_chat_history, get_welcome_overview_prompt, get_personal_info_prompt, get_account_setup_prompt
            
            # Always use LLM processing to ensure proper question prompts are followed
            
            # Get current node prompt
            if current_node == 'welcome_overview':
                node_prompt = get_welcome_overview_prompt()
            elif current_node == 'personal_info':
                node_prompt = get_personal_info_prompt()
            elif current_node == 'account_setup':
                node_prompt = get_account_setup_prompt()
            else:
                node_prompt = ""
            
            # Create full prompt
            system_prompt = get_system_prompt()
            user_prompt = get_user_prompt(user_message)
            history_context = format_chat_history(chat_history)
            
            full_prompt = f"{system_prompt}\n\n{node_prompt}\n\nCurrent Node: {current_node}\n\n{history_context}{user_prompt}"
            
            # Get AI response
            response = self.llm.invoke([HumanMessage(content=full_prompt)])
            return response.content.strip()
            
        except Exception as e:
            print(f"LLM Error: {e}")  # Debug logging
            # Fallback to intelligent responses when LLM fails
            return self._get_fallback_response(user_message, current_node, chat_history)