import tkinter as tk
from ui_items.karbon_ui import KarbonUI
from user_manager import select_or_create_user

if __name__ == "__main__":
    # Before launching Karbon UI
    CURRENT_USER = select_or_create_user()

    # Launch Tkinter UI
    root = tk.Tk()
    app = KarbonUI(root, user=CURRENT_USER)
    root.mainloop()
import tkinter as tk

# Define theme dictionaries
LIGHT_THEME = {
    "bg": "#ffffff",
    "fg": "#000000",
    "button_bg": "#e0e0e0",
    "button_fg": "#000000"
}

DARK_THEME = {
    "bg": "#2e2e2e",
    "fg": "#ffffff",
    "button_bg": "#555555",
    "button_fg": "#ffffff"
}

# Track current theme
current_theme = LIGHT_THEME

def apply_theme(widgets, theme):
    for widget in widgets:
        widget.configure(bg=theme["bg"], fg=theme["fg"])
        if isinstance(widget, tk.Button):
            widget.configure(bg=theme["button_bg"], fg=theme["button_fg"])

def toggle_theme(widgets, root):
    global current_theme
    current_theme = DARK_THEME if current_theme == LIGHT_THEME else LIGHT_THEME
    root.configure(bg=current_theme["bg"])
    apply_theme(widgets, current_theme)