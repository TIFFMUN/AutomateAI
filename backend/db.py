from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, create_engine, Boolean
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
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'employee' or 'manager'
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manager = relationship("User", remote_side=[id], backref="direct_reports")
    performance_feedbacks_given = relationship("PerformanceFeedback", foreign_keys="PerformanceFeedback.manager_id", back_populates="manager")
    performance_feedbacks_received = relationship("PerformanceFeedback", foreign_keys="PerformanceFeedback.employee_id", back_populates="employee")

class PerformanceFeedback(Base):
    __tablename__ = "performance_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    feedback_text = Column(Text, nullable=False)
    ai_summary = Column(Text, nullable=True)  # AI-generated summary
    strengths = Column(Text, nullable=True)  # AI-extracted strengths
    areas_for_improvement = Column(Text, nullable=True)  # AI-extracted improvement areas
    next_steps = Column(Text, nullable=True)  # AI-suggested next steps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("User", foreign_keys=[employee_id], back_populates="performance_feedbacks_received")
    manager = relationship("User", foreign_keys=[manager_id], back_populates="performance_feedbacks_given")

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

# User CRUD Functions
def get_user_by_user_id(db: Session, user_id: str) -> Optional[User]:
    """Get user by user_id"""
    return db.query(User).filter(User.user_id == user_id).first()

def create_user(db: Session, user_id: str, name: str, email: str, role: str, manager_id: Optional[int] = None) -> User:
    """Create a new user"""
    user = User(user_id=user_id, name=name, email=email, role=role, manager_id=manager_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_direct_reports(db: Session, manager_id: int) -> List[User]:
    """Get all direct reports for a manager"""
    return db.query(User).filter(User.manager_id == manager_id).all()

# Performance Feedback CRUD Functions
def create_performance_feedback(db: Session, employee_id: int, manager_id: int, feedback_text: str) -> PerformanceFeedback:
    """Create a new performance feedback"""
    feedback = PerformanceFeedback(
        employee_id=employee_id,
        manager_id=manager_id,
        feedback_text=feedback_text
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback

def get_performance_feedback_by_employee(db: Session, employee_id: int) -> List[PerformanceFeedback]:
    """Get all performance feedbacks for an employee"""
    return db.query(PerformanceFeedback).filter(PerformanceFeedback.employee_id == employee_id).order_by(PerformanceFeedback.created_at.desc()).all()

def get_performance_feedback_by_manager(db: Session, manager_id: int) -> List[PerformanceFeedback]:
    """Get all performance feedbacks given by a manager"""
    return db.query(PerformanceFeedback).filter(PerformanceFeedback.manager_id == manager_id).order_by(PerformanceFeedback.created_at.desc()).all()

def update_performance_feedback(db: Session, feedback_id: int, feedback_text: str) -> Optional[PerformanceFeedback]:
    """Update performance feedback text"""
    feedback = db.query(PerformanceFeedback).filter(PerformanceFeedback.id == feedback_id).first()
    if feedback:
        feedback.feedback_text = feedback_text
        feedback.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(feedback)
    return feedback

def update_performance_feedback_ai_analysis(db: Session, feedback_id: int, ai_summary: str, strengths: str, areas_for_improvement: str, next_steps: str) -> Optional[PerformanceFeedback]:
    """Update performance feedback with AI analysis"""
    feedback = db.query(PerformanceFeedback).filter(PerformanceFeedback.id == feedback_id).first()
    if feedback:
        feedback.ai_summary = ai_summary
        feedback.strengths = strengths
        feedback.areas_for_improvement = areas_for_improvement
        feedback.next_steps = next_steps
        feedback.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(feedback)
    return feedback
