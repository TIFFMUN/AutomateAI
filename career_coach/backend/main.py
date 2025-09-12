# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pydantic import BaseModel
import requests

app = FastAPI()

# Paths
app_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(app_dir, "frontend", "build")
static_dir = os.path.join(build_dir, "static")

# Mount static folder correctly
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# SPA fallback for everything else
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    index_path = os.path.join(build_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "index.html not found"}

# Backend API
SEA_LION_KEY = "sk-g0qhlR-f0sCkuYWowHx_AA"  # Use env var
SEA_LION_MODEL = "aisingapore/Gemma-SEA-LION-v4-27B-IT"

class QuizAnswers(BaseModel):
    answers: dict

@app.post("/career-coach")
def career_coach(answers: QuizAnswers):
    # 1️⃣ Create profile summary
    profile_text = ", ".join([f"{k}: {v}" for k,v in answers.answers.items()])
    summary_prompt = f"Summarize the user's work style, skills, and motivations based on their answers: {profile_text}"

    if SEA_LION_KEY:
        try:
            # Generate profile summary
            response = requests.post(
                "https://api.sea-lion.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {SEA_LION_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": SEA_LION_MODEL,
                    "messages": [{"role": "user", "content": summary_prompt}],
                    "max_completion_tokens": 150
                }
            )
            data = response.json()
            summary = data["choices"][0]["message"]["content"] if "choices" in data and len(data["choices"]) > 0 else "No valid summary returned."

            # Generate top 3 SAP role suggestions
            roles_prompt = (
                f"Based on this user profile:\n{summary}\n\n"
                "Suggest the **top 3 SAP roles** that match this profile and provide 1-2 sentences "
                "explaining why each role is suitable. Only output the roles and explanations."
            )
            roles_response = requests.post(
                "https://api.sea-lion.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {SEA_LION_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": SEA_LION_MODEL,
                    "messages": [{"role": "user", "content": roles_prompt}],
                    "max_completion_tokens": 250
                }
            )
            roles_data = roles_response.json()
            suggestions = roles_data["choices"][0]["message"]["content"] if "choices" in roles_data and len(roles_data["choices"]) > 0 else "No role suggestions returned."

        except Exception as e:
            summary = f"Error calling SEA-LION: {str(e)}"
            suggestions = "Could not generate role suggestions due to API error."
    else:
        # Mock fallback if no key
        summary = "This is a mock summary since the API key is not set."
        suggestions = (
            "1. SAP Business Analyst: Good fit because the user is analytical.\n"
            "2. Data Scientist: Matches their troubleshooting and problem-solving skills.\n"
            "3. SAP ABAP Developer: Suitable due to structured and methodical approach."
        )

    return {
        "profile_summary": summary,
        "suggestions": suggestions
    }