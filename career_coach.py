import requests
from typing import List
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS

# --- 1. SEA-LION API Key ---
SEA_LION_API_KEY = ""  # Replace with your SEA-LION key
SEA_LION_MODEL = "aisingapore/Gemma-SEA-LION-v4-27B-IT"

# --- 2. SEA-LION LLM Wrapper ---
class SEA_LION_LLM:
    def __init__(self, model=SEA_LION_MODEL, api_key=SEA_LION_API_KEY):
        self.model = model
        self.api_key = api_key
        self.endpoint = "https://api.sea-lion.ai/v1/chat/completions"

    def __call__(self, prompt: str, max_tokens=150) -> str:
        payload = {
            "model": self.model,
            "max_completion_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "accept": "text/plain"
        }
        response = requests.post(self.endpoint, json=payload, headers=headers)
        response.raise_for_status()
        # SEA-LION returns raw text in the response body
        return response.text.strip()

llm = SEA_LION_LLM()

# --- 3. Mock Embeddings for FAISS ---
class MockEmbeddings:
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[1.0, 2.0, 3.0, 4.0]] * len(texts)

    def embed_query(self, text: str) -> List[float]:
        return [1.0, 2.0, 3.0, 4.0]

mock_embeddings = MockEmbeddings()

# --- 4. Skills Assessment Agent ---
class SkillsAssessmentAgent:
    def __init__(self, llm):
        self.llm = llm
        self.quiz_questions = [
            "1. When working on a group project, what role do you naturally gravitate towards?\n   A) The visionary\n   B) The analyst\n   C) The facilitator",
            "2. You're given a task with a tight deadline. Your first instinct is to:\n   A) Experiment\n   B) Plan\n   C) Ask colleagues",
            "3. Which statement best describes your ideal measure of success?\n   A) Innovation\n   B) Efficiency\n   C) Positive feedback",
            "4. How do you prefer to learn new things?\n   A) Trial and error\n   B) Manuals/training\n   C) Shadowing an expert",
            "5. A teammate is stuck. You are more likely to:\n   A) Brainstorm\n   B) Work step-by-step\n   C) Listen & support",
            "6. Which task energizes you most?\n   A) Building new systems\n   B) Troubleshooting issues\n   C) Presenting work"
        ]

    def run_quiz(self):
        answers = {}
        print("Welcome to the Career Quiz! Please answer a few questions.")
        for i, q in enumerate(self.quiz_questions):
            answer = input(f"{q}\nYour answer (A/B/C): ")
            answers[f"q{i+1}"] = answer.lower()
        return answers

    def get_profile_summary(self, answers):
        answers_str = ", ".join([f"{k}: {v}" for k, v in answers.items()])
        prompt = f"Summarize the user's work style, skills, and motivations based on their quiz answers: {answers_str} in under 80 words."
        return self.llm(prompt)

# --- 5. Knowledge & Learning Agent ---
class KnowledgeLearningAgent:
    def __init__(self, vectorstore, llm):
        self.vectorstore = vectorstore
        self.llm = llm

    def suggest_roles(self, profile_summary):
        prompt = f"Based on this profile: {profile_summary}. Suggest the 3 best-matching SAP job roles from the database, with 1–2 sentences why each fits."
        return self.llm(prompt)

# --- 6. Career Catalyst ---
class CareerCatalyst:
    def __init__(self, llm, vectorstore):
        self.skills_agent = SkillsAssessmentAgent(llm)
        self.knowledge_agent = KnowledgeLearningAgent(vectorstore, llm)

    def start_session(self):
        print("🚀 Welcome to the SAP Career Catalyst! Let's find your ideal path.")
        user_answers = self.skills_agent.run_quiz()
        profile_summary = self.skills_agent.get_profile_summary(user_answers)
        print(f"\nYour profile summary: {profile_summary}")
        suggestions = self.knowledge_agent.suggest_roles(profile_summary)
        print("\nHere are some suggested job roles for you at SAP:")
        print(suggestions)
        print("\n✨ Your personalized career journey starts now! ✨")

# --- 7. SAP Roles Data ---
sap_roles_data = [
    {"name": "SAP ABAP Developer", "description": "Specializes in programming and developing custom applications using SAP ABAP."},
    {"name": "SAP Functional Consultant", "description": "Works with clients to configure SAP modules (Finance, HR, etc.)."},
    {"name": "SAP Business Analyst", "description": "Translates business needs into technical requirements, focusing on optimization."},
    {"name": "Data Scientist", "description": "Uses analysis and ML to extract insights from SAP data."},
    {"name": "Cloud Engineer", "description": "Manages cloud infrastructure for SAP apps on AWS, Azure, or GCP."},
    {"name": "Customer Success Manager", "description": "Builds long-term relationships ensuring SAP product adoption and value."},
    {"name": "Human Resources Specialist", "description": "Supports employee well-being using SAP SuccessFactors."},
    {"name": "Solution Architect", "description": "Designs SAP solutions meeting business needs."},
    {"name": "Security Analyst", "description": "Protects SAP systems and data from cyber threats."},
    {"name": "Product Manager", "description": "Defines vision and strategy for SAP software products."},
    {"name": "Technical Writer", "description": "Creates documentation for SAP systems."},
    {"name": "Support Engineer", "description": "Provides technical support to resolve SAP issues."}
]

documents = [Document(page_content=f"{d['name']}: {d['description']}", metadata={"name": d['name']}) for d in sap_roles_data]

# --- 8. Create Vectorstore ---
vectorstore = FAISS.from_documents(documents, mock_embeddings)

# --- 9. Run Career Catalyst ---
catalyst = CareerCatalyst(llm, vectorstore)
catalyst.start_session()
