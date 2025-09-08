from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from config import settings
from langgraph_connection import LangGraphConnection
from prompts import PERFORMANCE_FEEDBACK_ANALYSIS
from db import (
    get_db, create_tables, UserState, ChatMessage, User, PerformanceFeedback,
    get_user_state, create_user_state, get_chat_messages,
    save_chat_message, update_user_state_timestamp, calculate_points_for_task,
    get_user_by_user_id, create_user, get_user_direct_reports,
    create_performance_feedback, get_performance_feedback_by_employee,
    get_performance_feedback_by_manager, update_performance_feedback,
    update_performance_feedback_ai_analysis
)

app = FastAPI(title="SAP HR Assistant", version="1.0.0")

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HR Agent
hr_agent = LangGraphConnection(settings.OPENAI_API_KEY)

# Models
class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatMessageResponse(BaseModel):
    role: str
    content: str
    timestamp: datetime

class UserStateResponse(BaseModel):
    user_id: str
    current_node: str
    total_points: int
    node_tasks: Dict[str, Any]
    chat_messages: List[ChatMessageResponse]
    created_at: datetime
    updated_at: datetime

class UserResponse(BaseModel):
    id: int
    user_id: str
    name: str
    email: str
    role: str
    manager_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class PerformanceFeedbackResponse(BaseModel):
    id: int
    employee_id: int
    manager_id: int
    feedback_text: str
    ai_summary: Optional[str] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    next_steps: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    employee: Optional[UserResponse] = None
    manager: Optional[UserResponse] = None

class CreateFeedbackRequest(BaseModel):
    employee_id: int
    feedback_text: str

class UpdateFeedbackRequest(BaseModel):
    feedback_text: str

class GenerateAISummaryRequest(BaseModel):
    feedback_id: int

# All database functions are now in db.py

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "SAP HR Assistant API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/user/{user_id}/state")
def get_user_state_endpoint(user_id: str, db: Session = Depends(get_db)):
    user_state = get_user_state(db, user_id)
    if not user_state:
        user_state = create_user_state(db, user_id)
    
    chat_messages = get_chat_messages(db, user_id)
    chat_message_responses = [
        ChatMessageResponse(
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp
        ) for msg in chat_messages
    ]
    
    return UserStateResponse(
        user_id=user_state.user_id,
        current_node=user_state.current_node,
        total_points=user_state.total_points,
        node_tasks=user_state.node_tasks,
        chat_messages=chat_message_responses,
        created_at=user_state.created_at,
        updated_at=user_state.updated_at
    )

@app.post("/api/user/{user_id}/chat")
def handle_chat(user_id: str, request: ChatRequest, db: Session = Depends(get_db)):
    # Ensure user state exists
    user_state = get_user_state(db, user_id)
    if not user_state:
        user_state = create_user_state(db, user_id)
    
    # Get existing chat messages
    existing_messages = get_chat_messages(db, user_id)
    chat_history = [{"role": msg.role, "content": msg.content} for msg in existing_messages]
    
    # Prepare database state for agent
    db_state = {
        'current_node': user_state.current_node,
        'node_tasks': user_state.node_tasks,
        'chat_history': chat_history
    }
    
    # Save user message
    save_chat_message(db, user_id, "user", request.message)
    
    # Calculate points for task completion
    points_earned = calculate_points_for_task("", request.message)
    
    # Get agent response with database state
    result = hr_agent.process_chat(request.message, user_id, chat_history, db_state)
    
    # Handle restart case
    if result.get("restarted"):
        # Clear existing messages for restart
        db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
        db.commit()
        
        # Reset user state
        user_state.current_node = "welcome_overview"
        user_state.total_points = 0
        user_state.node_tasks = {
            "welcome_overview": {
                "welcome_video": False,
                "company_policies": False,
                "culture_quiz": False
            },
            "account_setup": {
                "email_setup": False,
                "sap_access": False,
                "permissions": False
            }
        }
        db.commit()
        
        # Save the restart message
        save_chat_message(db, user_id, "assistant", result["agent_response"])
        
        return {
            "agent_response": result["agent_response"],
            "agent_messages": result.get("agent_messages", [result["agent_response"]]),
            "current_node": result["current_node"],
            "node_tasks": result["node_tasks"],
            "chat_history": []
        }
    
    # Update user state with new information
    user_state.current_node = result["current_node"]
    user_state.node_tasks = result["node_tasks"]
    
    # Add points if earned
    if points_earned > 0:
        user_state.total_points += points_earned
    
    db.commit()
    
    # Save agent messages (multiple messages if split)
    agent_messages = result.get("agent_messages", [result["agent_response"]])
    for message in agent_messages:
        save_chat_message(db, user_id, "assistant", message)
    
    # Update user state timestamp
    update_user_state_timestamp(db, user_id)
    
    # Get updated chat messages
    updated_messages = get_chat_messages(db, user_id)
    chat_message_responses = [
        ChatMessageResponse(
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp
        ) for msg in updated_messages
    ]
    
    return {
        "messages": chat_message_responses,
        "agent_response": result["agent_response"],
        "agent_messages": agent_messages,
        "current_node": result["current_node"],
        "node_tasks": result["node_tasks"],
        "chat_history": result["chat_history"],
        "points_earned": points_earned,
        "total_points": user_state.total_points
    }

# Performance Feedback API Endpoints

@app.get("/api/user/{user_id}/profile")
def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """Get user profile by user_id"""
    user = get_user_by_user_id(db, user_id)
    if not user:
        return {"error": "User not found"}
    
    return UserResponse(
        id=user.id,
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        role=user.role,
        manager_id=user.manager_id,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

@app.get("/api/user/{user_id}/direct-reports")
def get_direct_reports(user_id: str, db: Session = Depends(get_db)):
    """Get direct reports for a manager"""
    user = get_user_by_user_id(db, user_id)
    if not user or user.role != "manager":
        return {"error": "User not found or not a manager"}
    
    direct_reports = get_user_direct_reports(db, user.id)
    return [
        UserResponse(
            id=report.id,
            user_id=report.user_id,
            name=report.name,
            email=report.email,
            role=report.role,
            manager_id=report.manager_id,
            created_at=report.created_at,
            updated_at=report.updated_at
        ) for report in direct_reports
    ]

@app.get("/api/user/{user_id}/feedback")
def get_user_feedback(user_id: str, db: Session = Depends(get_db)):
    """Get performance feedback for a user (as employee)"""
    user = get_user_by_user_id(db, user_id)
    if not user:
        return {"error": "User not found"}
    
    feedbacks = get_performance_feedback_by_employee(db, user.id)
    return [
        PerformanceFeedbackResponse(
            id=feedback.id,
            employee_id=feedback.employee_id,
            manager_id=feedback.manager_id,
            feedback_text=feedback.feedback_text,
            ai_summary=feedback.ai_summary,
            strengths=feedback.strengths,
            areas_for_improvement=feedback.areas_for_improvement,
            next_steps=feedback.next_steps,
            created_at=feedback.created_at,
            updated_at=feedback.updated_at,
            manager=UserResponse(
                id=feedback.manager.id,
                user_id=feedback.manager.user_id,
                name=feedback.manager.name,
                email=feedback.manager.email,
                role=feedback.manager.role,
                manager_id=feedback.manager.manager_id,
                created_at=feedback.manager.created_at,
                updated_at=feedback.manager.updated_at
            ) if feedback.manager else None
        ) for feedback in feedbacks
    ]

@app.get("/api/manager/{user_id}/feedback")
def get_manager_feedback(user_id: str, db: Session = Depends(get_db)):
    """Get performance feedback given by a manager"""
    user = get_user_by_user_id(db, user_id)
    if not user or user.role != "manager":
        return {"error": "User not found or not a manager"}
    
    feedbacks = get_performance_feedback_by_manager(db, user.id)
    return [
        PerformanceFeedbackResponse(
            id=feedback.id,
            employee_id=feedback.employee_id,
            manager_id=feedback.manager_id,
            feedback_text=feedback.feedback_text,
            ai_summary=feedback.ai_summary,
            strengths=feedback.strengths,
            areas_for_improvement=feedback.areas_for_improvement,
            next_steps=feedback.next_steps,
            created_at=feedback.created_at,
            updated_at=feedback.updated_at,
            employee=UserResponse(
                id=feedback.employee.id,
                user_id=feedback.employee.user_id,
                name=feedback.employee.name,
                email=feedback.employee.email,
                role=feedback.employee.role,
                manager_id=feedback.employee.manager_id,
                created_at=feedback.employee.created_at,
                updated_at=feedback.employee.updated_at
            ) if feedback.employee else None
        ) for feedback in feedbacks
    ]

@app.post("/api/manager/{user_id}/feedback")
def create_feedback(user_id: str, request: CreateFeedbackRequest, db: Session = Depends(get_db)):
    """Create new performance feedback"""
    manager = get_user_by_user_id(db, user_id)
    if not manager or manager.role != "manager":
        return {"error": "User not found or not a manager"}
    
    # Verify the employee exists and is a direct report
    employee = db.query(User).filter(User.id == request.employee_id).first()
    if not employee or employee.manager_id != manager.id:
        return {"error": "Employee not found or not a direct report"}
    
    feedback = create_performance_feedback(db, request.employee_id, manager.id, request.feedback_text)
    
    return PerformanceFeedbackResponse(
        id=feedback.id,
        employee_id=feedback.employee_id,
        manager_id=feedback.manager_id,
        feedback_text=feedback.feedback_text,
        ai_summary=feedback.ai_summary,
        strengths=feedback.strengths,
        areas_for_improvement=feedback.areas_for_improvement,
        next_steps=feedback.next_steps,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at
    )

@app.put("/api/feedback/{feedback_id}")
def update_feedback(feedback_id: int, request: UpdateFeedbackRequest, db: Session = Depends(get_db)):
    """Update performance feedback"""
    feedback = update_performance_feedback(db, feedback_id, request.feedback_text)
    if not feedback:
        return {"error": "Feedback not found"}
    
    return PerformanceFeedbackResponse(
        id=feedback.id,
        employee_id=feedback.employee_id,
        manager_id=feedback.manager_id,
        feedback_text=feedback.feedback_text,
        ai_summary=feedback.ai_summary,
        strengths=feedback.strengths,
        areas_for_improvement=feedback.areas_for_improvement,
        next_steps=feedback.next_steps,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at
    )

@app.post("/api/feedback/{feedback_id}/ai-summary")
def generate_ai_summary(feedback_id: int, db: Session = Depends(get_db)):
    """Generate AI summary for performance feedback"""
    feedback = db.query(PerformanceFeedback).filter(PerformanceFeedback.id == feedback_id).first()
    if not feedback:
        return {"error": "Feedback not found"}
    
    # Use the existing HR agent to generate AI analysis
    analysis_prompt = PERFORMANCE_FEEDBACK_ANALYSIS.format(feedback_text=feedback.feedback_text)
    
    try:
        result = hr_agent.process_chat(analysis_prompt, f"feedback_{feedback_id}", [], {})
        ai_response = result["agent_response"]
        
        # Parse the AI response (text format with sections)
        try:
            # Split the response into sections
            sections = ai_response.split('\n\n')
            summary = ""
            strengths = ""
            areas_for_improvement = ""
            next_steps = ""
            
            for section in sections:
                if section.startswith('SUMMARY:'):
                    summary = section.replace('SUMMARY:', '').strip()
                elif section.startswith('STRENGTHS:'):
                    strengths = section.replace('STRENGTHS:', '').strip()
                elif section.startswith('AREAS FOR IMPROVEMENT:'):
                    areas_for_improvement = section.replace('AREAS FOR IMPROVEMENT:', '').strip()
                elif section.startswith('NEXT STEPS:'):
                    next_steps = section.replace('NEXT STEPS:', '').strip()
            
            # If parsing fails, use the raw response
            if not summary:
                summary = ai_response
                strengths = "See feedback for details"
                areas_for_improvement = "See feedback for details"
                next_steps = "Review feedback with manager"
                
        except Exception:
            # If parsing fails completely, use the raw response
            summary = ai_response
            strengths = "See feedback for details"
            areas_for_improvement = "See feedback for details"
            next_steps = "Review feedback with manager"
        
        # Update the feedback with AI analysis
        updated_feedback = update_performance_feedback_ai_analysis(
            db, feedback_id, summary, strengths, areas_for_improvement, next_steps
        )
        
        return PerformanceFeedbackResponse(
            id=updated_feedback.id,
            employee_id=updated_feedback.employee_id,
            manager_id=updated_feedback.manager_id,
            feedback_text=updated_feedback.feedback_text,
            ai_summary=updated_feedback.ai_summary,
            strengths=updated_feedback.strengths,
            areas_for_improvement=updated_feedback.areas_for_improvement,
            next_steps=updated_feedback.next_steps,
            created_at=updated_feedback.created_at,
            updated_at=updated_feedback.updated_at
        )
        
    except Exception as e:
        return {"error": f"Failed to generate AI summary: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)