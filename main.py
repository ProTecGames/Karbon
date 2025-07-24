import tkinter as tk
import threading
from ui_items.karbon_ui import KarbonUI
from web_server.server import webview_main
import sys
import os

# Function to get the correct path for bundled data files
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    def start_ui():
        root = tk.Tk()
        app = KarbonUI(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()

    # Run Tkinter in a separate thread
    ui_thread = threading.Thread(target=start_ui)
    ui_thread.daemon = True
    ui_thread.start()

    # Run Flask and webview in the main thread
    webview_main()
