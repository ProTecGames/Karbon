import tkinter as tk
import threading
from ui_items.karbon_ui import KarbonUI
import sys
import os

from user_manager import select_or_create_user
import os

# Step 1: Ask user to select/create a profile
CURRENT_USER = select_or_create_user()

# Step 2: Create user-specific directories
USER_BASE_PATH = os.path.join("users", CURRENT_USER)
PROJECTS_PATH = os.path.join(USER_BASE_PATH, "projects")
HISTORY_PATH = os.path.join(USER_BASE_PATH, "history.json")
PREFS_PATH = os.path.join(USER_BASE_PATH, "preferences.json")

os.makedirs(PROJECTS_PATH, exist_ok=True)  # Ensure projects directory exists



# Function to get the correct path for bundled data files
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

import os

# Step 1: Create autosave directory
autosave_dir = "autosave"
os.makedirs(autosave_dir, exist_ok=True)




if __name__ == "__main__":
    def start_ui():
        root = tk.Tk()
        app = KarbonUI(root)
        # --- MODIFIED: Add protocol handler to save settings on close ---
        def on_closing():
            app.save_settings()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        # --- END MODIFIED ---
        root.mainloop()

    # Run the UI
    start_ui()