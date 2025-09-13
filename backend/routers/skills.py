from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import openai
import os
from config import settings

router = APIRouter()

class SkillRecommendationRequest(BaseModel):
    current_skills: str
    user_profile: str = "professional"

class SkillRecommendation(BaseModel):
    skill: str
    reason: str
    difficulty: str
    estimatedTime: str
    resources: List[str]

class SkillRecommendationResponse(BaseModel):
    recommendations: List[SkillRecommendation]

@router.post("/api/skills/recommendations", response_model=SkillRecommendationResponse)
async def get_skill_recommendations(request: SkillRecommendationRequest):
    """
    Get AI-powered skill recommendations based on user's current skills and profile.
    """
    try:
        # Initialize OpenAI client
        openai.api_key = settings.OPENAI_API_KEY
        
        # Create prompt for skill recommendations
        prompt = f"""
        Based on the user's current skills and profile, recommend 3-5 skills they should learn next.
        
        User's Current Skills: {request.current_skills}
        User Profile: {request.user_profile}
        
        For each recommended skill, provide:
        1. Skill name
        2. Reason why this skill is valuable for them
        3. Difficulty level (Beginner, Intermediate, Advanced)
        4. Estimated time to learn (e.g., "1-2 months", "3-6 months")
        5. 3-4 specific learning resources (courses, books, platforms, etc.)
        
        Format your response as a JSON array with the following structure:
        [
            {{
                "skill": "Skill Name",
                "reason": "Why this skill is valuable",
                "difficulty": "Beginner/Intermediate/Advanced",
                "estimatedTime": "Time estimate",
                "resources": ["Resource 1", "Resource 2", "Resource 3", "Resource 4"]
            }}
        ]
        
        Focus on practical, in-demand skills that complement their current abilities.
        Consider industry trends and career advancement opportunities.
        """
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a career development expert who provides personalized skill recommendations. Always respond with valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse the response
        recommendations_text = response.choices[0].message.content.strip()
        
        # Try to parse as JSON
        import json
        try:
            recommendations_data = json.loads(recommendations_text)
            
            # Convert to our response model
            recommendations = []
            for rec in recommendations_data:
                recommendations.append(SkillRecommendation(
                    skill=rec.get("skill", ""),
                    reason=rec.get("reason", ""),
                    difficulty=rec.get("difficulty", "Intermediate"),
                    estimatedTime=rec.get("estimatedTime", "2-3 months"),
                    resources=rec.get("resources", [])
                ))
            
            return SkillRecommendationResponse(recommendations=recommendations)
            
        except json.JSONDecodeError:
            # If JSON parsing fails, return default recommendations
            default_recommendations = [
                SkillRecommendation(
                    skill="Machine Learning",
                    reason="High demand in tech industry and complements data analysis skills",
                    difficulty="Advanced",
                    estimatedTime="3-6 months",
                    resources=["Coursera ML Course", "Kaggle Competitions", "TensorFlow Tutorials", "Andrew Ng's Course"]
                ),
                SkillRecommendation(
                    skill="Cloud Computing (AWS)",
                    reason="Essential for modern software development and deployment",
                    difficulty="Intermediate",
                    estimatedTime="2-4 months",
                    resources=["AWS Training", "Hands-on Labs", "Certification Prep", "AWS Documentation"]
                ),
                SkillRecommendation(
                    skill="Agile Project Management",
                    reason="Improves team collaboration and project success rates",
                    difficulty="Beginner",
                    estimatedTime="1-2 months",
                    resources=["Scrum Master Training", "Agile Books", "Practice Projects", "PMI Resources"]
                )
            ]
            return SkillRecommendationResponse(recommendations=default_recommendations)
            
    except Exception as e:
        print(f"Error in skill recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate skill recommendations")

@router.get("/api/skills/categories")
async def get_skill_categories():
    """
    Get available skill categories.
    """
    return {
        "categories": [
            {"id": "technical", "name": "Technical", "color": "#f093fb"},
            {"id": "soft", "name": "Soft Skills", "color": "#4facfe"},
            {"id": "leadership", "name": "Leadership", "color": "#43e97b"},
            {"id": "business", "name": "Business", "color": "#667eea"}
        ]
    }
