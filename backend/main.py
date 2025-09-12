from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from config import settings
from langgraph_connection import LangGraphConnection
from prompts import PERFORMANCE_FEEDBACK_ANALYSIS, PERFORMANCE_FEEDBACK_ANALYSIS_PROMPT, REAL_TIME_FEEDBACK_SUGGESTIONS_PROMPT
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
    get_performance_db, create_performance_tables, PerformanceUser, PerformanceGoal,
    create_performance_user, create_performance_goal, get_performance_user_by_id,
    get_performance_summary, get_performance_direct_reports, get_performance_goals_by_employee
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

@app.post("/api/feedback/analyze")
def analyze_feedback(request: FeedbackAnalysisRequest, db: Session = Depends(get_db)):
    """Analyze feedback text and provide AI-powered suggestions"""
    try:
        # Use the existing HR agent to analyze feedback
        analysis_prompt = PERFORMANCE_FEEDBACK_ANALYSIS_PROMPT.format(feedback_text=request.feedback_text)
        
        result = hr_agent.process_chat(analysis_prompt, f"feedback_analysis_{hash(request.feedback_text)}", [], {})
        ai_response = result["agent_response"]
        
        # Try to parse JSON response
        try:
            import json
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
def get_realtime_suggestions(request: RealTimeFeedbackRequest, db: Session = Depends(get_db)):
    """Get real-time suggestions as manager types feedback"""
    try:
        # Use the existing HR agent for real-time suggestions
        suggestions_prompt = REAL_TIME_FEEDBACK_SUGGESTIONS_PROMPT.format(feedback_text=request.feedback_text)
        
        result = hr_agent.process_chat(suggestions_prompt, f"realtime_{hash(request.feedback_text)}", [], {})
        ai_response = result["agent_response"]
        
        # Try to parse JSON response
        try:
            import json
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

@app.post("/api/progress/update")
def update_progress(request: ProgressUpdateRequest, db: Session = Depends(get_db)):
    """Update employee progress using LangGraph chain-of-experts"""
    try:
        # Get user state to understand current onboarding progress
        user_state = get_user_state(db, "test_user")  # Using test_user for now
        onboarding_context = ""
        if user_state:
            onboarding_context = f"""
Current Onboarding Status:
- Current Node: {user_state.current_node}
- Node Tasks: {user_state.node_tasks}
- Total Points: {user_state.total_points}
"""

        # Create the chain-of-experts prompt
        chain_of_experts_prompt = f"""
You are a Chain of Experts system for processing employee progress updates. You must output ONLY valid JSON in the exact format specified below.

Input: "{request.progress_text}"
Current Goals: {request.current_goals}
{onboarding_context}

Expert 1 - Progress Parser: Analyze the natural language input and extract structured progress data.
Expert 2 - Chart Generator: Generate chart configuration data for visualization.
Expert 3 - Insight Generator: Create a friendly, encouraging comment about the progress.

Rules for Goal Updates:
1. If the input mentions completing onboarding tasks (video, policies, quiz, forms), update the "Onboarding" goal
2. If the input mentions training, courses, or learning, update the "Training" goal
3. If the input mentions projects, deliverables, or work completion, update the "Project Delivery" goal
4. If the input mentions skills, certifications, or development, update the "Skill Development" goal
5. Progress should be realistic and incremental (typically 10-30% increases)
6. Consider the onboarding context when updating goals

Output Format (JSON only, no additional text):
{{
  "goals": [
    {{"id": 1, "name": "Training", "progress": 40, "target": 100}},
    {{"id": 2, "name": "Onboarding", "progress": 60, "target": 100}},
    {{"id": 3, "name": "Project Delivery", "progress": 25, "target": 100}},
    {{"id": 4, "name": "Skill Development", "progress": 30, "target": 100}}
  ],
  "chart_data": {{
    "type": "bar",
    "labels": ["Training", "Onboarding", "Project Delivery", "Skill Development"],
    "datasets": [{{
      "label": "Progress %",
      "data": [40, 60, 25, 30],
      "backgroundColor": ["#3498db", "#2980b9", "#1f5f8b", "#34495e"]
    }}]
  }},
  "insight": "Great progress! You've completed key onboarding tasks and are making solid progress on training."
}}

Output ONLY the JSON, no explanations or additional text.
"""

        # Use the HR agent to process the chain-of-experts prompt
        result = hr_agent.process_chat(chain_of_experts_prompt, f"progress_update_{hash(request.progress_text)}", [], {})
        ai_response = result["agent_response"]
        
        # Try to parse JSON response
        try:
            import json
            progress_data = json.loads(ai_response)
            
            # Validate the response structure
            if "goals" in progress_data and "chart_data" in progress_data and "insight" in progress_data:
                # Update goals in database if user state exists
                if user_state:
                    update_user_personal_goals(db, "test_user", {"goals": progress_data["goals"]})
                
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
                        "backgroundColor": ["#3498db", "#2980b9", "#1f5f8b", "#34495e"]
                    }]
                },
                "insight": "Progress update received! Keep up the great work on your goals."
            }
        
    except Exception as e:
        return {"error": f"Failed to update progress: {str(e)}"}

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

@app.get("/api/performance/users/{user_id}/goals", response_model=List[PerformanceGoalResponse])
def get_performance_user_goals(user_id: str, db: Session = Depends(get_performance_db)):
    """Get performance goals for a user"""
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