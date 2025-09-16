#!/usr/bin/env python3
"""Test script to debug LLM connection and response parsing"""

import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

def test_llm_connection():
    """Test basic LLM connection"""
    print("🔍 Testing LLM Connection...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"API Key Status: {'SET' if api_key else 'NOT SET'}")
    
    if not api_key:
        print("❌ No API key found!")
        return False
    
    try:
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            openai_api_key=api_key
        )
        print("✅ LLM initialized successfully")
        
        # Test simple message
        test_message = "Hello, can you respond with just 'Hello back'?"
        response = llm.invoke([HumanMessage(content=test_message)])
        print(f"✅ LLM Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        return False

def test_feedback_analysis():
    """Test the actual feedback analysis prompt"""
    print("\n🔍 Testing Feedback Analysis Prompt...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No API key found!")
        return False
    
    try:
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            openai_api_key=api_key
        )
        
        # Use the exact prompt from the application
        feedback_text = "John has been doing well this quarter. He completed his projects on time and showed good communication skills."
        
        prompt = f"""
You are an AI assistant helping managers write better performance feedback. Analyze the feedback text and provide structured suggestions.

Feedback Text: "{feedback_text}"

Please provide your analysis in this exact JSON format:
{{
    "quality_score": <number from 1-10>,
    "tone_analysis": {{
        "overall_tone": "<constructive/critical/neutral/positive>",
        "constructiveness_score": <number from 1-10>,
        "balance_score": <number from 1-10>
    }},
    "specificity_suggestions": [
        "<specific suggestion 1>",
        "<specific suggestion 2>",
        "<specific suggestion 3>"
    ],
    "missing_areas": [
        "<missing area 1>",
        "<missing area 2>",
        "<missing area 3>"
    ],
    "actionability_suggestions": [
        "<actionable suggestion 1>",
        "<actionable suggestion 2>",
        "<actionable suggestion 3>"
    ],
    "overall_recommendations": "<brief summary of key improvements needed>"
}}

Focus on:
- Making feedback more specific and measurable
- Ensuring constructive tone
- Adding missing performance areas (communication, leadership, technical skills, etc.)
- Making suggestions actionable
- Balancing positive and improvement areas
"""
        
        print("📝 Sending prompt to LLM...")
        response = llm.invoke([HumanMessage(content=prompt)])
        ai_response = response.content.strip()
        
        print(f"🤖 Raw LLM Response:")
        print("=" * 50)
        print(ai_response)
        print("=" * 50)
        
        # Try to parse JSON
        try:
            # First try direct JSON parsing
            analysis_data = json.loads(ai_response)
            print("✅ Successfully parsed JSON response!")
            print(f"📊 Quality Score: {analysis_data.get('quality_score')}")
            return True
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            try:
                import re
                # Look for JSON within ```json ... ``` blocks
                json_match = re.search(r'```json\s*\n(.*?)\n```', ai_response, re.DOTALL)
                if json_match:
                    json_content = json_match.group(1).strip()
                    analysis_data = json.loads(json_content)
                    print("✅ Successfully parsed JSON from markdown block!")
                    print(f"📊 Quality Score: {analysis_data.get('quality_score')}")
                    return True
                
                # Look for JSON within ``` ... ``` blocks (without json specifier)
                json_match = re.search(r'```\s*\n(.*?)\n```', ai_response, re.DOTALL)
                if json_match:
                    json_content = json_match.group(1).strip()
                    # Check if it looks like JSON (starts with { and ends with })
                    if json_content.startswith('{') and json_content.endswith('}'):
                        analysis_data = json.loads(json_content)
                        print("✅ Successfully parsed JSON from code block!")
                        print(f"📊 Quality Score: {analysis_data.get('quality_score')}")
                        return True
                        
            except json.JSONDecodeError as json_err:
                print(f"❌ JSON parsing failed even after markdown extraction: {json_err}")
                print("🔍 This explains why the hardcoded response is returned!")
                return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting LLM Connection Tests...\n")
    
    # Test basic connection
    basic_test = test_llm_connection()
    
    if basic_test:
        # Test feedback analysis
        feedback_test = test_feedback_analysis()
        
        if feedback_test:
            print("\n✅ All tests passed! LLM should work in the application.")
        else:
            print("\n❌ Feedback analysis test failed. Check the prompt or JSON parsing.")
    else:
        print("\n❌ Basic LLM connection failed. Check API key and network.")
