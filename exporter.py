# import os
# from tkinter import filedialog

# def export_code(code: str):
#     folder_selected = filedialog.askdirectory(title="Select Export Folder")
#     if not folder_selected:
#         return

#     html_path = os.path.join(folder_selected, "index.html")
#     with open(html_path, "w", encoding="utf-8") as f:
#         f.write(code)
import os
from tkinter import filedialog
import zipfile
from datetime import datetime

def export_code(code: str, as_zip: bool = False):
    folder_selected = filedialog.askdirectory(title="Select Export Folder")
    if not folder_selected:
        return

    if as_zip:
        export_name = f"karbon_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(folder_selected, export_name)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("index.html", code)
        
        print(f"Exported as zip: {zip_path}")
    else:
        html_path = os.path.join(folder_selected, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Exported as HTML: {html_path}")
