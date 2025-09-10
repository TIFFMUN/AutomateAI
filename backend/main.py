from fastapi import FastAPI, Depends 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime
from config import settings
from langgraph_connection import LangGraphConnection
from database import get_db
from db import (
    UserState, ChatMessage,
    get_user_state, create_user_state, get_chat_messages,
    save_chat_message, update_user_state_timestamp, calculate_points_for_task
)
from routers.auth import router as auth_router
import os
from dotenv import load_dotenv
from database import create_tables

load_dotenv()

app = FastAPI(
    title="AutomateAI API", 
    description="AI-powered employee development platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication router
app.include_router(auth_router, prefix="/api")

# Database-backed onboarding data (now persistent)

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

# All database functions are now in db.py

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "SAP HR Assistant API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Ensure core tables exist (users, etc.) without onboarding tables
@app.on_event("startup")
def on_startup() -> None:
    create_tables()

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
    print(f"Received chat request for user {user_id}: {request}")
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

@app.get("/api/health")
def api_health_check():
    return {"status": "healthy", "service": "AutomateAI API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
