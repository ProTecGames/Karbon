import datetime
import json
from tkinter import filedialog

def create_project_data(prompt, html, css, js):
    project_data = {
        "prompt": prompt,
        "html_code": html,
        "css_code": css,
        "js_code": js,
        "last_modified": datetime.datetime.now().isoformat()
    }
    return project_data


def save_project_to_file(project_data):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".karbonproject",
        filetypes=[("Karbon Project Files", "*.karbonproject")],
        title="Save Your Karbon Project"
    )
    
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=4)
        return file_path
    return None

def save_project(code_input):
    full_code = code_input.get("1.0", "end-1c")

    # You can later parse HTML, CSS, JS separately if needed
    project_data = create_project_data(
        prompt="User's original prompt (if any)",
        html=full_code,
        css="",
        js=""
    )

    save_project_to_file(project_data)
