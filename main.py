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
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Create autosave directory
autosave_dir = "autosave"
os.makedirs(autosave_dir, exist_ok=True)

if __name__ == "__main__":
    def start_ui():
        try:
            print("[INFO] Creating main window...")
            root = tk.Tk()
            print("[INFO] Main window created.")

            print("[INFO] Loading KarbonUI...")
            try:
                app = KarbonUI(root)
                print("[INFO] KarbonUI loaded successfully.")
            except Exception as ui_error:
                print(f"[ERROR] Failed to load KarbonUI: {ui_error}")
                root.destroy()
                sys.exit(1)

            app.autosave_dir = autosave_dir  # attach for access in save_settings()

            def on_closing():
                print("[INFO] Saving settings before exit...")
                try:
                    app.save_settings()
                except Exception as save_error:
                    print(f"[WARNING] Failed to save settings: {save_error}")
                root.destroy()

            root.protocol("WM_DELETE_WINDOW", on_closing)
            print("[INFO] Karbon UI started. Window should be visible now.")
            root.mainloop()

        except Exception as e:
            print(f"[ERROR] Unexpected crash: {e}")

    start_ui()
