from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import requests
import os
from config import settings

router = APIRouter()

class QuizAnswers(BaseModel):
    answers: Dict[str, str]

class CareerCoachResponse(BaseModel):
    profile_summary: str
    suggestions: str

@router.post("/api/career/coach", response_model=CareerCoachResponse)
async def career_coach(answers: QuizAnswers):
    """
    Get AI-powered career recommendations using SeaLion model
    """
    try:
        # Get SeaLion configuration from environment or config
        sea_lion_key = getattr(settings, 'SEA_LION_KEY', os.getenv('SEA_LION_KEY'))
        sea_lion_model = getattr(settings, 'SEA_LION_MODEL', os.getenv('SEA_LION_MODEL', 'aisingapore/Gemma-SEA-LION-v4-27B-IT'))
        
        if not sea_lion_key:
            # Fallback to mock response if no API key
            return CareerCoachResponse(
                profile_summary="This is a mock summary since the SeaLion API key is not configured.",
                suggestions=(
                    "1. SAP Business Analyst: Good fit because the user shows analytical thinking.\n"
                    "2. SAP Technical Consultant: Suitable due to structured problem-solving approach.\n"
                    "3. SAP Project Manager: Matches leadership and organizational skills."
                )
            )
        
        # Create profile summary from quiz answers
        profile_text = ", ".join([f"{k}: {v}" for k, v in answers.answers.items()])
        summary_prompt = f"Summarize the user's work style, skills, and motivations based on their answers: {profile_text}"
        
        # Generate profile summary using SeaLion
        summary_response = requests.post(
            "https://api.sea-lion.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {sea_lion_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": sea_lion_model,
                "messages": [{"role": "user", "content": summary_prompt}],
                "max_completion_tokens": 150
            },
            timeout=30
        )
        
        if summary_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to get profile summary from SeaLion API")
        
        summary_data = summary_response.json()
        summary = summary_data["choices"][0]["message"]["content"] if "choices" in summary_data and len(summary_data["choices"]) > 0 else "No valid summary returned."
        
        # Generate top 3 SAP role suggestions
        roles_prompt = (
            f"Based on this user profile:\n{summary}\n\n"
            "Suggest the **top 3 SAP roles** that match this profile and provide 1-2 sentences "
            "explaining why each role is suitable. Only output the roles and explanations."
        )
        
        roles_response = requests.post(
            "https://api.sea-lion.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {sea_lion_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": sea_lion_model,
                "messages": [{"role": "user", "content": roles_prompt}],
                "max_completion_tokens": 250
            },
            timeout=30
        )
        
        if roles_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to get role suggestions from SeaLion API")
        
        roles_data = roles_response.json()
        suggestions = roles_data["choices"][0]["message"]["content"] if "choices" in roles_data and len(roles_data["choices"]) > 0 else "No role suggestions returned."
        
        return CareerCoachResponse(
            profile_summary=summary,
            suggestions=suggestions
        )
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="SeaLion API request timed out")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"SeaLion API request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/api/career/health")
async def career_health_check():
    """
    Health check for career service
    """
    return {"status": "healthy", "service": "Career Coach API"}
