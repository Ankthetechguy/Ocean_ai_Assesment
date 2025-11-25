# gemini_client.py
import os
import logging
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional

# Load optional .env
load_dotenv()

# Environment config
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Import the google.generativeai SDK
genai = None
try:
    import google.generativeai as genai
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    logging.warning("google.generativeai import failed: %s", e)
    genai = None

# Default model name
MODEL_NAME = "gemini-2.0-flash"

def call_llm(prompt: str, system_instruction: str = "", max_tokens: int = 512, temperature: float = 0.2) -> str:
    """Send prompt to Gemini and return text output."""
    
    if not GEMINI_API_KEY:
        return "ERROR_CALLING_GEMINI: GEMINI_API_KEY not set in environment"

    if genai is None:
        return "ERROR_CALLING_GEMINI: google.generativeai SDK not installed. Run: pip install google-generativeai"

    try:
        # Use the latest recommended API pattern
        model = genai.GenerativeModel(
            MODEL_NAME,
            system_instruction=system_instruction
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
        )
        
        # Extract text from response
        if hasattr(response, 'text'):
            return response.text.strip()
        elif hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                return candidate.content.parts[0].text.strip()
        elif hasattr(response, 'result'):
            return response.result.strip()
        else:
            return str(response).strip()
            
    except Exception as e:
        return f"ERROR_CALLING_GEMINI: {e}"

def test_connection() -> str:
    """Run a simple test to verify the SDK and key are functional."""
    if not GEMINI_API_KEY:
        return "ERROR_CALLING_GEMINI: GEMINI_API_KEY not set in environment"

    if genai is None:
        return "ERROR_CALLING_GEMINI: google.generativeai SDK not installed"

    try:
        result = call_llm("Say 'hello' in one word.", system_instruction="You are a helpful assistant.", max_tokens=10, temperature=0.0)
        return result
    except Exception as e:
        return f"ERROR_CALLING_GEMINI: {e}"