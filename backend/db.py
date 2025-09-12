from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, create_engine, Boolean, DECIMAL, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session, joinedload
from datetime import datetime, date
from typing import Optional, List
from config import settings
from models.user import User

# Main Database setup
Base = declarative_base()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Performance Database setup
PerformanceBase = declarative_base()
performance_engine = create_engine(settings.PERFORMANCE_DATABASE_URL)
PerformanceSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=performance_engine)

# Database Models - User model moved to models/user.py to avoid conflicts

# PerformanceFeedback moved to performance database section below

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
    personal_goals = Column(JSON, default=lambda: {
        "goals": [
            {"id": 1, "name": "Training", "progress": 0, "target": 100},
            {"id": 2, "name": "Onboarding", "progress": 0, "target": 100}
        ]
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

# =============================================================================
# PERFORMANCE DATABASE MODELS
# =============================================================================

class PerformanceUser(PerformanceBase):
    __tablename__ = "performance_users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'employee' or 'manager'
    manager_id = Column(Integer, ForeignKey("performance_users.id"), nullable=True)
    department = Column(String, nullable=True)
    position = Column(String, nullable=True)
    hire_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manager = relationship("PerformanceUser", remote_side=[id], backref="direct_reports")
    feedbacks_given = relationship("PerformanceFeedback", foreign_keys="PerformanceFeedback.manager_id", back_populates="manager")
    feedbacks_received = relationship("PerformanceFeedback", foreign_keys="PerformanceFeedback.employee_id", back_populates="employee")

class PerformanceFeedback(PerformanceBase):
    __tablename__ = "performance_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("performance_users.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("performance_users.id"), nullable=False)
    feedback_text = Column(Text, nullable=False)
    
    # AI Analysis fields
    ai_summary = Column(Text, nullable=True)
    strengths = Column(Text, nullable=True)
    areas_for_improvement = Column(Text, nullable=True)
    next_steps = Column(Text, nullable=True)
    ai_quality_score = Column(DECIMAL(3, 2), nullable=True)
    
    # Rating system
    overall_rating = Column(Integer, nullable=True)  # 1-5 scale
    rating_breakdown = Column(JSON, nullable=True)  # Detailed ratings
    
    # Categorization
    feedback_categories = Column(JSON, nullable=True)  # ['technical', 'communication', 'leadership']
    tags = Column(JSON, nullable=True)  # ['positive', 'needs_improvement', 'urgent']
    
    # Review period
    review_period = Column(String(50), default='quarterly')
    review_year = Column(Integer, default=lambda: datetime.now().year)
    review_quarter = Column(Integer, default=lambda: (datetime.now().month - 1) // 3 + 1)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("PerformanceUser", foreign_keys=[employee_id], back_populates="feedbacks_received")
    manager = relationship("PerformanceUser", foreign_keys=[manager_id], back_populates="feedbacks_given")

class ProgressUpdate(PerformanceBase):
    __tablename__ = "progress_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    progress_text = Column(Text, nullable=False)
    updated_goals = Column(JSON, nullable=False)  # The goals after update
    ai_insight = Column(Text, nullable=True)  # AI-generated insight
    created_at = Column(DateTime, default=datetime.utcnow)

class PerformanceGoal(PerformanceBase):
    __tablename__ = "performance_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("performance_users.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("performance_users.id"), nullable=False)
    goal_title = Column(String(200), nullable=False)
    goal_description = Column(Text, nullable=True)
    goal_category = Column(String(50), nullable=True)
    target_value = Column(DECIMAL(10, 2), nullable=True)
    current_value = Column(DECIMAL(10, 2), default=0)
    unit_of_measure = Column(String(50), nullable=True)
    start_date = Column(Date, nullable=True)
    target_date = Column(Date, nullable=True)
    status = Column(String(20), default='active')  # active, completed, cancelled, overdue
    priority = Column(String(10), default='medium')  # low, medium, high
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("PerformanceUser", foreign_keys=[employee_id])
    manager = relationship("PerformanceUser", foreign_keys=[manager_id])

class PerformanceMetric(PerformanceBase):
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("performance_users.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(DECIMAL(10, 2), nullable=True)
    metric_unit = Column(String(50), nullable=True)
    measurement_date = Column(Date, default=date.today)
    source = Column(String(50), nullable=True)  # system, manual, survey
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("PerformanceUser")

# =============================================================================
# DATABASE FUNCTIONS
# =============================================================================
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

def get_performance_db():
    """Dependency to get performance database session"""
    db = PerformanceSessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_performance_tables():
    """Create all performance database tables"""
    PerformanceBase.metadata.create_all(bind=performance_engine)

# =============================================================================
# MAIN DATABASE CRUD FUNCTIONS
# =============================================================================
def get_user_state(db: Session, user_id: str) -> Optional[UserState]:
    """Get user state by user_id"""
    try:
        print(f"Querying user state for user_id: {user_id}")
        result = db.query(UserState).filter(UserState.user_id == user_id).first()
        print(f"User state query result: {result}")
        return result
    except Exception as e:
        print(f"Error getting user state: {e}")
        raise

def create_user_state(db: Session, user_id: str) -> UserState:
    """Create a new user state"""
    try:
        print(f"Creating user state for user_id: {user_id}")
        user_state = UserState(user_id=user_id)
        db.add(user_state)
        db.commit()
        db.refresh(user_state)
        print(f"User state created successfully: {user_state}")
        return user_state
    except Exception as e:
        print(f"Error creating user state: {e}")
        db.rollback()
        # If it's a unique constraint violation, try to get the existing user state
        if "duplicate key value violates unique constraint" in str(e):
            print(f"User state already exists for user_id: {user_id}, fetching existing one")
            existing_state = get_user_state(db, user_id)
            if existing_state:
                return existing_state
        raise

def get_chat_messages(db: Session, user_id: str) -> List[ChatMessage]:
    """Get all chat messages for a user"""
    try:
        print(f"Querying chat messages for user_id: {user_id}")
        result = db.query(ChatMessage).filter(ChatMessage.user_id == user_id).order_by(ChatMessage.timestamp).all()
        print(f"Found {len(result)} chat messages")
        return result
    except Exception as e:
        print(f"Error getting chat messages: {e}")
        raise

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

# Performance Feedback CRUD Functions (removed duplicates - using performance database functions)

# Personal Goals CRUD Functions
def update_user_personal_goals(db: Session, user_id: str, personal_goals: dict) -> Optional[UserState]:
    """Update user's personal goals"""
    user_state = get_user_state(db, user_id)
    if user_state:
        user_state.personal_goals = personal_goals
        user_state.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user_state)
    return user_state

def get_user_personal_goals(db: Session, user_id: str) -> dict:
    """Get user's personal goals"""
    user_state = get_user_state(db, user_id)
    if user_state and user_state.personal_goals:
        return user_state.personal_goals
    else:
        # Return default goals if none exist
        return {
            "goals": [
                {"id": 1, "name": "Training", "progress": 0, "target": 100},
                {"id": 2, "name": "Onboarding", "progress": 0, "target": 100}
            ]
        }

def calculate_goal_progress_from_onboarding(node_tasks: dict, current_node: str) -> dict:
    """Calculate goal progress based on onboarding completion"""
    goals = {
        "goals": [
            {"id": 1, "name": "Training", "progress": 0, "target": 100},
            {"id": 2, "name": "Onboarding", "progress": 0, "target": 100}
        ]
    }
    
    # Calculate onboarding progress based on completed tasks
    if "welcome_overview" in node_tasks:
        welcome_tasks = node_tasks["welcome_overview"]
        completed_welcome = sum(1 for task in welcome_tasks.values() if task)
        total_welcome = len(welcome_tasks)
        welcome_progress = (completed_welcome / total_welcome) * 100 if total_welcome > 0 else 0
        
        # Update onboarding goal based on welcome progress
        goals["goals"][1]["progress"] = min(welcome_progress, 100)
    
    # Calculate personal info progress
    if "personal_info" in node_tasks:
        personal_tasks = node_tasks["personal_info"]
        completed_personal = sum(1 for task in personal_tasks.values() if task)
        total_personal = len(personal_tasks)
        personal_progress = (completed_personal / total_personal) * 100 if total_personal > 0 else 0
        
        # Update onboarding goal (personal info is part of onboarding)
        current_onboarding_progress = goals["goals"][1]["progress"]
        goals["goals"][1]["progress"] = min((current_onboarding_progress + personal_progress) / 2, 100)
    
    # Calculate account setup progress
    if "account_setup" in node_tasks:
        account_tasks = node_tasks["account_setup"]
        completed_account = sum(1 for task in account_tasks.values() if task)
        total_account = len(account_tasks)
        account_progress = (completed_account / total_account) * 100 if total_account > 0 else 0
        
        # Update onboarding goal (account setup is part of onboarding)
        current_onboarding_progress = goals["goals"][1]["progress"]
        goals["goals"][1]["progress"] = min((current_onboarding_progress + account_progress) / 2, 100)
    
    # Set training progress based on current node (basic training starts after welcome)
    if current_node != "welcome_overview":
        goals["goals"][0]["progress"] = 20  # Basic training started
    
    return goals

# =============================================================================
# PERFORMANCE DATABASE CRUD FUNCTIONS
# =============================================================================

def create_performance_user(db: Session, user_id: str, name: str, email: str, role: str, manager_id: Optional[int] = None, 
                           department: Optional[str] = None, position: Optional[str] = None, hire_date: Optional[str] = None) -> PerformanceUser:
    """Create a new performance user"""
    # Convert hire_date string to date object if provided
    hire_date_obj = None
    if hire_date:
        from datetime import datetime
        try:
            hire_date_obj = datetime.strptime(hire_date, "%Y-%m-%d").date()
        except ValueError:
            print(f"Invalid hire_date format: {hire_date}")
    
    user = PerformanceUser(
        user_id=user_id, 
        name=name, 
        email=email, 
        role=role, 
        manager_id=manager_id,
        department=department,
        position=position,
        hire_date=hire_date_obj
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_performance_user_by_id(db: Session, user_id: str) -> Optional[PerformanceUser]:
    """Get performance user by user_id"""
    return db.query(PerformanceUser).filter(PerformanceUser.user_id == user_id).first()

def get_performance_user_by_db_id(db: Session, db_id: int) -> Optional[PerformanceUser]:
    """Get performance user by database ID"""
    return db.query(PerformanceUser).filter(PerformanceUser.id == db_id).first()

def get_performance_users_by_role(db: Session, role: str) -> List[PerformanceUser]:
    """Get all performance users by role"""
    return db.query(PerformanceUser).filter(PerformanceUser.role == role).all()

def get_performance_direct_reports(db: Session, manager_id: int) -> List[PerformanceUser]:
    """Get direct reports for a manager"""
    return db.query(PerformanceUser).filter(PerformanceUser.manager_id == manager_id).all()

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
    """Get all feedback for an employee"""
    return db.query(PerformanceFeedback).options(
        joinedload(PerformanceFeedback.employee),
        joinedload(PerformanceFeedback.manager)
    ).filter(PerformanceFeedback.employee_id == employee_id).order_by(PerformanceFeedback.created_at.desc()).all()

def get_performance_feedback_by_manager(db: Session, manager_id: int) -> List[PerformanceFeedback]:
    """Get all feedback given by a manager"""
    return db.query(PerformanceFeedback).options(
        joinedload(PerformanceFeedback.employee),
        joinedload(PerformanceFeedback.manager)
    ).filter(PerformanceFeedback.manager_id == manager_id).order_by(PerformanceFeedback.created_at.desc()).all()

def get_performance_feedback_by_id(db: Session, feedback_id: int) -> Optional[PerformanceFeedback]:
    """Get performance feedback by ID"""
    return db.query(PerformanceFeedback).filter(PerformanceFeedback.id == feedback_id).first()

def update_performance_feedback(db: Session, feedback_id: int, feedback_text: str) -> Optional[PerformanceFeedback]:
    """Update performance feedback text"""
    feedback = get_performance_feedback_by_id(db, feedback_id)
    if feedback:
        feedback.feedback_text = feedback_text
        feedback.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(feedback)
    return feedback

def update_performance_feedback_ai_analysis(db: Session, feedback_id: int, ai_summary: str = None, 
                                           strengths: str = None, areas_for_improvement: str = None, 
                                           next_steps: str = None, ai_quality_score: float = None) -> Optional[PerformanceFeedback]:
    """Update performance feedback with AI analysis"""
    feedback = get_performance_feedback_by_id(db, feedback_id)
    if feedback:
        if ai_summary is not None:
            feedback.ai_summary = ai_summary
        if strengths is not None:
            feedback.strengths = strengths
        if areas_for_improvement is not None:
            feedback.areas_for_improvement = areas_for_improvement
        if next_steps is not None:
            feedback.next_steps = next_steps
        if ai_quality_score is not None:
            feedback.ai_quality_score = ai_quality_score
        
        feedback.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(feedback)
    return feedback

def create_performance_goal(db: Session, employee_id: int, manager_id: int, goal_title: str, 
                           goal_description: str = None, goal_category: str = None) -> PerformanceGoal:
    """Create a new performance goal"""
    goal = PerformanceGoal(
        employee_id=employee_id,
        manager_id=manager_id,
        goal_title=goal_title,
        goal_description=goal_description,
        goal_category=goal_category
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

def get_performance_goals_by_employee(db: Session, employee_id: int) -> List[PerformanceGoal]:
    """Get all goals for an employee"""
    return db.query(PerformanceGoal).filter(PerformanceGoal.employee_id == employee_id).all()

def update_performance_goal_progress(db: Session, goal_id: int, current_value: float) -> Optional[PerformanceGoal]:
    """Update goal progress"""
    goal = db.query(PerformanceGoal).filter(PerformanceGoal.id == goal_id).first()
    if goal:
        goal.current_value = current_value
        goal.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(goal)
    return goal

def create_performance_metric(db: Session, employee_id: int, metric_name: str, 
                             metric_value: float = None, metric_unit: str = None, 
                             source: str = None) -> PerformanceMetric:
    """Create a new performance metric"""
    metric = PerformanceMetric(
        employee_id=employee_id,
        metric_name=metric_name,
        metric_value=metric_value,
        metric_unit=metric_unit,
        source=source
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric

def get_performance_metrics_by_employee(db: Session, employee_id: int) -> List[PerformanceMetric]:
    """Get all metrics for an employee"""
    return db.query(PerformanceMetric).filter(PerformanceMetric.employee_id == employee_id).all()

def get_performance_summary(db: Session, employee_id: int) -> dict:
    """Get comprehensive performance summary for an employee"""
    feedbacks = db.query(PerformanceFeedback).filter(PerformanceFeedback.employee_id == employee_id).all()
    goals = db.query(PerformanceGoal).filter(PerformanceGoal.employee_id == employee_id).all()
    
    total_feedbacks = len(feedbacks)
    avg_rating = sum(f.overall_rating for f in feedbacks if f.overall_rating) / len([f for f in feedbacks if f.overall_rating]) if feedbacks else 0
    completed_goals = len([g for g in goals if g.status == 'completed'])
    active_goals = len([g for g in goals if g.status == 'active'])
    
    return {
        'total_feedbacks': total_feedbacks,
        'average_rating': round(avg_rating, 2) if avg_rating else None,
        'completed_goals': completed_goals,
        'active_goals': active_goals,
        'total_goals': len(goals),
        'last_feedback_date': max([f.created_at for f in feedbacks]) if feedbacks else None,
        'recent_feedbacks': feedbacks[:3]
    }

# Progress Update Functions (Performance Database)
def save_progress_update_performance(db: Session, user_id: str, progress_text: str, updated_goals: list, ai_insight: str = None) -> ProgressUpdate:
    """Save a progress update to the performance database"""
    progress_update = ProgressUpdate(
        user_id=user_id,
        progress_text=progress_text,
        updated_goals=updated_goals,
        ai_insight=ai_insight
    )
    db.add(progress_update)
    db.commit()
    db.refresh(progress_update)
    return progress_update

def get_latest_progress_goals_performance(db: Session, user_id: str) -> list:
    """Get the latest progress goals for a user from performance database"""
    latest_update = db.query(ProgressUpdate).filter(
        ProgressUpdate.user_id == user_id
    ).order_by(ProgressUpdate.created_at.desc()).first()
    
    if latest_update:
        return latest_update.updated_goals
    else:
        # Return default goals if no progress updates found
        return [
            {"id": 1, "name": "Training", "progress": 0, "target": 100},
            {"id": 2, "name": "Onboarding", "progress": 0, "target": 100}
        ]

def get_progress_history_performance(db: Session, user_id: str, limit: int = 10) -> List[ProgressUpdate]:
    """Get progress update history for a user from performance database"""
    return db.query(ProgressUpdate).filter(
        ProgressUpdate.user_id == user_id
    ).order_by(ProgressUpdate.created_at.desc()).limit(limit).all()
