import os
import zipfile
from datetime import datetime
from tkinter import filedialog

from core.token_manager import get_token, NETLIFY_SERVICE, VERCEL_SERVICE


def export_code(code: str, as_zip: bool = False):
    """
    Export generated code locally as HTML or ZIP.

    Args:
        code (str): The generated HTML code.
        as_zip (bool): If True, export as ZIP. Otherwise, export as index.html.

    Returns:
        str: Path to the exported file/folder, or None if cancelled.
    """
    folder_selected = filedialog.askdirectory(title="Select Export Folder")
    if not folder_selected:
        return None

    if as_zip:
        export_name = f"karbon_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(folder_selected, export_name)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("index.html", code)

        print(f"✅ Code exported as ZIP: {zip_path}")
        return zip_path
    else:
        html_path = os.path.join(folder_selected, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(code)

        print(f"✅ Code exported as HTML: {html_path}")
        return html_path
