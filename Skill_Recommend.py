import pandas as pd
import google.generativeai as genai
from IPython.display import display

# -------------------------
# Configure Gemini API
# -------------------------
genai.configure(api_key="key")

# -------------------------
# Sample Databases
# -------------------------
skills_db = {
    "Python": "Advanced",
    "SQL": "Advanced",
    "Machine Learning": "Intermediate",
    "Statistics": "Intermediate",
    "Excel": "Advanced",
    "Communication": "Advanced",
    "Data Visualization": "Intermediate",
    "Java": "Intermediate",
    "System Design": "Intermediate",
    "Git": "Intermediate"
}

course_db = {
    "Python": [
        {"title": "Python for Everybody (Coursera)", "duration_weeks": 4},
        {"title": "Intermediate Python (DataCamp)", "duration_weeks": 3}
    ],
    "SQL": [
        {"title": "SQL for Data Science (Coursera)", "duration_weeks": 3},
        {"title": "Advanced SQL (Udemy)", "duration_weeks": 4}
    ],
    "Machine Learning": [
        {"title": "Machine Learning (Andrew Ng, Coursera)", "duration_weeks": 6},
        {"title": "Practical Deep Learning (Fast.ai)", "duration_weeks": 5}
    ],
    "Statistics": [
        {"title": "Statistics with Python (Coursera)", "duration_weeks": 4}
    ],
    "Excel": [
        {"title": "Excel Skills for Business (Coursera)", "duration_weeks": 3}
    ],
    "Communication": [
        {"title": "Effective Business Communication (edX)", "duration_weeks": 2}
    ],
    "Data Visualization": [
        {"title": "Data Visualization with Tableau (Coursera)", "duration_weeks": 4}
    ],
    "Java": [
        {"title": "Java Programming Masterclass (Udemy)", "duration_weeks": 6}
    ],
    "System Design": [
        {"title": "System Design Primer (Educative)", "duration_weeks": 5}
    ],
    "Git": [
        {"title": "Git & GitHub Crash Course (Udemy)", "duration_weeks": 2}
    ]
}

skill_levels = ["Beginner", "Intermediate", "Advanced"]

# -------------------------
# Helper Functions
# -------------------------
def compare_levels(user_level, target_level):
    if skill_levels.index(user_level) >= skill_levels.index(target_level):
        return "Mastered"
    else:
        return "Needs Improvement"

# -------------------------
# Gemini LLM: Course Summaries Only
# -------------------------
model = genai.GenerativeModel('gemini-1.5-flash') 

# def generate_course_summary(skill, status, course_title):
#     prompt = (
#         f"Explain why the skill '{skill}' is important for someone who is '{status}' in it, "
#         f"and how taking the course '{course_title}' will help them improve. "
#         "Keep the explanation concise and actionable."
#     )
#     response = model.generate_content(prompt)
#     return response.text

#Using this now as token ran out#
def generate_course_summary(skill, status, course_title):
    # Simple fallback summary without API
    return f"This course '{course_title}' will help you improve your '{skill}' skill which is currently '{status}'."


# -------------------------
# Agents
# -------------------------
class SkillProfilingAgent:
    def process(self, user_skills_dict):
        return user_skills_dict

class GapAnalysisAgent:
    def process(self, user_skills, target_skills):
        gaps = {}
        for skill, target_level in target_skills.items():
            user_level = user_skills.get(skill, "Beginner")
            gaps[skill] = compare_levels(user_level, target_level)
        return gaps

class CourseRecommendationAgent:
    def process(self, gaps):
        recommendations = []
        for skill, status in gaps.items():
            if status == "Needs Improvement" and skill in course_db:
                for course in course_db[skill]:
                    summary = generate_course_summary(skill, status, course['title'])
                    recommendations.append({
                        "Skill": skill,
                        "Course": course['title'],
                        "Duration (weeks)": course['duration_weeks'],
                        "Status": status,
                        "Summary": summary
                    })
        return recommendations

class LearningRoadmapAgent:
    def process(self, recommendations):
        roadmap = []
        week_counter = 1
        for rec in recommendations:
            roadmap.append({
                "Skill": rec["Skill"],
                "Course": rec["Course"],
                "Start Week": week_counter,
                "End Week": week_counter + rec["Duration (weeks)"] - 1
            })
            week_counter += rec["Duration (weeks)"]
        return roadmap

# -------------------------
# Ranking Function
# -------------------------
def rank_courses(recommendations):
    ranked = []
    for rec in recommendations:
        priority = rec["Duration (weeks)"]/100
        rec["Priority"] = priority
        ranked.append(rec)
    ranked_sorted = sorted(ranked, key=lambda x: x["Priority"])
    return ranked_sorted

# -------------------------
# Sample Input
# -------------------------
user_skills = {
    "Python": "Beginner",
    "SQL": "Intermediate",
    "Excel": "Advanced"
}

# -------------------------
# Workflow
# -------------------------
# Profile skills
skill_agent = SkillProfilingAgent()
user_skills = skill_agent.process(user_skills)

# Gap analysis
gap_agent = GapAnalysisAgent()
gaps = gap_agent.process(user_skills, skills_db)

# Recommend courses with Gemini summaries
course_agent = CourseRecommendationAgent()
recommendations = course_agent.process(gaps)
ranked_recommendations = rank_courses(recommendations)

# Learning roadmap
roadmap_agent = LearningRoadmapAgent()
roadmap = roadmap_agent.process(ranked_recommendations)

# Generate final report
def generate_final_report(user_skills, gaps, recommendations, roadmap):
    report = "Skills Development Report\n\n"
    report += "Current Skills:\n"
    for skill, level in user_skills.items():
        report += f"- {skill}: {level}\n"
    report += "\nSkill Gaps:\n"
    for skill, status in gaps.items():
        if status == "Needs Improvement":
            report += f"- {skill}: {status}\n"
    report += "\nRecommended Courses:\n"
    for rec in recommendations:
        report += f"- {rec['Skill']}: {rec['Course']} ({rec['Duration (weeks)']} weeks)\n"
        report += f"  Summary: {rec['Summary']}\n"
    report += "\nLearning Roadmap:\n"
    for step in roadmap:
        report += f"- Week {step['Start Week']} to {step['End Week']}: {step['Skill']} - {step['Course']}\n"
    return report

final_report = generate_final_report(user_skills, gaps, ranked_recommendations, roadmap)

# -------------------------
# Display Outputs
# -------------------------
print("=== Current Skills ===")
print(user_skills)

print("\n=== Skill Gaps ===")
display(pd.DataFrame([{"Skill": s, "Status": gaps[s]} for s in gaps]))

print("\n=== Ranked Course Recommendations ===")
display(pd.DataFrame(ranked_recommendations))

print("\n=== Learning Roadmap ===")
display(pd.DataFrame(roadmap))

print("\n=== Final Skills Development Report ===")
print(final_report)
