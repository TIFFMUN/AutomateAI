import json
import os
from typing import List, Dict, Any
from pathlib import Path

class SAPJobRecommendationService:
    """Recommendation service for matching SAP jobs based on user profile and preferences"""
    
    def __init__(self):
        self.jobs_data = self._load_jobs_data()
    
    def _load_jobs_data(self) -> List[Dict[str, Any]]:
        """Load SAP jobs data from JSON file"""
        try:
            data_file = Path(__file__).parent.parent / "data" / "sap_jobs.json"
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('sap_jobs', [])
        except Exception as e:
            print(f"Error loading jobs data: {e}")
            return []
    
    def _calculate_match_score(self, job: Dict[str, Any], user_responses: Dict[str, str]) -> float:
        """Calculate how well a job matches user responses"""
        score = 0.0
        total_weight = 0.0
        
        # Map quiz answers to job attributes
        answer_mapping = {
            'technical_expert': ['technical', 'analytical'],
            'team_lead': ['leadership', 'management', 'collaborative'],
            'management': ['leadership', 'management'],
            'entrepreneur': ['innovative', 'strategic'],
            'startup': ['innovative', 'technical'],
            'enterprise': ['systematic', 'analytical'],
            'consulting': ['collaborative', 'analytical'],
            'remote': ['remote_friendly'],
            'technical': ['technical', 'analytical'],
            'business': ['analytical', 'collaborative'],
            'leadership': ['leadership', 'management'],
            'innovation': ['innovative', 'strategic'],
            'analytical': ['analytical', 'systematic'],
            'collaborative': ['collaborative'],
            'creative': ['innovative'],
            'systematic': ['systematic', 'analytical'],
            'impact': ['leadership', 'strategic'],
            'growth': ['growth_potential'],
            'stability': ['enterprise'],
            'recognition': ['leadership', 'management']
        }
        
        # Calculate work style match
        work_style_weight = 0.4
        job_work_styles = job.get('work_style', [])
        for answer_key, answer_value in user_responses.items():
            if answer_value in answer_mapping:
                matching_styles = answer_mapping[answer_value]
                for style in matching_styles:
                    if style in job_work_styles:
                        score += work_style_weight
                total_weight += work_style_weight
        
        # Calculate environment match
        environment_weight = 0.3
        job_environments = job.get('environment', [])
        for answer_key, answer_value in user_responses.items():
            if answer_value in ['startup', 'enterprise', 'consulting', 'remote']:
                if answer_value in job_environments:
                    score += environment_weight
                total_weight += environment_weight
        
        # Calculate growth potential match
        growth_weight = 0.2
        job_growth = job.get('growth_potential', 'Medium')
        for answer_key, answer_value in user_responses.items():
            if answer_value == 'growth':
                if job_growth in ['High', 'Very High']:
                    score += growth_weight
                total_weight += growth_weight
        
        # Calculate experience level match (bonus for senior roles if leadership/management chosen)
        experience_weight = 0.1
        job_experience = job.get('experience_level', 'Mid')
        for answer_key, answer_value in user_responses.items():
            if answer_value in ['team_lead', 'management', 'leadership']:
                if job_experience in ['Senior']:
                    score += experience_weight
                total_weight += experience_weight
        
        return score / max(total_weight, 1.0)  # Normalize to 0-1
    
    def get_recommended_jobs(self, user_responses: Dict[str, str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Get top-k recommended SAP jobs based on user responses and preferences"""
        print(f"\n🔍 Recommendation Service: Starting job matching for user responses: {user_responses}")
        
        if not self.jobs_data:
            print("❌ Recommendation Service: No jobs data loaded!")
            return []
        
        print(f"📊 Recommendation Service: Analyzing {len(self.jobs_data)} SAP jobs...")
        
        # Calculate match scores for all jobs
        job_scores = []
        for job in self.jobs_data:
            score = self._calculate_match_score(job, user_responses)
            job_scores.append((job, score))
            print(f"   📋 {job['title']}: Score {score:.3f}")
        
        # Sort by score (highest first) and return top-k
        job_scores.sort(key=lambda x: x[1], reverse=True)
        top_jobs = [job for job, score in job_scores[:top_k]]
        
        print(f"\n✅ Recommendation Service: Top {top_k} matching jobs:")
        for i, (job, score) in enumerate(job_scores[:top_k], 1):
            print(f"   {i}. {job['title']} (Score: {score:.3f})")
            print(f"      Skills: {', '.join(job['skills'][:3])}...")
            print(f"      Work Style: {', '.join(job['work_style'])}")
        
        return top_jobs
    
    def get_job_context(self, relevant_jobs: List[Dict[str, Any]]) -> str:
        """Convert recommended jobs into context string for LLM"""
        print(f"\n📝 Recommendation Service: Generating context for {len(relevant_jobs)} recommended jobs...")
        
        if not relevant_jobs:
            print("❌ Recommendation Service: No recommended jobs to generate context from!")
            return "No recommended jobs found."
        
        context = "Relevant SAP job opportunities based on your profile:\n\n"
        for i, job in enumerate(relevant_jobs, 1):
            context += f"{i}. {job['title']} ({job['category']})\n"
            context += f"   Skills: {', '.join(job['skills'][:5])}\n"
            context += f"   Work Style: {', '.join(job['work_style'])}\n"
            context += f"   Environment: {', '.join(job['environment'])}\n"
            context += f"   Salary: {job['salary_range']}\n"
            context += f"   Growth: {job['growth_potential']}\n"
            context += f"   Description: {job['description']}\n\n"
        
        print(f"✅ Recommendation Service: Generated context with {len(context)} characters")
        print(f"📄 Recommendation Service: Context preview: {context[:200]}...")
        
        return context
