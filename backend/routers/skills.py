# skills.py

from openai import AsyncOpenAI
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import json
import traceback

# Assumes you have your OpenAI API key in config.py
from config import settings

router = APIRouter()

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
        
        Format the response strictly as a JSON object with a single key "recommendations". The value of this key should be an array of objects, where each object has the keys: skill, reason, difficulty, and estimatedTime.
        """
        
        skill_response = await client.chat.completions.create(
            model="gpt-3.5-turbo", # Change to an OpenAI model
            messages=[
                {"role": "system", "content": "You are a career development expert. Always output a strict JSON object with a 'recommendations' key."},
                {"role": "user", "content": skill_prompt}
            ],
            temperature=0.7,
            max_tokens=800,
            response_format={"type": "json_object"} # Use this for better JSON formatting
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

            resource_prompt = f"""
            Search for 3-4 real, popular online courses for learning '{skill_name}'.
            For each course, provide the title and a direct link to the course page.
            Format strictly as a JSON object with a single key "resources", where the value is an array of objects. Each object should have keys "title" and "link".
            Example: {{"resources": [{{"title": "Coursera: Python for Everybody", "link": "https://www.coursera.org/learn/python"}}]}}
            """

            resource_response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that finds real online courses. Always provide direct links to the course pages. Your output must be a valid JSON object."},
                    {"role": "user", "content": resource_prompt}
                ],
                temperature=0.6,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            try:
                resources_dict = json.loads(resource_response.choices[0].message.content.strip())
                resources = [Resource(**res) for res in resources_dict.get("resources", [])]
            except (json.JSONDecodeError, KeyError, TypeError):
                resources = [] # On error, return an empty list of resources

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