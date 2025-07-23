import json
import re
import logging
import requests
from meta_ai_api import MetaAI



logging.basicConfig(
    filename = "karbon_ai_errors.log",
    level = logging.INFO,
    format = "%(asctime)s %(levelname)s %(message)s"
)

ai_status = {"state": "connecting", "message": "Connecting to AI service..."}

def set_ai_status(state: str, message: str):
    ai_status["state"] = state
    ai_status["message"] = message
    logging.info(f"AI Status Updated: {state} - {message}")

def extract_json(response: str) -> dict:
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        match = re.search(r'\{.*?\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return None

def generate_code_from_prompt(prompt: str, retries = 2) -> str:
    formatted = (
        f"You are a helpful assistant that writes complete frontend apps.\n"
        f"Given the task: \"{prompt}\"\n"
        f"Respond ONLY in this JSON format:\n"
        "{\n"
        "  \"html\": \"<html>...</html>\",\n"
        "  \"css\": \"body { ... }\",\n"
        "  \"js\": \"document.addEventListener(...)\",\n"
        "  \"name\": \"App Name\"\n"
        "}\n"
        "No markdown, no explanation, only raw JSON."
    )
    last_exception = None
    try:
        set_ai_status("connecting", "Connecting to AI service...")
        meta = MetaAI()
    except Exception as e:
        set_ai_status("error", f"AI service unavailable (no internet connection).")
        logging.error(f"MetaAI init failed: {e}")
        return "<!DOCTYPE html><html><head><title>Error</title><style></style></head><body><h1>AI service is currently unavailable.</h1></body></html>"

    for attempt in range(retries + 1):
        try:
            set_ai_status("generating", "Connecting to AI service...")
            result = meta.prompt(formatted)
            response = result.get("message", "")
            parsed = extract_json(response)

            if not parsed:
                set_ai_status("error", "Could not parse AI response.")
                return "<!DOCTYPE html><html><head><title>Error</title><style></style></head><body><h1>Could not parse AI response.</h1><script></script></body></html>"
            set_ai_status("online", "AI service is online.")
            html = parsed.get("html", "")
            css = parsed.get("css", "")
            js = parsed.get("js", "")

            final_code = html.replace("</head>", f"<style>{css}</style></head>").replace("</body>", f"<script>{js}</script></body>")
            return final_code
        except requests.exceptions.RequestException as e:
            last_exception = e
            set_ai_status("offline", "Network error, AI service is offline.")
            logging.error(f"AI API network error: {e}")
        except Exception as e:
            last_exception = e
            set_ai_status("error", f"AI service error: {e}")
            logging.error(f"AI API error: {e}")
        import time
        time.sleep(2 ** attempt)
    set_ai_status("offline", f"AI service unavailable: {last_exception}.")
    return "<!DOCTYPE html><html><head><title>Error</title><style></style></head><body><h1>AI service is currently unavailable.</h1></body></html>"