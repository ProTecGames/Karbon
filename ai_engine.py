import json
import re
from meta_ai_api import MetaAI

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

def generate_code_from_prompt(prompt: str, api_key: str = None, model_source: str = None) -> str:
    # Use the provided API key and model source, otherwise use defaults
    meta = MetaAI(api_key=api_key, model_source=model_source)

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

    result = meta.prompt(formatted)
    response = result.get("message", "")
    parsed = extract_json(response)

    if not parsed:
        return "<!DOCTYPE html><html><head><title>Error</title><style></style></head><body><h1>Could not parse AI response.</h1><script></script></body></html>"

    html = parsed.get("html", "")
    css = parsed.get("css", "")
    js = parsed.get("js", "")

    final_code = html.replace("</head>", f"<style>{css}</style></head>").replace("</body>", f"<script>{js}</script></body>")
    return final_code
