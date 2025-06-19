import os
from tkinter import filedialog

def export_code(code: str):
    folder_selected = filedialog.askdirectory(title="Select Export Folder")
    if not folder_selected:
        return

    html_path = os.path.join(folder_selected, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(code)