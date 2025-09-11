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
import re

class LangGraphConnection:
    """LangGraph connection manager for SAP onboarding"""
    
    def __init__(self, openai_api_key: str):
        self.llm = None
        if not openai_api_key or openai_api_key.strip() == "":
            print("WARNING: OpenAI API key is not configured!")
            print("Please set OPENAI_API_KEY in your .env file")
        else:
            try:
                self.llm = ChatOpenAI(
                    model=settings.OPENAI_MODEL,
                    temperature=0.3,
                    openai_api_key=openai_api_key
                )
            except Exception as e:
                print(f"Failed to initialize OpenAI LLM, falling back. Error: {e}")
                self.llm = None
        self.graph = self._create_graph()
    
    def _split_message(self, message: str) -> List[str]:
        """Split long messages into multiple shorter messages for better conversation flow"""
        # Don't split messages that contain button triggers to avoid duplicates
        # BUT if the message is very long (300+ chars), we should split it for readability
        button_triggers = [
            'SHOW_VIDEO_BUTTON',
            'SHOW_COMPANY_POLICIES_BUTTON', 
            'SHOW_CULTURE_QUIZ_BUTTON',
            'SHOW_EMPLOYEE_PERKS_BUTTON',
            'SHOW_PERSONAL_INFO_FORM_BUTTON'
        ]
        
        # Only keep button trigger messages intact if they're reasonably short
        if any(trigger in message for trigger in button_triggers) and len(message) <= 250:
            return [message]  # Don't split short button trigger messages
        
        # Don't split short messages (up to 200 characters)
        if len(message) <= 200:
            return [message]
        
        # Split on natural break points (sentences)
        sentences = re.split(r'(?<=[.!?])\s+', message)
        
        if len(sentences) <= 2:  # Don't split if only 1-2 sentences
            return [message]
        
        # Group sentences into chunks, aiming for 150-200 characters per chunk
        chunks = []
        current_chunk = []
        
        for sentence in sentences:
            current_chunk.append(sentence)
            current_text = ' '.join(current_chunk)
            
            # Create a chunk if it's getting long (200+ chars) or we have 2+ sentences
            if len(current_text) > 200 or len(current_chunk) >= 2:
                chunks.append(current_text)
                current_chunk = []
        
        # Add any remaining sentences
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        # If we have too many chunks (more than 3), recombine some
        if len(chunks) > 3:
            combined_chunks = []
            for i in range(0, len(chunks), 2):
                if i + 1 < len(chunks):
                    combined_chunks.append(chunks[i] + ' ' + chunks[i + 1])
                else:
                    combined_chunks.append(chunks[i])
            chunks = combined_chunks
        
        return chunks
    
    def _format_task_status(self, current_node: str, node_tasks: Dict[str, Any] = None) -> str:
        """Format task completion status for LLM context"""
        if not node_tasks:
            return "TASK STATUS: No tasks completed yet."
        
        status_lines = ["TASK COMPLETION STATUS:"]
        
        # Welcome Overview tasks
        if current_node == "welcome_overview" and "welcome_overview" in node_tasks:
            welcome_tasks = node_tasks["welcome_overview"]
            status_lines.append("- Welcome Overview:")
            status_lines.append(f"  * Welcome Video: {'✅ COMPLETED' if welcome_tasks.get('welcome_video', False) else '❌ NOT COMPLETED'}")
            status_lines.append(f"  * Company Policies: {'✅ COMPLETED' if welcome_tasks.get('company_policies', False) else '❌ NOT COMPLETED'}")
            status_lines.append(f"  * Employee Perks: {'✅ COMPLETED' if welcome_tasks.get('employee_perks', False) else '❌ NOT COMPLETED'}")
            status_lines.append(f"  * Culture Quiz: {'✅ COMPLETED' if welcome_tasks.get('culture_quiz', False) else '❌ NOT COMPLETED'}")
        
        # Personal Info tasks
        elif current_node == "personal_info" and "personal_info" in node_tasks:
            personal_tasks = node_tasks["personal_info"]
            status_lines.append("- Personal Information:")
            status_lines.append(f"  * Personal Info Form: {'✅ COMPLETED' if personal_tasks.get('personal_info_form', False) else '❌ NOT COMPLETED'}")
            status_lines.append(f"  * Emergency Contact: {'✅ COMPLETED' if personal_tasks.get('emergency_contact', False) else '❌ NOT COMPLETED'}")
            status_lines.append(f"  * Legal Forms: {'✅ COMPLETED' if personal_tasks.get('legal_forms', False) else '❌ NOT COMPLETED'}")
        
        # Account Setup tasks
        elif current_node == "account_setup" and "account_setup" in node_tasks:
            account_tasks = node_tasks["account_setup"]
            status_lines.append("- Account Setup:")
            status_lines.append(f"  * Email Setup: {'✅ COMPLETED' if account_tasks.get('email_setup', False) else '❌ NOT COMPLETED'}")
            status_lines.append(f"  * SAP Access: {'✅ COMPLETED' if account_tasks.get('sap_access', False) else '❌ NOT COMPLETED'}")
            status_lines.append(f"  * Permissions: {'✅ COMPLETED' if account_tasks.get('permissions', False) else '❌ NOT COMPLETED'}")
        
        status_lines.append("\nIMPORTANT: Only suggest tasks that are NOT COMPLETED. Do not ask users to repeat completed tasks.")
        
        return "\n".join(status_lines)
    
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
                    "agent_messages": ["Welcome to SAP! Let's get you set up. I'll guide you step by step!"],
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
            else:
                current_node = 'welcome_overview'
                node_tasks = get_default_tasks()
                existing_chat_history = []
            
            # If already completed, provide completion responses
            if current_node == "onboarding_complete":
                return {
                    "agent_response": "Thank you! Your onboarding is complete. If you have any questions or need assistance, feel free to reach out. Welcome to the SAP team!",
                    "agent_messages": ["Thank you! Your onboarding is complete. If you have any questions or need assistance, feel free to reach out. Welcome to the SAP team!"],
                    "current_node": "onboarding_complete",
                    "node_tasks": node_tasks,
                    "chat_history": existing_chat_history,
                    "restarted": False
                }
            
            # Handle LLM processing before graph execution
            ai_response = self._process_with_llm(clean_message, current_node, existing_chat_history, node_tasks)
            
            # Check for onboarding completion
            onboarding_complete = "ONBOARDING_COMPLETE" in ai_response
            if onboarding_complete:
                # Clean up the completion signal from the response
                ai_response = ai_response.replace("ONBOARDING_COMPLETE", "").strip()
                # Split the completion message
                split_messages = self._split_message(ai_response)
                # Return completion response directly without running the graph
                return {
                    "agent_response": ai_response,
                    "agent_messages": split_messages,
                    "current_node": "onboarding_complete",
                    "node_tasks": node_tasks,
                    "chat_history": existing_chat_history,
                    "restarted": False
                }
            
            # Create initial state
            initial_state = OnboardingState(
                user_id=user_id,
                current_node=current_node,
                node_tasks=node_tasks,
                total_points=0,
                messages=[HumanMessage(content=clean_message), AIMessage(content=ai_response)],
                chat_history=existing_chat_history,
                agent_response=ai_response,
                restarted=False
            )
            
            # Run the graph
            result = self.graph.invoke(initial_state)
            
            # Split the response into multiple messages
            split_messages = self._split_message(result["agent_response"])
            
            # Return formatted response
            return {
                "agent_response": result["agent_response"],
                "agent_messages": split_messages,
                "current_node": result["current_node"],
                "node_tasks": result["node_tasks"],
                "chat_history": result["chat_history"],
                "restarted": result.get("restarted", False)
            }
            
        except Exception as e:
            # Return error response
            error_response = "Sorry, I encountered an error. Please try again."
            
            return {
                "agent_response": error_response,
                "agent_messages": [error_response],
                "current_node": 'welcome_overview',
                "node_tasks": get_default_tasks(),
                "chat_history": [],
                "restarted": False
            }
    
    def _process_with_llm(self, user_message: str, current_node: str, chat_history: list, node_tasks: Dict[str, Any] = None) -> str:
        """Process message with LLM or fallback responses"""
        if self.llm is None:
            return self._get_fallback_response(user_message, current_node, chat_history)
        try:
            from prompts import get_system_prompt, get_user_prompt, format_chat_history, get_welcome_overview_prompt, get_personal_info_prompt, get_account_setup_prompt
            
            # Get current node prompt
            if current_node == 'welcome_overview':
                node_prompt = get_welcome_overview_prompt()
            elif current_node == 'personal_info':
                node_prompt = get_personal_info_prompt()
            elif current_node == 'account_setup':
                node_prompt = get_account_setup_prompt()
            else:
                node_prompt = ""
            
            # Create task completion status context
            task_status = self._format_task_status(current_node, node_tasks)
            
            # Create full prompt with limited history (last 3 messages only)
            system_prompt = get_system_prompt()
            user_prompt = get_user_prompt(user_message)
            
            # Only include recent history to avoid message combination
            recent_history = chat_history[-3:] if len(chat_history) > 3 else chat_history
            history_context = format_chat_history(recent_history)
            
            full_prompt = f"{system_prompt}\n\n{node_prompt}\n\nCurrent Node: {current_node}\n\n{task_status}\n\n{history_context}{user_prompt}"
            
            # Get AI response
            response = self.llm.invoke([HumanMessage(content=full_prompt)])
            return response.content.strip()
            
        except Exception as e:
            print(f"LLM Error: {e}")  # Debug logging
            # Fallback to intelligent responses when LLM fails
            return self._get_fallback_response(user_message, current_node, chat_history)