from fastapi import FastAPI
from pydantic import BaseModel
import requests
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Serve React build
app_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(app_dir, "frontend", "build")
app.mount("/", StaticFiles(directory=build_dir, html=True), name="frontend")


SEA_LION_KEY = os.getenv("SEA_LION_KEY")
SEA_LION_MODEL = "aisingapore/Gemma-SEA-LION-v4-27B-IT"

class QuizAnswers(BaseModel):
    answers: dict

@app.post("/career-coach")
def career_coach(answers: QuizAnswers):
    profile_text = ", ".join([f"{k}: {v}" for k,v in answers.answers.items()])
    prompt = f"Summarize the user's work style, skills, and motivations based on their answers: {profile_text}"

    response = requests.post(
        "https://api.sea-lion.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {SEA_LION_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": SEA_LION_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_completion_tokens": 150
        }
    )
    summary = response.json()["choices"][0]["message"]["content"]

    # Here you could add logic to suggest SAP roles
    suggestions = f"Suggested roles based on profile: {summary}"

    return {"profile_summary": summary, "suggestions": suggestions}
