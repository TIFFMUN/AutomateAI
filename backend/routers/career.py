from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import requests
import os
import json
from config import settings
from services.recommendation_service import SAPJobRecommendationService

router = APIRouter()

class QuizAnswers(BaseModel):
    answers: Dict[str, str]

class CareerCoachResponse(BaseModel):
    profile_summary: str
    suggestions: str

class OracleRequest(BaseModel):
    current_role: str
    experience_years: int
    goal: Optional[str] = None

class CareerPath(BaseModel):
    level: int
    role: str
    timeline: str
    experience_required: int
    skills_required: List[str]
    skills_gained: List[str]
    prerequisites: List[str]
    story: str
    next_levels: List[int]
    is_ai_generated: bool = False

class CareerTree(BaseModel):
    tree_name: str
    tree_description: str
    tree_icon: str
    progressive_paths: List[CareerPath]

class OracleResponse(BaseModel):
    current_role: str
    experience_years: int
    career_trees: List[CareerTree]

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
        
        # Use recommendation service to get relevant jobs based on user responses
        print(f"\n🚀 Career Coach: Starting job recommendation matching...")
        recommendation_service = SAPJobRecommendationService()
        relevant_jobs = recommendation_service.get_recommended_jobs(answers.answers, top_k=5)
        job_context = recommendation_service.get_job_context(relevant_jobs)
        print(f"🎯 Career Coach: Job recommendations completed, proceeding with AI generation...")
        
        # Generate personalized SAP role suggestions using recommendation data
        roles_prompt = f"""Based on this user profile: {summary}

Here are SAP roles to consider based on their quiz responses: {profile_text}

{job_context}

Select the **top 3 SAP roles** from the relevant jobs above that best match this person's profile and explain why each role is suitable in 1-2 sentences. Consider their work style, preferences, and career goals.

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

@router.post("/api/career/oracle", response_model=OracleResponse)
async def career_oracle(request: OracleRequest):
    """
    Get RPG-style career paths using RAG retrieval + LLM generation
    """
    try:
        # 1️⃣ RAG Retrieval - Load career oracle database
        oracle_db_path = "data/career_oracle_db.json"
        if not os.path.exists(oracle_db_path):
            raise HTTPException(status_code=404, detail="Career oracle database not found")
        
        with open(oracle_db_path, 'r', encoding='utf-8') as f:
            oracle_data = json.load(f)
        
        # Find matching role and experience level
        matching_roles = []
        for role_data in oracle_data:
            if (role_data["role"].lower() == request.current_role.lower() or 
                request.current_role.lower() in role_data["role"].lower()):
                matching_roles.append(role_data)
        
        if not matching_roles:
            raise HTTPException(status_code=404, detail=f"No career paths found for role: {request.current_role}")
        
        # Get the closest experience match
        best_match = min(matching_roles, key=lambda x: abs(x["experience_years"] - request.experience_years))
        
        # 2️⃣ LLM Call - Generate additional paths
        openai_key = getattr(settings, 'OPENAI_API_KEY', os.getenv('OPENAI_API_KEY'))
        openai_model = getattr(settings, 'OPENAI_MODEL', os.getenv('OPENAI_MODEL', 'gpt-4o'))
        
        ai_generated_trees = []
        if openai_key and openai_key.strip() != "":
            try:
                # Prepare context for LLM
                existing_trees = best_match["career_trees"]
                trees_context = "\n".join([
                    f"- {tree['tree_name']}: {tree['tree_description']}"
                    for tree in existing_trees
                ])
                
                llm_prompt = f"""You are a career oracle expert. Based on this SAP professional's profile:

Current Role: {request.current_role}
Experience: {request.experience_years} years
Goal: {request.goal or 'General career growth'}

Existing career trees:
{trees_context}

Generate 1-2 additional career trees that complement the existing ones. Each tree should have 2-3 career paths. Focus on:
- Unique career directions not covered by existing trees
- Realistic SAP career progressions
- Specific skills, timelines, and prerequisites
- Engaging stories for each path

Format as JSON with this structure:
{{
  "trees": [
    {{
      "tree_name": "Tree Name",
      "tree_description": "Brief description",
      "tree_icon": "🎯",
      "paths": [
        {{
          "path_id": "unique_id",
          "future_role": "Role Name",
          "timeline": "X-Y years",
          "experience_required": X,
          "skills_required": ["skill1", "skill2"],
          "skills_gained": ["skill1", "skill2"],
          "prerequisites": ["prereq1", "prereq2"],
          "story": "Engaging narrative",
          "next_paths": ["next_id1", "next_id2"]
        }}
      ]
    }}
  ]
}}

Return only the JSON, no additional text."""

                llm_response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {openai_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": openai_model,
                        "messages": [
                            {"role": "system", "content": "You are an expert SAP career advisor. Generate realistic, detailed career paths in JSON format only."},
                            {"role": "user", "content": llm_prompt}
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.7
                    },
                    timeout=30
                )
                
                if llm_response.status_code == 200:
                    llm_data = llm_response.json()
                    llm_content = llm_data["choices"][0]["message"]["content"]
                    
                    # Parse LLM response
                    try:
                        ai_data = json.loads(llm_content)
                        for tree in ai_data.get("trees", []):
                            # Mark all paths as AI-generated
                            for path in tree["paths"]:
                                path["is_ai_generated"] = True
                            ai_generated_trees.append(tree)
                    except json.JSONDecodeError:
                        print(f"Failed to parse LLM response: {llm_content}")
                        
            except Exception as e:
                print(f"LLM generation failed: {str(e)}")
        
        # 3️⃣ Merge Paths - Combine RAG + LLM results
        all_trees = best_match["career_trees"] + ai_generated_trees
        
        # Convert to response format
        career_trees = []
        for tree in all_trees:
            paths = []
            for path in tree["progressive_paths"]:
                paths.append(CareerPath(
                    level=path["level"],
                    role=path["role"],
                    timeline=path["timeline"],
                    experience_required=path["experience_required"],
                    skills_required=path["skills_required"],
                    skills_gained=path["skills_gained"],
                    prerequisites=path["prerequisites"],
                    story=path["story"],
                    next_levels=path["next_levels"],
                    is_ai_generated=path.get("is_ai_generated", False)
                ))
            
            career_trees.append(CareerTree(
                tree_name=tree["tree_name"],
                tree_description=tree["tree_description"],
                tree_icon=tree["tree_icon"],
                progressive_paths=paths
            ))
        
        return OracleResponse(
            current_role=request.current_role,
            experience_years=request.experience_years,
            career_trees=career_trees
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Career oracle database not found")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid career oracle database format: {str(e)}")
    except Exception as e:
        print(f"Career oracle error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
