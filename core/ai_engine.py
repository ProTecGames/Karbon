import json
import re
import logging
import requests
import google.generativeai as genai
from meta_ai_api import MetaAI

# Configure logging
logging.basicConfig(
    filename="karbon_ai_errors.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# Global AI status
ai_status = {"state": "connecting", "message": "Connecting to AI service..."}

def set_ai_status(state: str, message: str):
    """Update AI status with proper error handling."""
    ai_status["state"] = state
    ai_status["message"] = message
    logging.info(f"AI Status Updated: {state} - {message}")

def extract_json(response: str) -> dict:
    """
    Extract and parse JSON from the AI response with improved error handling.
    """
    if not response or response.isspace():
        logging.error("Empty AI response received")
        raise ValueError("Empty response from AI service")
    
    logging.info("Raw AI response length: %d", len(response))
    
    # Clean the response more thoroughly
    cleaned_response = response.strip()
    
    # Remove markdown code blocks
    cleaned_response = re.sub(r'```json\s*', '', cleaned_response, flags=re.IGNORECASE)
    cleaned_response = re.sub(r'```\s*$', '', cleaned_response, flags=re.MULTILINE)
    cleaned_response = re.sub(r'^```|```$', '', cleaned_response, flags=re.MULTILINE)
    
    # Remove any leading/trailing non-JSON text
    cleaned_response = cleaned_response.strip()
    
    logging.info("Cleaned response preview: %s", cleaned_response[:200] + "..." if len(cleaned_response) > 200 else cleaned_response)
    
    # Try multiple JSON extraction strategies
    strategies = [
        lambda x: x,  # Try as-is first
        lambda x: find_json_block(x),  # Find JSON block
        lambda x: extract_between_braces(x),  # Extract content between first { and last }
    ]
    
    for i, strategy in enumerate(strategies):
        try:
            candidate = strategy(cleaned_response)
            if not candidate:
                continue
                
            logging.info(f"Strategy {i+1} candidate: %s", candidate[:200] + "..." if len(candidate) > 200 else candidate)
            
            # Parse JSON
            parsed = json.loads(candidate)
            
            # Validate structure
            if validate_json_structure(parsed):
                logging.info("Successfully extracted and validated JSON")
                return parsed
            else:
                logging.warning(f"Strategy {i+1}: JSON structure validation failed")
                
        except json.JSONDecodeError as e:
            logging.warning(f"Strategy {i+1}: JSON decode failed - {e}")
            continue
        except Exception as e:
            logging.warning(f"Strategy {i+1}: General error - {e}")
            continue
    
    # If all strategies fail, try to create a minimal valid response
    logging.error("All JSON extraction strategies failed")
    raise ValueError("Failed to extract valid JSON from AI response")

def find_json_block(text: str) -> str:
    """Find the first complete JSON object in the text."""
    brace_count = 0
    start_idx = None
    
    for i, char in enumerate(text):
        if char == '{':
            if brace_count == 0:
                start_idx = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_idx is not None:
                return text[start_idx:i + 1]
    
    return ""

def extract_between_braces(text: str) -> str:
    """Extract content between the first { and last }."""
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    
    if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
        return text[first_brace:last_brace + 1]
    
    return ""

def validate_json_structure(parsed: dict) -> bool:
    """Validate that the parsed JSON has the expected structure."""
    if not isinstance(parsed, dict):
        return False
    
    required_keys = {"html", "css", "js", "name"}
    if not required_keys.issubset(parsed.keys()):
        logging.warning(f"Missing required keys. Expected: {required_keys}, Got: {set(parsed.keys())}")
        return False
    
    # Check that values are strings
    for key in required_keys:
        if not isinstance(parsed[key], str):
            logging.warning(f"Key '{key}' is not a string: {type(parsed[key])}")
            return False
    
    return True

def create_fallback_response(prompt: str) -> dict:
    """Create a basic fallback response when AI fails."""
    return {
        "html": f"<!DOCTYPE html><html><head><title>Generated App</title></head><body><h1>Welcome</h1><p>App generated from: {prompt[:100]}{'...' if len(prompt) > 100 else ''}</p></body></html>",
        "css": "body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }",
        "js": "console.log('App loaded successfully');",
        "name": "Generated App"
    }

def generate_code_from_prompt(prompt: str, api_key: str = None, retries: int = 3) -> str:
    """
    Generate code from prompt with improved error handling and fallbacks.
    """
    formatted_prompt = (
        f"Create a complete web application for: {prompt}\n\n"
        f"Respond with ONLY a JSON object in this exact format (no markdown, no extra text):\n"
        "{\n"
        '  "html": "<!DOCTYPE html><html>...</html>",\n'
        '  "css": "body { ... }",\n'
        '  "js": "// JavaScript code here",\n'
        '  "name": "App Name"\n'
        "}\n\n"
        "CRITICAL: Return ONLY the JSON object, no explanations, no markdown formatting."
    )
    
    last_error = None
    
    for attempt in range(retries + 1):
        try:
            set_ai_status("generating", f"Generating code (attempt {attempt + 1})...")
            response = None
            
            # Try Gemini first if API key provided
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.0-flash-exp')
                    result = model.generate_content(formatted_prompt)
                    response = result.text
                    logging.info("Gemini response received")
                except Exception as gem_e:
                    logging.warning(f"Gemini failed: {gem_e}")
                    last_error = gem_e
            
            # Fallback to Meta AI
            if not response:
                try:
                    ai = MetaAI()
                    result = ai.prompt(message=formatted_prompt)
                    response = result.get("message", "")
                    logging.info("Meta AI response received")
                except Exception as meta_e:
                    logging.warning(f"Meta AI failed: {meta_e}")
                    last_error = meta_e
            
            if not response:
                raise Exception("No response from any AI service")
            
            # Extract and validate JSON
            parsed = extract_json(response)
            
            # Create final HTML with inlined CSS and JS
            html = parsed.get("html", "")
            css = parsed.get("css", "")
            js = parsed.get("js", "")
            
            # Ensure HTML has proper structure
            if not html.strip().startswith("<!DOCTYPE html>"):
                html = f"<!DOCTYPE html><html><head><title>{parsed.get('name', 'Generated App')}</title></head><body>{html}</body></html>"
            
            # Inline CSS and JS
            if css and "<style>" not in html:
                html = html.replace("</head>", f"<style>{css}</style></head>")
            
            if js and "<script>" not in html:
                html = html.replace("</body>", f"<script>{js}</script></body>")
            
            set_ai_status("online", "AI service is online")
            logging.info("Successfully generated code")
            return html
            
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed: {str(e)}")
            last_error = e
            set_ai_status("error", f"Attempt {attempt + 1} failed: {str(e)}")
            
            # Wait before retry (exponential backoff)
            if attempt < retries:
                import time
                wait_time = min(2 ** attempt, 10)  # Cap at 10 seconds
                time.sleep(wait_time)
    
    # All attempts failed - create fallback response
    logging.error("All attempts failed, creating fallback response")
    set_ai_status("offline", f"AI service unavailable: {str(last_error)}")
    
    fallback = create_fallback_response(prompt)
    return fallback["html"].replace("</head>", f"<style>{fallback['css']}</style></head>").replace("</body>", f"<script>{fallback['js']}</script></body>")

def optimize_prompt(prompt: str, api_key: str = None) -> str:
    """
    Optimize vague prompts with better error handling.
    """
    print(f"[optimize_prompt] Input: {prompt}")
    
    # If prompt is already detailed enough, return as-is
    if len(prompt.strip()) >= 20 and not is_generic(prompt):
        return prompt.strip()
    
    optimization_prompt = (
        f"Transform this brief UI request into a detailed web development specification: '{prompt.strip()}'\n\n"
        f"Include:\n"
        f"- Specific layout and components\n"
        f"- Visual styling preferences\n"
        f"- Any interactive features\n"
        f"- Target audience considerations\n\n"
        f"Return only the enhanced prompt, no explanations."
    )
    
    try:
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            result = model.generate_content(optimization_prompt)
            enhanced = result.text.strip()
            
            if enhanced and len(enhanced) > len(prompt):
                logging.info("Prompt successfully optimized with Gemini")
                return enhanced
                
    except Exception as e:
        logging.warning(f"Prompt optimization failed: {e}")
    
    # Fallback to rule-based enhancement
    return rule_based_enhancement(prompt)

def rule_based_enhancement(prompt: str) -> str:
    """
    Rule-based prompt enhancement as fallback.
    """
    prompt = prompt.strip()
    
    enhancements = [
        "Use modern HTML5 semantic structure with proper accessibility.",
        "Apply responsive CSS with mobile-first approach and modern design principles.",
        "Include interactive JavaScript features with smooth animations.",
        "Ensure clean, professional styling with good typography and color scheme."
    ]
    
    return f"{prompt}\n\n" + " ".join(enhancements)

def is_generic(prompt: str) -> bool:
    """
    Check if prompt is too generic and needs enhancement.
    """
    generic_phrases = {
        "make a website", "build ui", "create page", "webpage", 
        "dashboard", "login", "landing page", "app", "site"
    }
    
    prompt_lower = prompt.lower().strip()
    return any(phrase in prompt_lower for phrase in generic_phrases) and len(prompt_lower) < 30

