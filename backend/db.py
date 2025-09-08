from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
from typing import Optional, List
from config import settings

# Database setup
Base = declarative_base()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database Models
class UserState(Base):
    __tablename__ = "user_states"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    current_node = Column(String, default="welcome_overview")
    total_points = Column(Integer, default=0)  # Total points earned
    node_tasks = Column(JSON, default=lambda: {
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
    })
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to chat messages
    chat_messages = relationship("ChatMessage", back_populates="user_state", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user_states.user_id"), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship back to user state
    user_state = relationship("UserState", back_populates="chat_messages")

# Database Functions
def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

# Database CRUD Functions
def get_user_state(db: Session, user_id: str) -> Optional[UserState]:
    """Get user state by user_id"""
    return db.query(UserState).filter(UserState.user_id == user_id).first()

def create_user_state(db: Session, user_id: str) -> UserState:
    """Create a new user state"""
    user_state = UserState(user_id=user_id)
    db.add(user_state)
    db.commit()
    db.refresh(user_state)
    return user_state

def get_chat_messages(db: Session, user_id: str) -> List[ChatMessage]:
    """Get all chat messages for a user"""
    return db.query(ChatMessage).filter(ChatMessage.user_id == user_id).order_by(ChatMessage.timestamp).all()

def save_chat_message(db: Session, user_id: str, role: str, content: str) -> ChatMessage:
    """Save a chat message"""
    message = ChatMessage(user_id=user_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def update_user_state_timestamp(db: Session, user_id: str):
    """Update user state timestamp"""
    user_state = get_user_state(db, user_id)
    if user_state:
        user_state.updated_at = datetime.utcnow()
        db.commit()

def calculate_points_for_task(task_name: str, user_message: str) -> int:
    """Calculate points based on task completion"""
    points_map = {
        'welcome_video': 300,
        'company_policies': 200,
        'culture_quiz': 250,
        'employee_perks': 150,
        'personal_info_form': 400,
        'account_setup': 500
    }
    
    # Check if user completed a specific task
    user_msg_lower = user_message.lower()
    
    if 'watched the video' in user_msg_lower or 'video' in user_msg_lower:
        return points_map.get('welcome_video', 0)
    elif 'reviewed all company policies' in user_msg_lower or 'policies' in user_msg_lower:
        return points_map.get('company_policies', 0)
    elif 'completed the culture quiz' in user_msg_lower or 'quiz' in user_msg_lower:
        return points_map.get('culture_quiz', 0)
    elif 'reviewed the employee perks' in user_msg_lower or 'perks' in user_msg_lower:
        return points_map.get('employee_perks', 0)
    elif 'submitted the personal information form' in user_msg_lower or 'personal information' in user_msg_lower:
        return points_map.get('personal_info_form', 0)
    elif 'account setup' in user_msg_lower and 'complete' in user_msg_lower:
        return points_map.get('account_setup', 0)
    
    return 0


def get_task_completion_summary(node_tasks: dict) -> dict:
    """Get summary of completed tasks"""
    summary = {
        "welcome_overview": {
            "completed": 0,
            "total": 0,
            "tasks": []
        },
        "personal_info": {
            "completed": 0,
            "total": 0,
            "tasks": []
        },
        "account_setup": {
            "completed": 0,
            "total": 0,
            "tasks": []
        }
    }
    
    for node_name, tasks in node_tasks.items():
        if node_name in summary:
            for task_name, completed in tasks.items():
                summary[node_name]["total"] += 1
                if completed:
                    summary[node_name]["completed"] += 1
                    summary[node_name]["tasks"].append(f"✅ {task_name}")
                else:
                    summary[node_name]["tasks"].append(f"⏳ {task_name}")
    
    return summary
