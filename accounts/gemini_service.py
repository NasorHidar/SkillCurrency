import os
import json
import logging
from django.conf import settings
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

def analyze_id_document(file_path):
    """
    Analyzes an uploaded ID document using Gemini API.
    Returns a tuple: (is_valid: bool, status: str, reason: str)
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        logger.warning("GEMINI_API_KEY not set. Falling back to manual verification.")
        return False, 'Pending', "Automated verification unavailable. Manual review required."

    try:
        client = genai.Client(api_key=api_key)
        
        # Upload the file to Gemini API securely
        uploaded_file = client.files.upload(file=file_path)
        
        prompt = """
        You are a strict security compliance officer. Your job is to verify identity documents.
        Review the attached document. 
        Determine if it is a valid, readable government-issued ID (National ID, Passport, Driver's License) or a TIN Certificate.
        Return a JSON object with exactly two keys: "status" and "reason".
        - Set "status" to "Approved" ONLY if you are extremely confident it is a valid, readable ID.
        - Set "status" to "Rejected" ONLY if you are extremely confident it is a fake, a random picture, an animal, scenery, or completely irrelevant.
        - Set "status" to "Pending" if you are unsure, if the image is blurry, partially obscured, or if you cannot make a highly confident decision either way.
        For "reason", provide a brief explanation of your decision.
        Return ONLY valid JSON and nothing else. Do not use markdown blocks for the JSON.
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[uploaded_file, prompt]
        )
        
        # Clean up the file from Gemini servers
        client.files.delete(name=uploaded_file.name)
        
        # Parse the JSON response
        try:
            # Strip markdown if present
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            result = json.loads(response_text)
            
            ai_status = result.get('status', 'Pending')
            reason = result.get('reason', 'No reason provided.')
            
            if ai_status == 'Approved':
                return True, 'Approved', reason
            elif ai_status == 'Rejected':
                return False, 'Rejected', reason
            else:
                return False, 'Pending', f"AI Unsure: {reason}. Manual review required."
                
        except json.JSONDecodeError:
            logger.error(f"Failed to parse Gemini response: {response.text}")
            return False, 'Pending', "Automated verification returned invalid format. Manual review required."
            
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return False, 'Pending', "Automated verification failed. Manual review required."
