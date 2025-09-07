from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from config import settings
from langgraph_connection import LangGraphConnection
from database import get_db, create_tables
from models import UserState, ChatMessage

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
    current_policy: int
    node_tasks: Dict[str, Any]
    chat_messages: List[ChatMessageResponse]
    created_at: datetime
    updated_at: datetime

# Database functions
def get_user_state(db: Session, user_id: str) -> Optional[UserState]:
    return db.query(UserState).filter(UserState.user_id == user_id).first()

def create_user_state(db: Session, user_id: str) -> UserState:
    user_state = UserState(user_id=user_id)
    db.add(user_state)
    db.commit()
    db.refresh(user_state)
    return user_state

def get_chat_messages(db: Session, user_id: str) -> List[ChatMessage]:
    return db.query(ChatMessage).filter(ChatMessage.user_id == user_id).order_by(ChatMessage.timestamp).all()

def save_chat_message(db: Session, user_id: str, role: str, content: str) -> ChatMessage:
    message = ChatMessage(user_id=user_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def update_user_state_timestamp(db: Session, user_id: str):
    user_state = get_user_state(db, user_id)
    if user_state:
        user_state.updated_at = datetime.utcnow()
        db.commit()

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
        current_policy=user_state.current_policy,
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
        'current_policy': user_state.current_policy,
        'node_tasks': user_state.node_tasks,
        'chat_history': chat_history
    }
    
    # Save user message
    save_chat_message(db, user_id, "user", request.message)
    
    # Get agent response with database state
    result = hr_agent.process_chat(request.message, user_id, chat_history, db_state)
    
    # Handle restart case
    if result.get("restarted"):
        # Clear existing messages for restart
        db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
        db.commit()
        
        # Reset user state
        user_state.current_node = "welcome_overview"
        user_state.current_policy = 0
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
            "current_node": result["current_node"],
            "node_tasks": result["node_tasks"],
            "chat_history": []
        }
    
    # Update user state with new information
    user_state.current_node = result["current_node"]
    user_state.current_policy = result.get("current_policy", user_state.current_policy)
    user_state.node_tasks = result["node_tasks"]
    db.commit()
    
    # Save agent response
    save_chat_message(db, user_id, "assistant", result["agent_response"])
    
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
        "current_node": result["current_node"],
        "node_tasks": result["node_tasks"],
        "chat_history": result["chat_history"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)