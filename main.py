import threading
import tkinter as tk
from ui import KarbonUI
from preview import webview_main

if __name__ == "__main__":
    def start_ui():
        root = tk.Tk()
        app = KarbonUI(root)
        root.protocol("WM_DELETE_WINDOW", root.destroy)
        root.mainloop()

    threading.Thread(target=start_ui, daemon=True).start()

    # start webview in main thread
    webview_main()
