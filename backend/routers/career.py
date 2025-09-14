from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import requests
import os
import json
from config import settings
from services.recommendation_service import SAPJobRecommendationService

router = APIRouter()

def _validate_llm_path(path: dict, user_experience: int) -> bool:
    """
    Validate LLM-generated career path against basic constraints
    """
    try:
        # Check if role name contains SAP-relevant keywords
        role_name = path.get("role", "").lower()
        sap_keywords = ["sap", "abap", "fiori", "basis", "hana", "ui5"]
        if not any(keyword in role_name for keyword in sap_keywords):
            print(f"❌ Role '{path.get('role')}' is not SAP-relevant")
            return False
        
        # Check if skills contain SAP-relevant keywords
        skills = path.get("skills_required", [])
        if isinstance(skills, list):
            skills_text = " ".join(skills).lower()
        else:
            skills_text = str(skills).lower()
            
        if not any(keyword in skills_text for keyword in sap_keywords):
            print(f"❌ Skills {skills} are not SAP-relevant")
            return False
        
        # Basic timeline validation (should be reasonable)
        timeline = path.get("timeline", "")
        if "years" in timeline.lower():
            import re
            years_match = re.search(r'(\d+)', timeline)
            if years_match:
                required_years = int(years_match.group(1))
                # Allow some flexibility - don't be too strict
                if required_years > user_experience + 10:  # Allow up to 10 years ahead
                    print(f"❌ Timeline {timeline} seems unrealistic")
                    return False
        
        print(f"✅ Path {path.get('role')} passed validation")
        return True
        
    except Exception as e:
        print(f"❌ Validation error for path {path.get('role')}: {str(e)}")
        return False

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
    AI-powered career path oracle that crafts personalized routes based on constraints
    """
    try:
        print(f"🤖 Career Oracle: ENDPOINT CALLED!")
        print(f"🤖 Career Oracle: Starting AI crafting for {request.current_role} with {request.experience_years} years experience")
        print(f"🤖 Career Oracle: Request goal: {request.goal}")
        print(f"🤖 Career Oracle: Request data: {request.dict()}")
        
        # Load constraints from database
        oracle_db_path = "data/career_oracle_db.json"
        constraints_context = ""
        
        if os.path.exists(oracle_db_path):
            with open(oracle_db_path, 'r', encoding='utf-8') as f:
                oracle_data = json.load(f)
            
            # Build constraints context for LLM
            constraints_list = []
            for role_data in oracle_data:
                if "constraints" in role_data:
                    constraints_list.append(
                        f"- {role_data['role']}: {role_data['constraints']['min_experience']}+ years, "
                        f"skills: {', '.join(role_data['constraints']['required_skills'])}, "
                        f"types: {', '.join(role_data['constraints']['career_types'])}"
                    )
            
            constraints_context = "\n".join(constraints_list[:10])  # Limit to avoid token limits
        
        # Get OpenAI configuration
        openai_key = getattr(settings, 'OPENAI_API_KEY', os.getenv('OPENAI_API_KEY'))
        openai_model = getattr(settings, 'OPENAI_MODEL', os.getenv('OPENAI_MODEL', 'gpt-4o'))
        
        print(f"🤖 Career Oracle: OpenAI key status: {'SET' if openai_key else 'NOT SET'}")
        print(f"🤖 Career Oracle: OpenAI model: {openai_model}")
        
        career_trees = []
        
        if openai_key and openai_key.strip() != "":
            try:
                print(f"🤖 Career Oracle: OpenAI key found, calling LLM to craft personalized routes...")
                print(f"🤖 Career Oracle: Constraints context length: {len(constraints_context)}")
                
                # Craft focused prompt for route generation
                llm_prompt = f"""Create 2-3 realistic SAP career progression routes for this professional.

PROFILE: {request.current_role} with {request.experience_years} years experience, goal: {request.goal or 'career growth'}

AVAILABLE SAP ROLES:
{constraints_context}

CAREER PROGRESSION RULES:
1. TECHNICAL ROLES (Developer, Architect) → Stay in technical track or move to Technical Lead/Manager
2. FUNCTIONAL ROLES (Consultant, Analyst) → Progress to Senior Consultant, Lead, or Manager
3. MANAGEMENT ROLES (Manager, Director) → Progress to Senior Management or Executive roles
4. BUSINESS ROLES (Analyst, Business roles) → Progress to Senior Business roles or Management
5. EXECUTIVE ROLES (CTO, VP) → Stay in executive track or board positions

LOGICAL PROGRESSIONS:
- ABAP Developer → Senior Developer → Technical Lead → Development Manager
- SAP FI Consultant → Senior Consultant → Functional Lead → Solution Architect
- SAP Business Analyst → Senior Analyst → Business Process Consultant → Project Manager
- SAP Project Manager → Senior PM → Program Manager → Director
- SAP Solution Architect → Senior Architect → Principal Architect → CTO
- SAP Security Consultant → Senior Security → Security Manager → CISO
- SAP Development Manager → Director → VP Engineering → CTO
- SAP CTO → Senior VP → President → Board Member

Create routes with 2-3 realistic steps each. Each step should show:
- LOGICAL progression from current role (don't jump between unrelated tracks)
- Realistic timeline based on their {request.experience_years} years experience
- Specific SAP skills needed and gained
- Personal story explaining why this step makes sense

Return JSON format:
{{
  "career_routes": [
    {{
      "route_name": "Route Name",
      "route_description": "Brief description",
      "route_icon": "🎯",
      "steps": [
        {{
          "role": "SAP Role Name",
          "timeline": "1-2 years",
          "experience_required": {request.experience_years + 1},
          "skills_required": ["SAP skill1", "SAP skill2"],
          "skills_gained": ["new skill1", "new skill2"],
          "prerequisites": ["prereq1"],
          "story": "Why this role fits their {request.experience_years} years experience and {request.goal or 'career growth'} goal"
        }}
      ]
    }}
  ]
}}

CRITICAL: Follow logical career progression rules above. Don't suggest Project Manager → Solution Architect or other illogical jumps."""

                llm_response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {openai_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": openai_model,
                        "messages": [
                            {"role": "system", "content": "You are an expert SAP career advisor. Generate realistic, personalized career routes in JSON format only."},
                            {"role": "user", "content": llm_prompt}
                        ],
                        "max_tokens": 1200,
                        "temperature": 0.7
                    },
                    timeout=30
                )
                
                if llm_response.status_code == 200:
                    llm_data = llm_response.json()
                    llm_content = llm_data["choices"][0]["message"]["content"]
                    
                    print(f"🤖 Career Oracle: LLM response status: {llm_response.status_code}")
                    print(f"🤖 Career Oracle: Raw LLM content: {llm_content[:500]}...")
                    
                    # Parse and validate LLM response
                    try:
                        print(f"🤖 Career Oracle: Processing LLM response...")
                        
                        # Clean the response
                        cleaned_content = llm_content.strip()
                        if cleaned_content.startswith("```json"):
                            cleaned_content = cleaned_content[7:]
                        if cleaned_content.startswith("```"):
                            cleaned_content = cleaned_content[3:]
                        if cleaned_content.endswith("```"):
                            cleaned_content = cleaned_content[:-3]
                        cleaned_content = cleaned_content.strip()
                        
                        ai_data = json.loads(cleaned_content)
                        print(f"🔍 Parsed LLM data: {ai_data}")
                        validated_routes = []
                        
                        # Check if we have the expected structure
                        if "career_routes" not in ai_data:
                            print("❌ No 'career_routes' key in LLM response")
                            print(f"Available keys: {list(ai_data.keys())}")
                            career_trees = []
                        else:
                            for route in ai_data.get("career_routes", []):
                                print(f"🔍 Processing route: {route.get('route_name', 'Unknown')}")
                                validated_steps = []
                                
                                for step in route.get("steps", []):
                                    # More lenient validation - accept any role that looks professional
                                    role_name = step.get("role", "").lower()
                                    if role_name and len(role_name) > 3:  # Basic validation
                                        step["is_ai_generated"] = True
                                        validated_steps.append(step)
                                        print(f"✅ Validated step: {step.get('role')}")
                                    else:
                                        print(f"❌ Rejected invalid role: {step.get('role')}")
                                
                                if validated_steps:
                                    validated_routes.append({
                                        "tree_name": route["route_name"],
                                        "tree_description": route["route_description"],
                                        "tree_icon": route["route_icon"],
                                        "progressive_paths": validated_steps
                                    })
                                    print(f"✅ Added route: {route['route_name']}")
                                else:
                                    print(f"❌ No valid steps for route: {route.get('route_name')}")
                            
                            career_trees = validated_routes
                        print(f"🤖 Career Oracle: Generated {len(career_trees)} career routes")
                        
                        if len(career_trees) == 0:
                            print("⚠️ No valid career routes generated - all routes were filtered out")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse LLM response: {str(e)}")
                        print(f"Raw response: {llm_content[:200]}...")
                        career_trees = []
                else:
                    print(f"❌ LLM API call failed with status: {llm_response.status_code}")
                    print(f"❌ Response: {llm_response.text}")
                    career_trees = []
                        
            except Exception as e:
                print(f"❌ LLM generation failed: {str(e)}")
                career_trees = []
        else:
            print("❌ OpenAI API key not configured")
            career_trees = []
        
        # Convert to response format
        final_career_trees = []
        
        for tree in career_trees:
            paths = []
            for path in tree["progressive_paths"]:
                paths.append(CareerPath(
                    level=path.get("level", 1),
                    role=path["role"],
                    timeline=path["timeline"],
                    experience_required=path["experience_required"],
                    skills_required=path["skills_required"],
                    skills_gained=path["skills_gained"],
                    prerequisites=path["prerequisites"],
                    story=path["story"],
                    next_levels=path.get("next_levels", []),
                    is_ai_generated=path.get("is_ai_generated", True)
                ))
            
            final_career_trees.append(CareerTree(
                tree_name=tree["tree_name"],
                tree_description=tree["tree_description"],
                tree_icon=tree["tree_icon"],
                progressive_paths=paths
            ))
        
        print(f"🤖 Career Oracle: Returning {len(final_career_trees)} crafted routes")
        print(f"🤖 Career Oracle: final_career_trees content: {[tree.tree_name for tree in final_career_trees]}")
        
        if len(final_career_trees) == 0:
            print("⚠️ No career routes to return - generating fallback routes")
            # Generate basic fallback routes
            fallback_routes = [
                {
                    "tree_name": "Technical Progression",
                    "tree_description": "Advance your technical skills in SAP development",
                    "tree_icon": "💻",
                    "progressive_paths": [
                        {
                            "role": f"Senior {request.current_role}",
                            "timeline": "1-2 years",
                            "experience_required": request.experience_years + 1,
                            "skills_required": ["Advanced ABAP", "Performance Optimization"],
                            "skills_gained": ["Senior Development Skills", "Code Review"],
                            "prerequisites": ["Current role experience"],
                            "story": f"Build on your {request.experience_years} years of experience to become a senior developer",
                            "is_ai_generated": False
                        }
                    ]
                }
            ]
            
            for route in fallback_routes:
                paths = []
                for path in route["progressive_paths"]:
                    paths.append(CareerPath(
                        level=1,
                        role=path["role"],
                        timeline=path["timeline"],
                        experience_required=path["experience_required"],
                        skills_required=path["skills_required"],
                        skills_gained=path["skills_gained"],
                        prerequisites=path["prerequisites"],
                        story=path["story"],
                        next_levels=[],
                        is_ai_generated=path["is_ai_generated"]
                    ))
                
                final_career_trees.append(CareerTree(
                    tree_name=route["tree_name"],
                    tree_description=route["tree_description"],
                    tree_icon=route["tree_icon"],
                    progressive_paths=paths
                ))
        
        return OracleResponse(
            current_role=request.current_role,
            experience_years=request.experience_years,
            career_trees=final_career_trees
        )
        
    except Exception as e:
        print(f"❌ Career oracle error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return fallback response even on error
        print("🔄 Returning fallback response due to error")
        fallback_tree = CareerTree(
            tree_name="Career Guidance",
            tree_description="Basic career progression guidance",
            tree_icon="💼",
            progressive_paths=[
                CareerPath(
                    level=1,
                    role=f"Senior {request.current_role}",
                    timeline="1-2 years",
                    experience_required=request.experience_years + 1,
                    skills_required=["Advanced Skills", "Leadership"],
                    skills_gained=["Senior Level Skills", "Mentoring"],
                    prerequisites=["Current Experience"],
                    story=f"Progress from your current {request.current_role} role with {request.experience_years} years experience",
                    next_levels=[],
                    is_ai_generated=False
                )
            ]
        )
        
        return OracleResponse(
            current_role=request.current_role,
            experience_years=request.experience_years,
            career_trees=[fallback_tree]
        )
