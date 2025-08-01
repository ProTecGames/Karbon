import json
import re
import logging
import requests
import google.generativeai as genai
from meta_ai_api import MetaAI

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
    clean_response = response.strip()
    if clean_response.startswith("```json"):
        clean_response = clean_response[len("```json"):].strip()
    if clean_response.endswith("```"):
        clean_response = clean_response[:-len("```")].strip()

    try:
        return json.loads(clean_response)
    except json.JSONDecodeError as e:
        logging.error(f"JSONDecodeError on cleaned string: {e}")
        match = re.search(r'\{.*\}', clean_response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError as e_inner:
                logging.error(f"JSONDecodeError during regex fallback: {e_inner}")
        logging.error(f"No valid JSON found in response: {response}")
        return None


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
        "}"
    )

    for attempt in range(retries + 1):
        try:
            set_ai_status("generating", "Generating code...")
            if api_key:
                # Try Gemini
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(formatted).text
                    logging.info(f"[Gemini] Raw AI response: {response}")
                except Exception as gem_e:
                    logging.warning(f"[Gemini Fallback] Gemini failed: {gem_e}. Falling back to Meta AI.")
                    api_key = None  # Force fallback
                    continue
            if not api_key:
                # Fallback to Meta AI
                ai = MetaAI()
                result = ai.prompt(message=formatted)
                response = result.get("message", "")
                logging.info(f"[MetaAI] Raw AI response: {response}")

            parsed = extract_json(response)
            if not parsed:
                raise ValueError("AI response couldn't be parsed into JSON.")

            set_ai_status("online", "AI service is online.")
            html = parsed.get("html", "")
            css = parsed.get("css", "")
            js = parsed.get("js", "")

            final_code = html.replace("</head>", f"<style>{css}</style></head>") \
                             .replace("</body>", f"<script>{js}</script></body>")
            logging.info(f"Final inlined HTML code (first 500 chars): {final_code[:500]}...")
            return final_code
        except Exception as e:
            logging.error(f"[AI Error] Attempt {attempt + 1} failed: {e}")
            set_ai_status("error", f"AI error: {e}")
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
        logging.error(f"optimize_prompt failed with Gemini: {e}")
    return rule_based_enhancement(prompt)


def rule_based_enhancement(prompt: str) -> str:
    prompt = prompt.strip()
    return f"{prompt}\n\nUse semantic HTML5 structure.\nApply responsive CSS (mobile-first).\nInclude clean modular JavaScript with comments."


def is_generic(prompt: str) -> bool:
    generic_phrases = {
        "make a website", "build ui", "create page", "webpage", "dashboard", "login", "landing page"
    }
    return prompt.lower().strip() in generic_phrases
