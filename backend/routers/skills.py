# skills.py

from openai import AsyncOpenAI
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import json
import traceback
from serpapi import GoogleSearch

# Assumes you have your OpenAI API key and SerpAPI key in config.py
from config import settings

router = APIRouter()

# ----------- MODELS -----------

class SkillRecommendationRequest(BaseModel):
    current_skills: str
    user_profile: str = "professional"

class Resource(BaseModel):
    title: str
    link: str

class SkillRecommendation(BaseModel):
    skill: str
    reason: str
    difficulty: str
    estimatedTime: str
    resources: List[Resource]

class SkillRecommendationResponse(BaseModel):
    recommendations: List[SkillRecommendation]

# ----------- SEARCH HELPER (SerpAPI) -----------

def search_courses(skill_name: str, max_results: int = 4) -> List[Resource]:
    """
    Search for real online courses using SerpAPI (Google Search API).
    Returns up to `max_results` Resource objects.
    """
    query = f"{skill_name} online course site:coursera.org OR site:udemy.com OR site:edx.org OR site:pluralsight.com"

    params = {
        "q": query,
        "hl": "en",
        "gl": "us",
        "api_key": settings.SERPAPI_KEY
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as e:
        print(f"Search error for {skill_name}: {e}")
        return []

    resources = []
    # First check "organic_results"
    for item in results.get("organic_results", []):
        title = item.get("title")
        link = item.get("link")
        if title and link:
            resources.append(Resource(title=title, link=link))
        if len(resources) >= max_results:
            break

    return resources

# ----------- ROUTE -----------

@router.post("/api/skills/recommendations", response_model=SkillRecommendationResponse)
async def get_skill_recommendations(request: SkillRecommendationRequest):
    try:
        # Initialize OpenAI client with the correct API key
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        skill_prompt = f"""
        Based on the user's current skills and profile, recommend 3-5 skills they should learn next.
        User's Current Skills: {request.current_skills}
        User Profile: {request.user_profile}
        
        For each recommended skill, provide:
        1. Skill name
        2. Reason why this skill is valuable
        3. Difficulty level (Beginner, Intermediate, Advanced)
        4. Estimated time to learn (e.g., '1-2 weeks', '2-3 months', '6 months')
        
        Format the response strictly as a JSON object with a single key "recommendations". 
        The value of this key should be an array of objects, where each object has the keys: 
        skill, reason, difficulty, and estimatedTime.
        """

        skill_response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a career development expert. Always output a strict JSON object with a 'recommendations' key."},
                {"role": "user", "content": skill_prompt}
            ],
            temperature=0.7,
            max_tokens=800,
            response_format={"type": "json_object"}
        )

        skills_json = skill_response.choices[0].message.content.strip()
        skills_data = json.loads(skills_json)
        recommendations_list = skills_data.get("recommendations", [])

        if not recommendations_list:
            raise HTTPException(status_code=500, detail="OpenAI response did not contain recommendations.")

        recommendations = []
        for rec in recommendations_list:
            skill_name = rec.get("skill", "")
            if not skill_name:
                continue

            # 🔍 Fetch real resources using SerpAPI (Google)
            resources = search_courses(skill_name)

            recommendations.append(SkillRecommendation(
                skill=skill_name,
                reason=rec.get("reason", ""),
                difficulty=rec.get("difficulty", "Intermediate"),
                estimatedTime=rec.get("estimatedTime", "2-3 months"),
                resources=resources
            ))

        return SkillRecommendationResponse(recommendations=recommendations)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate skill recommendations: {str(e)}")
