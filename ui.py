import tkinter as tk
from ui_items.karbon_ui import KarbonUI

if __name__ == "__main__":
    root = tk.Tk()
    app = KarbonUI(root)
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

# Example usage in a simple UI
def main_ui():
    root = tk.Tk()
    root.title("Karbon UI")
    root.geometry("400x300")

    # Create sample widgets
    label = tk.Label(root, text="Hello, Karbon!")
    button1 = tk.Button(root, text="Do Something")
    toggle_button = tk.Button(root, text="Toggle Theme")

    # Pack widgets
    label.pack(pady=10)
    button1.pack(pady=10)
    toggle_button.pack(pady=10)

    widgets = [label, button1, toggle_button]

    # Apply initial theme
    root.configure(bg=current_theme["bg"])
    apply_theme(widgets, current_theme)

    # Bind toggle button
    toggle_button.config(command=lambda: toggle_theme(widgets, root))

    root.mainloop()

if __name__ == "__main__":
    main_ui()