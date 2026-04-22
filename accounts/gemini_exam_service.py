import json
import logging
from django.conf import settings
from google import genai

logger = logging.getLogger(__name__)

def generate_assessment_questions(category_name):
    """
    Uses Gemini API to generate 10 multiple choice questions for the given category.
    Returns a list of dictionaries with question data.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        logger.error("GEMINI_API_KEY not set. Cannot generate questions.")
        return []

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        You are an expert technical examiner.
        Generate exactly 10 multiple-choice questions to assess a user's skill level in: {category_name}.
        The questions should range from beginner to advanced difficulty.
        
        CRITICAL REQUIREMENT:
        - 9 of the questions should be standard multiple-choice knowledge checks.
        - Exactly 1 of the questions MUST be a complex "Real-Time Problem Solving Scenario". Describe a complex scenario or show a piece of code/architecture, and ask the user how to solve the specific problem or what the output will be.
        
        Return ONLY a JSON array of objects. Do not use markdown blocks (like ```json).
        Each object MUST have the following keys:
        - "question_text": The question itself (can be long for the scenario).
        - "option_a": First choice.
        - "option_b": Second choice.
        - "option_c": Third choice.
        - "option_d": Fourth choice.
        - "correct_option": A single character "A", "B", "C", or "D" indicating the correct answer.
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        try:
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            questions = json.loads(response_text)
            
            if isinstance(questions, list) and len(questions) > 0:
                return questions
            else:
                logger.error(f"Gemini returned an empty or invalid list: {response_text}")
                return []
                
        except json.JSONDecodeError:
            logger.error(f"Failed to parse Gemini exam response: {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Gemini API error during exam generation: {str(e)}")
        return []
