from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import json
from config import settings
from langgraph_connection import LangGraphConnection
from prompts import PERFORMANCE_FEEDBACK_ANALYSIS, PERFORMANCE_FEEDBACK_ANALYSIS_PROMPT, REAL_TIME_FEEDBACK_SUGGESTIONS_PROMPT
from langchain_core.messages import HumanMessage
from db import (
    get_db, create_tables, UserState, ChatMessage, User, PerformanceFeedback,
    get_user_state, create_user_state, get_chat_messages,
    save_chat_message, update_user_state_timestamp, calculate_points_for_task,
    get_user_by_user_id, create_user, get_user_direct_reports,
    create_performance_feedback, get_performance_feedback_by_employee,
    get_performance_feedback_by_manager, update_performance_feedback,
    update_performance_feedback_ai_analysis, update_user_personal_goals,
    get_user_personal_goals, calculate_goal_progress_from_onboarding,
    # Performance database imports
    get_performance_db, create_performance_tables, PerformanceUser, PerformanceGoal, ProgressUpdate,
    create_performance_user, create_performance_goal, get_performance_user_by_id,
    get_performance_summary, get_performance_direct_reports, get_performance_goals_by_employee,
    save_progress_update_performance, get_latest_progress_goals_performance, get_progress_history_performance
)

app = FastAPI(title="SAP HR Assistant", version="1.0.0")

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()
    create_performance_tables()
    
    # Create performance users if they don't exist
    try:
        db_gen = get_performance_db()
        db = next(db_gen)
        
        # Check if users already exist
        existing_users = db.query(PerformanceUser).count()
        if existing_users == 0:
            print("Creating performance users...")
            
            # Create manager (Alex Thompson)
            manager = create_performance_user(
                db=db,
                user_id="perf_manager001",
                name="Alex Thompson",
                email="alex.thompson@company.com",
                role="Manager"
            )
            print(f"Created manager: {manager.name} (ID: {manager.id})")
            
            # Create employees
            employees = [
                ("perf_employee001", "Sarah Chen", "sarah.chen@company.com", "Employee"),
                ("perf_employee002", "David Rodriguez", "david.rodriguez@company.com", "Employee"),
                ("perf_employee003", "Lisa Park", "lisa.park@company.com", "Employee")
            ]
            
            for user_id, name, email, role in employees:
                employee = create_performance_user(
                    db=db,
                    user_id=user_id,
                    name=name,
                    email=email,
                    role=role,
                    manager_id=manager.id  # Set Alex as their manager
                )
                print(f"Created employee: {employee.name} (ID: {employee.id})")
            
            print("Performance users created successfully!")
        else:
            print(f"Performance database already has {existing_users} users.")
        
        db.close()
    except Exception as e:
        print(f"Error creating performance users: {e}")

@app.get("/api/performance/debug/users")
def debug_performance_users(db: Session = Depends(get_performance_db)):
    """Debug endpoint to see what users exist in performance database"""
    try:
        from sqlalchemy import text
        
        # Get all columns in the table
        columns_result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'performance_users'
            ORDER BY ordinal_position
        """))
        
        columns = [row[0] for row in columns_result.fetchall()]
        
        # Get basic user data using only existing columns
        users_result = db.execute(text("""
            SELECT id, user_id, name, email, role, created_at
            FROM performance_users
        """))
        
        users = []
        for row in users_result.fetchall():
            users.append({
                "id": row[0],
                "user_id": row[1], 
                "name": row[2],
                "email": row[3],
                "role": row[4],
                "created_at": str(row[5]) if row[5] else None
            })
        
        return {
            "total_users": len(users),
            "existing_columns": columns,
            "users": users
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying users: {str(e)}")

@app.post("/api/performance/setup-manager-relationships")
def setup_manager_relationships(db: Session = Depends(get_performance_db)):
    """Set up manager-employee relationships"""
    try:
        from sqlalchemy import text
        
        # Set Alex Thompson (ID: 1) as manager for all employees (IDs: 2, 3, 4)
        db.execute(text("""
            UPDATE performance_users 
            SET manager_id = 1 
            WHERE id IN (2, 3, 4)
        """))
        
        db.commit()
        
        return {"message": "Successfully set up manager-employee relationships"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")

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

class FeedbackAnalysisRequest(BaseModel):
    feedback_text: str

class RealTimeFeedbackRequest(BaseModel):
    feedback_text: str

class ProgressUpdateRequest(BaseModel):
    progress_text: str
    current_goals: List[Dict[str, Any]]

class PersonalGoalsResponse(BaseModel):
    goals: List[Dict[str, Any]]

# Performance Testing Models
class PerformanceUserResponse(BaseModel):
    id: int
    user_id: str
    name: str
    email: str
    role: str
    manager_id: Optional[int] = None
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class PerformanceGoalResponse(BaseModel):
    id: int
    employee_id: int
    manager_id: int
    goal_title: str
    goal_description: Optional[str] = None
    goal_category: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit_of_measure: Optional[str] = None
    start_date: Optional[str] = None
    target_date: Optional[str] = None
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

class CreatePerformanceGoalRequest(BaseModel):
    employee_id: int
    goal_title: str
    goal_description: Optional[str] = None
    target_value: Optional[float] = None

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
    
    # Update personal goals based on onboarding progress
    updated_goals = calculate_goal_progress_from_onboarding(
        user_state.node_tasks, 
        user_state.current_node
    )
    user_state.personal_goals = updated_goals
    
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
def get_user_feedback(user_id: str, db: Session = Depends(get_performance_db)):
    """Get performance feedback for a user (as employee)"""
    user = get_performance_user_by_id(db, user_id)
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
def get_manager_feedback(user_id: str, db: Session = Depends(get_performance_db)):
    """Get performance feedback given by a manager"""
    user = get_performance_user_by_id(db, user_id)
    if not user or user.role != "Manager":
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
def create_feedback(user_id: str, request: CreateFeedbackRequest, db: Session = Depends(get_performance_db)):
    """Create new performance feedback"""
    manager = get_performance_user_by_id(db, user_id)
    if not manager or manager.role != "Manager":
        return {"error": "User not found or not a manager"}
    
    # Verify the employee exists and is a direct report
    employee = db.query(PerformanceUser).filter(PerformanceUser.id == request.employee_id).first()
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
        updated_at=feedback.updated_at,
        employee=UserResponse(
            id=employee.id,
            user_id=employee.user_id,
            name=employee.name,
            email=employee.email,
            role=employee.role,
            manager_id=employee.manager_id,
            created_at=employee.created_at,
            updated_at=employee.updated_at
        ),
        manager=UserResponse(
            id=manager.id,
            user_id=manager.user_id,
            name=manager.name,
            email=manager.email,
            role=manager.role,
            manager_id=manager.manager_id,
            created_at=manager.created_at,
            updated_at=manager.updated_at
        )
    )

@app.put("/api/feedback/{feedback_id}")
def update_feedback(feedback_id: int, request: UpdateFeedbackRequest, db: Session = Depends(get_performance_db)):
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
def generate_ai_summary(feedback_id: int, db: Session = Depends(get_performance_db)):
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

@app.post("/api/feedback/analyze")
def analyze_feedback(request: FeedbackAnalysisRequest, db: Session = Depends(get_performance_db)):
    """Analyze feedback text and provide AI-powered suggestions"""
    try:
        # Use the existing HR agent to analyze feedback
        analysis_prompt = PERFORMANCE_FEEDBACK_ANALYSIS_PROMPT.format(feedback_text=request.feedback_text)
        
        result = hr_agent.process_chat(analysis_prompt, f"feedback_analysis_{hash(request.feedback_text)}", [], {})
        ai_response = result["agent_response"]
        
        # Try to parse JSON response
        try:
            analysis_data = json.loads(ai_response)
            return analysis_data
        except json.JSONDecodeError:
            # If JSON parsing fails, return structured response
            return {
                "quality_score": 7,
                "tone_analysis": {
                    "overall_tone": "constructive",
                    "constructiveness_score": 7,
                    "balance_score": 6
                },
                "specificity_suggestions": [
                    "Add specific examples of performance",
                    "Include measurable outcomes",
                    "Provide concrete instances"
                ],
                "missing_areas": [
                    "Communication skills",
                    "Leadership development",
                    "Technical competencies"
                ],
                "actionability_suggestions": [
                    "Set specific goals for next quarter",
                    "Schedule regular check-ins",
                    "Provide training resources"
                ],
                "overall_recommendations": "Consider adding more specific examples and actionable next steps to make this feedback more effective."
            }
        
    except Exception as e:
        return {"error": f"Failed to analyze feedback: {str(e)}"}

@app.post("/api/feedback/realtime-suggestions")
def get_realtime_suggestions(request: RealTimeFeedbackRequest, db: Session = Depends(get_performance_db)):
    """Get real-time suggestions as manager types feedback"""
    try:
        # Use the existing HR agent for real-time suggestions
        suggestions_prompt = REAL_TIME_FEEDBACK_SUGGESTIONS_PROMPT.format(feedback_text=request.feedback_text)
        
        result = hr_agent.process_chat(suggestions_prompt, f"realtime_{hash(request.feedback_text)}", [], {})
        ai_response = result["agent_response"]
        
        # Try to parse JSON response
        try:
            suggestions_data = json.loads(ai_response)
            return suggestions_data
        except json.JSONDecodeError:
            # If JSON parsing fails, return default suggestions
            return {
                "live_suggestions": [
                    "Consider adding specific examples",
                    "Include measurable outcomes",
                    "Balance positive and improvement areas"
                ],
                "completeness_check": {
                    "has_specifics": len(request.feedback_text.split()) > 20,
                    "has_examples": "example" in request.feedback_text.lower() or "instance" in request.feedback_text.lower(),
                    "has_action_items": "next" in request.feedback_text.lower() or "goal" in request.feedback_text.lower(),
                    "covers_communication": "communication" in request.feedback_text.lower(),
                    "covers_leadership": "leadership" in request.feedback_text.lower() or "lead" in request.feedback_text.lower(),
                    "covers_technical": "technical" in request.feedback_text.lower() or "skill" in request.feedback_text.lower()
                },
                "next_suggestions": [
                    "Add specific examples of performance",
                    "Include actionable next steps"
                ]
            }
        
    except Exception as e:
        return {"error": f"Failed to get suggestions: {str(e)}"}

@app.post("/api/progress/update/{user_id}")
def update_progress(user_id: str, request: ProgressUpdateRequest, db: Session = Depends(get_performance_db)):
    """Update employee progress using GPT-4 with intelligent goal analysis"""
    try:
        # Create an intelligent progress analysis prompt for GPT-4
        smart_progress_prompt = f"""
You are an expert HR analyst and performance coach with deep understanding of employee development and goal tracking. Your task is to intelligently analyze employee progress updates and provide accurate goal assessments.

EMPLOYEE PROGRESS UPDATE: "{request.progress_text}"

CURRENT GOAL STATUS: {request.current_goals}

ANALYSIS FRAMEWORK:
As an expert analyst, you must:

1. **CONTEXTUAL UNDERSTANDING**: Analyze the progress text for:
   - Specific achievements mentioned
   - Skills developed or demonstrated
   - Tasks completed or milestones reached
   - Learning activities undertaken
   - Challenges overcome or areas of improvement

2. **GOAL MAPPING**: Intelligently map progress to the two available goals:
   - **TRAINING GOAL**: Any learning, skill development, course completion, certification, knowledge acquisition, professional development activities
   - **ONBOARDING GOAL**: Company-specific tasks, policy understanding, system access, orientation activities, company culture integration, administrative tasks

3. **PROGRESS CALCULATION**: Calculate realistic progress increases:
   - Small achievements: 5-15% increase
   - Moderate achievements: 15-30% increase  
   - Major milestones: 30-50% increase
   - Never exceed 100% or decrease progress
   - Consider current progress levels when calculating increases

4. **INTELLIGENT INSIGHTS**: Generate personalized, encouraging insights that:
   - Acknowledge specific achievements mentioned
   - Provide constructive feedback
   - Suggest next steps or areas for continued growth
   - Maintain an encouraging, professional tone

OUTPUT REQUIREMENTS:
You must respond with ONLY valid JSON in this exact format:

{{
  "goals": [
    {{"id": 1, "name": "Training", "progress": [calculated_progress], "target": 100}},
    {{"id": 2, "name": "Onboarding", "progress": [calculated_progress], "target": 100}}
  ],
  "chart_data": {{
    "type": "bar",
    "labels": ["Training", "Onboarding"],
    "datasets": [{{
      "label": "Progress %",
      "data": [training_progress, onboarding_progress],
      "backgroundColor": ["#3498db", "#2980b9"]
    }}]
  }},
  "insight": "[Personalized, encouraging insight based on the specific achievements mentioned]"
}}

CRITICAL: Output ONLY the JSON response, no additional text or explanations.
"""

        # Use GPT-4 directly for better analysis
        from langchain_openai import ChatOpenAI
        
        # Initialize GPT-4 model for performance analysis
        gpt4_model = ChatOpenAI(
            model=settings.PERFORMANCE_OPENAI_MODEL,  # Uses GPT-4
            temperature=0.2,  # Lower temperature for more consistent analysis
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Get AI response
        response = gpt4_model.invoke([HumanMessage(content=smart_progress_prompt)])
        ai_response = response.content
        
        # Try to parse JSON response
        try:
            progress_data = json.loads(ai_response)
            
            # Validate the response structure
            if "goals" in progress_data and "chart_data" in progress_data and "insight" in progress_data:
                # Save progress update to performance database
                try:
                    print(f"Attempting to save progress update for user: {user_id}")
                    print(f"Progress text: {request.progress_text}")
                    print(f"Updated goals: {progress_data['goals']}")
                    
                    saved_update = save_progress_update_performance(
                        db=db,
                        user_id=user_id,
                        progress_text=request.progress_text,
                        updated_goals=progress_data["goals"],
                        ai_insight=progress_data["insight"]
                    )
                    print(f"Successfully saved progress update with ID: {saved_update.id}")
                except Exception as db_error:
                    print(f"Database save failed: {db_error}")
                    import traceback
                    traceback.print_exc()
                    # Continue even if database save fails
                
                # Return the progress data - frontend will handle state updates
                return progress_data
            else:
                raise ValueError("Invalid response structure")
                
        except (json.JSONDecodeError, ValueError) as e:
            # If JSON parsing fails, return a structured response based on input analysis
            return {
                "goals": request.current_goals,  # Keep current goals as fallback
                "chart_data": {
                    "type": "bar",
                    "labels": [goal["name"] for goal in request.current_goals],
                    "datasets": [{
                        "label": "Progress %",
                        "data": [goal["progress"] for goal in request.current_goals],
                        "backgroundColor": ["#3498db", "#2980b9"]
                    }]
                },
                "insight": "Progress update received! Keep up the great work on your goals."
            }
        
    except Exception as e:
        print(f"AI API failed: {str(e)}")
        # Fallback: Simple progress calculation without AI
        try:
            # Simple progress calculation based on keywords
            progress_text_lower = request.progress_text.lower()
            updated_goals = request.current_goals.copy()
            
            # Check for training-related keywords
            training_keywords = ['course', 'training', 'learn', 'study', 'python', 'programming', 'skill']
            onboarding_keywords = ['onboard', 'company', 'policy', 'system', 'access', 'orientation']
            
            training_increase = 0
            onboarding_increase = 0
            
            for keyword in training_keywords:
                if keyword in progress_text_lower:
                    training_increase = 20  # 20% increase for training activities
                    break
            
            for keyword in onboarding_keywords:
                if keyword in progress_text_lower:
                    onboarding_increase = 15  # 15% increase for onboarding activities
                    break
            
            # Update goals
            for goal in updated_goals:
                if goal['name'] == 'Training':
                    goal['progress'] = min(100, goal['progress'] + training_increase)
                elif goal['name'] == 'Onboarding':
                    goal['progress'] = min(100, goal['progress'] + onboarding_increase)
            
            # Save progress update to database
            try:
                saved_update = save_progress_update_performance(
                    db=db,
                    user_id=user_id,
                    progress_text=request.progress_text,
                    updated_goals=updated_goals,
                    ai_insight="Progress updated successfully! Keep up the great work."
                )
                print(f"Successfully saved progress update with ID: {saved_update.id}")
            except Exception as db_error:
                print(f"Database save failed: {db_error}")
            
            return {
                "goals": updated_goals,
                "chart_data": {
                    "type": "bar",
                    "labels": [goal["name"] for goal in updated_goals],
                    "datasets": [{
                        "label": "Progress %",
                        "data": [goal["progress"] for goal in updated_goals],
                        "backgroundColor": ["#3498db", "#2980b9"]
                    }]
                },
                "insight": "Progress update received! Keep up the great work on your goals."
            }
        except Exception as fallback_error:
            return {"error": f"Failed to update progress: {str(fallback_error)}"}

@app.get("/api/performance/users/{user_id}/goals")
def get_performance_user_goals(user_id: str, db: Session = Depends(get_performance_db)):
    """Get the latest progress goals for a performance user"""
    try:
        goals = get_latest_progress_goals_performance(db, user_id)
        return {"goals": goals}
    except Exception as e:
        return {"error": f"Failed to get goals: {str(e)}"}

@app.get("/api/performance/users/{user_id}/latest-insight")
def get_latest_ai_insight(user_id: str, db: Session = Depends(get_performance_db)):
    """Get the latest AI insight for a performance user"""
    try:
        latest_update = db.query(ProgressUpdate).filter(
            ProgressUpdate.user_id == user_id
        ).order_by(ProgressUpdate.created_at.desc()).first()
        
        if latest_update and latest_update.ai_insight:
            return {"insight": latest_update.ai_insight}
        else:
            return {"insight": None}
    except Exception as e:
        return {"error": f"Failed to get insight: {str(e)}"}

@app.get("/api/user/{user_id}/goals")
def get_user_goals(user_id: str, db: Session = Depends(get_db)):
    """Get user's personal goals"""
    try:
        goals_data = get_user_personal_goals(db, user_id)
        return PersonalGoalsResponse(goals=goals_data["goals"])
    except Exception as e:
        return {"error": f"Failed to get goals: {str(e)}"}

@app.put("/api/user/{user_id}/goals")
def update_user_goals(user_id: str, goals_data: PersonalGoalsResponse, db: Session = Depends(get_db)):
    """Update user's personal goals"""
    try:
        updated_goals = {"goals": goals_data.goals}
        update_user_personal_goals(db, user_id, updated_goals)
        return PersonalGoalsResponse(goals=goals_data.goals)
    except Exception as e:
        return {"error": f"Failed to update goals: {str(e)}"}

@app.post("/api/user/{user_id}/goals/update-from-onboarding")
def update_goals_from_onboarding(user_id: str, db: Session = Depends(get_db)):
    """Update goals based on current onboarding progress"""
    try:
        user_state = get_user_state(db, user_id)
        if not user_state:
            return {"error": "User state not found"}
        
        # Calculate goals based on onboarding progress
        updated_goals = calculate_goal_progress_from_onboarding(
            user_state.node_tasks, 
            user_state.current_node
        )
        
        # Update goals in database
        update_user_personal_goals(db, user_id, updated_goals)
        
        return PersonalGoalsResponse(goals=updated_goals["goals"])
    except Exception as e:
        return {"error": f"Failed to update goals from onboarding: {str(e)}"}

# =============================================================================
# PERFORMANCE TESTING API ENDPOINTS
# =============================================================================

@app.get("/api/performance/users", response_model=List[PerformanceUserResponse])
def get_all_performance_users(db: Session = Depends(get_performance_db)):
    """Get all performance testing users"""
    users = db.query(PerformanceUser).all()
    return [
        PerformanceUserResponse(
            id=user.id,
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            role=user.role,
            manager_id=user.manager_id,
            department=user.department,
            position=user.position,
            hire_date=user.hire_date.isoformat() if user.hire_date else None,
            created_at=user.created_at,
            updated_at=user.updated_at
        ) for user in users
    ]

@app.get("/api/performance/users/{user_id}", response_model=PerformanceUserResponse)
def get_performance_user_by_id_endpoint(user_id: str, db: Session = Depends(get_performance_db)):
    """Get a specific performance user by user_id"""
    user = get_performance_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return PerformanceUserResponse(
        id=user.id,
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        role=user.role,
        manager_id=user.manager_id,
        department=user.department,
        position=user.position,
        hire_date=user.hire_date.isoformat() if user.hire_date else None,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

@app.get("/api/performance/users/{user_id}/profile", response_model=PerformanceUserResponse)
def get_performance_user_profile(user_id: str, db: Session = Depends(get_performance_db)):
    """Get performance user profile (alias for get_performance_user_by_id)"""
    return get_performance_user_by_id_endpoint(user_id, db)

@app.get("/api/performance/users/{user_id}/direct-reports", response_model=List[PerformanceUserResponse])
def get_performance_direct_reports_endpoint(user_id: str, db: Session = Depends(get_performance_db)):
    """Get direct reports for a performance manager"""
    user = get_performance_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role != "Manager":
        raise HTTPException(status_code=400, detail="User is not a manager")
    
    direct_reports = get_performance_direct_reports(db, user.id)
    return [
        PerformanceUserResponse(
            id=report.id,
            user_id=report.user_id,
            name=report.name,
            email=report.email,
            role=report.role,
            manager_id=report.manager_id,
            department=report.department,
            position=report.position,
            hire_date=report.hire_date.isoformat() if report.hire_date else None,
            created_at=report.created_at,
            updated_at=report.updated_at
        ) for report in direct_reports
    ]

@app.get("/api/performance/users/{user_id}/performance-goals", response_model=List[PerformanceGoalResponse])
def get_performance_user_performance_goals(user_id: str, db: Session = Depends(get_performance_db)):
    """Get performance goals for a user (different from progress goals)"""
    user = get_performance_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    goals = get_performance_goals_by_employee(db, user.id)
    return [
        PerformanceGoalResponse(
            id=goal.id,
            employee_id=goal.employee_id,
            manager_id=goal.manager_id,
            goal_title=goal.goal_title,
            goal_description=goal.goal_description,
            goal_category=goal.goal_category,
            target_value=float(goal.target_value) if goal.target_value else None,
            current_value=float(goal.current_value) if goal.current_value else None,
            unit_of_measure=goal.unit_of_measure,
            start_date=goal.start_date.isoformat() if goal.start_date else None,
            target_date=goal.target_date.isoformat() if goal.target_date else None,
            status=goal.status,
            priority=goal.priority,
            created_at=goal.created_at,
            updated_at=goal.updated_at
        ) for goal in goals
    ]

@app.post("/api/performance/managers/{user_id}/goals", response_model=PerformanceGoalResponse)
def create_performance_goal_endpoint(user_id: str, request: CreatePerformanceGoalRequest, db: Session = Depends(get_performance_db)):
    """Create new performance goal"""
    manager = get_performance_user_by_id(db, user_id)
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    if manager.role != "Manager":
        raise HTTPException(status_code=400, detail="User is not a manager")
    
    # Verify employee exists
    employee = db.query(PerformanceUser).filter(PerformanceUser.id == request.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    goal = create_performance_goal(
        db, request.employee_id, manager.id, request.goal_title, 
        request.goal_description, request.target_value
    )
    
    return PerformanceGoalResponse(
        id=goal.id,
        employee_id=goal.employee_id,
        manager_id=goal.manager_id,
        goal_title=goal.goal_title,
        goal_description=goal.goal_description,
        goal_category=goal.goal_category,
        target_value=float(goal.target_value) if goal.target_value else None,
        current_value=float(goal.current_value) if goal.current_value else None,
        unit_of_measure=goal.unit_of_measure,
        start_date=goal.start_date.isoformat() if goal.start_date else None,
        target_date=goal.target_date.isoformat() if goal.target_date else None,
        status=goal.status,
        priority=goal.priority,
        created_at=goal.created_at,
        updated_at=goal.updated_at
    )

@app.get("/api/performance/users/{user_id}/summary")
def get_performance_user_summary(user_id: str, db: Session = Depends(get_performance_db)):
    """Get comprehensive performance summary for a user"""
    user = get_performance_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    summary = get_performance_summary(db, user.id)
    return summary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)