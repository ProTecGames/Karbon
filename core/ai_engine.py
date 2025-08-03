
import json
import re
import logging
import requests
import google.generativeai as genai
from meta_ai_api import MetaAI
from fuzzy_json import loads as fuzzy_loads

logging.basicConfig(
    filename="karbon_ai_errors.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

ai_status = {"state": "connecting", "message": "Connecting to AI service..."}

def set_ai_status(state: str, message: str):
    ai_status["state"] = state
    ai_status["message"] = message
    logging.info(f"AI Status Updated: {state} - {message}")

def extract_json(response: str) -> dict:
    """
    Extract and parse JSON from the AI response, handling malformed input.
    
    Args:
        response (str): Raw response from the AI service.
    
    Returns:
        dict: Parsed JSON object with 'html', 'css', 'js', and 'name' keys.
    
    Raises:
        ValueError: If JSON parsing fails or the structure is invalid.
    """
    if not response or response.isspace():
        logging.error("Empty AI response received")
        raise ValueError("Empty response from AI service")

    logging.info("Raw AI response: %s", response)

    # Remove markdown formatting
    cleaned_response = re.sub(r'```json\s*|\s*```', '', response, flags=re.DOTALL)
    cleaned_response = re.sub(r'^\s*```|```\s*$', '', cleaned_response, flags=re.DOTALL).strip()

    logging.info("Cleaned AI response: %s", cleaned_response[:500])

    # Extract first valid JSON object from the string
    try:
        stack = []
        start_idx = None
        for i, char in enumerate(cleaned_response):
            if char == '{':
                if not stack:
                    start_idx = i
                stack.append(char)
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack:
                        json_block = cleaned_response[start_idx:i + 1]
                        break
        else:
            raise ValueError("No valid JSON object found in response.")

        logging.info("Extracted JSON block: %s", json_block[:500])

        parsed = json.loads(json_block)

        expected_keys = {"html", "css", "js", "name"}
        if not isinstance(parsed, dict) or not expected_keys.issubset(parsed.keys()):
            raise ValueError(f"Parsed JSON does not contain expected keys: {expected_keys}")
        return parsed
    except json.JSONDecodeError as e:
        logging.warning(f"Initial JSON parse failed: {e}")
    except Exception as general_e:
        logging.error(f"JSON extraction logic failed: {general_e}")

    # Try fuzzy JSON parser
    try:
        parsed = fuzzy_loads(cleaned_response)
        expected_keys = {"html", "css", "js", "name"}
        if not isinstance(parsed, dict) or not expected_keys.issubset(parsed.keys()):
            raise ValueError(f"Fuzzy JSON parse does not contain expected keys: {expected_keys}")
        logging.info("Successfully parsed JSON using fuzzy-json")
        return parsed
    except Exception as fuzzy_e:
        logging.error(f"Fuzzy JSON parse failed: {fuzzy_e}")
        logging.error(f"Cleaned response: {cleaned_response}")
        raise ValueError("Failed to parse AI response as JSON.")

def generate_code_from_prompt(prompt: str, api_key: str = None, retries=2) -> str:
    formatted = (
        f"You are a helpful assistant that writes complete frontend apps.\n"
        f"Given the task: \"{prompt}\"\n"
        f"Respond ONLY in this JSON format, with no additional text, markdown, or explanation before or after the JSON:\n"
        "{\n"
        "  \"html\": \"<html>...</html>\",\n"
        "  \"css\": \"body { ... }\",\n"
        "  \"js\": \"document.addEventListener(...)\",\n"
        "  \"name\": \"App Name\"\n"
        "}\n"
        "IMPORTANT: Do NOT include markdown (like ```json) or any trailing explanation or comments. Only return pure JSON."
    )

    for attempt in range(retries + 1):
        try:
            set_ai_status("generating", "Generating code...")
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(formatted).text
                    logging.info(f"[Gemini] Raw AI response: {response}")
                except Exception as gem_e:
                    logging.warning(f"[Gemini Fallback] Gemini failed: {gem_e}. Falling back to Meta AI.")
                    api_key = None
                    continue

            if not api_key:
                ai = MetaAI()
                result = ai.prompt(message=formatted)
                response = result.get("message", "")
                logging.info(f"[MetaAI] Raw AI response: {response}")

            parsed = extract_json(response)
            if not parsed:
                raise ValueError("AI response couldn't be parsed into JSON.")

            set_ai_status("online", "AI service is online.")
            html = str(parsed.get("html", ""))
            css = str(parsed.get("css", ""))
            js = str(parsed.get("js", ""))

            final_code = html.replace("</head>", f"<style>{css}</style></head>") \
                             .replace("</body>", f"<script>{js}</script></body>")
            logging.info(f"Final inlined HTML code (first 500 chars): {str(final_code)[:500]}...")
            return final_code
        except Exception as e:
            logging.error(f"[AI Error] Attempt {attempt + 1} failed: {str(e)}")
            set_ai_status("error", f"AI error: {str(e)}")
            import time
            time.sleep(2 ** attempt)

    set_ai_status("offline", "All attempts to use AI failed.")
    return "<!DOCTYPE html><html><head><title>Error</title><style></style></head><body><h1>AI service is currently unavailable.</h1></body></html>"

def optimize_prompt(prompt: str, api_key: str = None) -> str:
    print("[optimize_prompt] Called with:", prompt)
    if len(prompt.strip()) >= 20 and not is_generic(prompt):
        return prompt

    try:
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            enriched = model.generate_content(
                f"Transform the following vague or minimal UI prompt into a clear, detailed, and professional instruction specifically for frontend web development. "
                f"Focus on HTML, CSS, and JavaScript. Include layout details, components to be included, styling considerations, and any interactivity if relevant. "
                f"Keep the improved prompt concise yet specific. Do not add commentary or formatting:\n\n"
                f"User Prompt: \"{prompt.strip()}\"\n\n"
                f"Refined Prompt:"
            ).text.strip()
            if enriched:
                return enriched
    except Exception as e:
        logging.error(f"optimize_prompt failed with Gemini: {str(e)}")
    return rule_based_enhancement(prompt)

def rule_based_enhancement(prompt: str) -> str:
    prompt = prompt.strip()
    return f"{prompt}\n\nUse semantic HTML5 structure.\nApply responsive CSS (mobile-first).\nInclude clean modular JavaScript with comments."

def is_generic(prompt: str) -> bool:
    generic_phrases = {
        "make a website", "build ui", "create page", "webpage", "dashboard", "login", "landing page"
    }
    return prompt.lower().strip() in generic_phrases
