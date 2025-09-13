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
    Get AI-powered career recommendations using OpenAI model
    """
    try:
        # Get OpenAI configuration from environment or config
        openai_key = getattr(settings, 'OPENAI_API_KEY', os.getenv('OPENAI_API_KEY'))
        openai_model = getattr(settings, 'OPENAI_MODEL', os.getenv('OPENAI_MODEL', 'gpt-4o'))
        
        print(f"OpenAI key: {'SET' if openai_key else 'NOT SET'}")
        print(f"OpenAI model: {openai_model}")
        print(f"Quiz answers: {answers.answers}")
        
        if not openai_key or openai_key.strip() == "":
            # Fallback to mock response if no API key
            print("OpenAI API key not configured, returning mock response")
            return CareerCoachResponse(
                profile_summary="This is a mock summary since the OpenAI API key is not configured.",
                suggestions=(
                    "1. SAP Business Analyst: Good fit because the user shows analytical thinking.\n"
                    "2. SAP Technical Consultant: Suitable due to structured problem-solving approach.\n"
                    "3. SAP Project Manager: Matches leadership and organizational skills."
                )
            )
        
        # Create profile summary from quiz answers
        profile_text = ", ".join([f"{k}: {v}" for k, v in answers.answers.items()])
        summary_prompt = f"""Based on these career quiz responses: {profile_text}

Write a personalized, engaging profile summary in second person (using "you" and "your"). Make it sound natural and conversational, highlighting the person's strengths and work style. Keep it concise (2-3 sentences) and positive. Focus on what makes them unique and valuable in their career."""
        
        # Generate profile summary using OpenAI API
        summary_response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": openai_model,
                "messages": [
                    {"role": "system", "content": "You are a friendly, professional career coach specializing in SAP careers. Write in a warm, encouraging tone that makes people feel confident about their potential. Use second person (you/your) and be conversational yet professional."},
                    {"role": "user", "content": summary_prompt}
                ],
                "max_tokens": 150,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if summary_response.status_code != 200:
            print(f"OpenAI API error: {summary_response.status_code} - {summary_response.text}")
            if summary_response.status_code == 401:
                print("OpenAI API authentication failed, falling back to mock response")
                return CareerCoachResponse(
                    profile_summary="This is a mock summary since the OpenAI API authentication failed.",
                    suggestions=(
                        "1. SAP Business Analyst: Good fit because the user shows analytical thinking.\n"
                        "2. SAP Technical Consultant: Suitable due to structured problem-solving approach.\n"
                        "3. SAP Project Manager: Matches leadership and organizational skills."
                    )
                )
            raise HTTPException(status_code=500, detail=f"Failed to get profile summary from OpenAI API: {summary_response.status_code}")
        
        summary_data = summary_response.json()
        summary = summary_data["choices"][0]["message"]["content"] if "choices" in summary_data and len(summary_data["choices"]) > 0 else "No valid summary returned."
        
        # Generate personalized SAP role suggestions based on quiz responses
        roles_prompt = f"""Based on this user profile: {summary}

Here are SAP roles to consider based on their quiz responses: {profile_text}

Available SAP roles to match with:
- SAP Business Analyst (analytical, business-focused)
- SAP Technical Consultant (technical, implementation-focused)
- SAP Solution Architect (strategic, design-focused)
- SAP Project Manager (leadership, management-focused)
- SAP Functional Consultant (process-focused, module-specific)
- SAP Integration Specialist (technical, system integration)
- SAP Security Consultant (security-focused, compliance)
- SAP Data Analyst (data-focused, analytical)
- SAP Basis Administrator (technical, infrastructure)
- SAP SuccessFactors Consultant (HR-focused, cloud)
- SAP FICO Consultant (finance-focused, accounting)
- SAP MM Consultant (procurement-focused, supply chain)
- SAP SD Consultant (sales-focused, customer-facing)
- SAP HANA Developer (technical, database-focused)
- SAP Innovation Manager (innovation-focused, strategic)

Select the **top 3 SAP roles** that best match this person's profile and explain why each role is suitable in 1-2 sentences. Consider their work style, preferences, and career goals.

Format your response as:
1. [Role Name]: [Brief explanation]
2. [Role Name]: [Brief explanation]  
3. [Role Name]: [Brief explanation]

Do not include any introductory text like "Based on the user's profile" or "The top three SAP roles are". Start directly with the first role recommendation."""
        
        roles_response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": openai_model,
                "messages": [
                    {"role": "system", "content": "You are an expert SAP career advisor. Analyze the user's quiz responses and match them with the most suitable SAP roles from the provided list. Focus on alignment between their work style, preferences, and the role requirements. Be specific about why each role fits their profile."},
                    {"role": "user", "content": roles_prompt}
                ],
                "max_tokens": 250,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if roles_response.status_code != 200:
            print(f"OpenAI API error: {roles_response.status_code} - {roles_response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to get role suggestions from OpenAI API: {roles_response.status_code}")
        
        roles_data = roles_response.json()
        suggestions = roles_data["choices"][0]["message"]["content"] if "choices" in roles_data and len(roles_data["choices"]) > 0 else "No role suggestions returned."
        
        return CareerCoachResponse(
            profile_summary=summary,
            suggestions=suggestions
        )
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="OpenAI API request timed out")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API request failed: {str(e)}")
    except Exception as e:
        print(f"Career coach error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/api/career/health")
async def career_health_check():
    """
    Health check for career service
    """
    return {"status": "healthy", "service": "Career Coach API"}
