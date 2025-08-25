import os
import json
import tkinter as tk
from tkinter import messagebox

USERS_DIR = "users"

def select_or_create_user():
    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)

    existing_users = [d for d in os.listdir(USERS_DIR) if os.path.isdir(os.path.join(USERS_DIR, d))]

    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Create custom dark-themed dialog
    dialog = tk.Toplevel()
    dialog.title("User Login")
    dialog.configure(bg="#161921")
    dialog.resizable(False, False)

    # --- Center dialog on screen ---
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() - dialog.winfo_reqwidth()) // 2
    y = (dialog.winfo_screenheight() - dialog.winfo_reqheight()) // 2
    dialog.geometry(f"+{x}+{y}")

    # Prompt label
    prompt_label = tk.Label(dialog, text="Enter username:",
                            fg="white", bg="#161921",
                            font=("Segoe UI", 10, "bold"))
    prompt_label.pack(pady=(15, 5))

    # Entry field
    username_entry = tk.Entry(dialog, font=("Segoe UI", 10),
                            bg="#202329", fg="white", insertbackground="white",
                            width=30, relief=tk.SOLID,
                            highlightbackground="white", highlightthickness=3,
                            justify="center")
    username_entry.pack(pady=5, padx=20, ipady=4)


    result = {"username": None}


    def on_ok():
        username = username_entry.get().strip()
        if not username:   # empty input
            messagebox.showerror("Invalid Username", "Username cannot be empty.")
            return
        result["username"] = username
        root.quit()
        dialog.destroy()


    def on_cancel():
        dialog.destroy()
        root.destroy()
        exit()

    # Buttons frame
    btn_frame = tk.Frame(dialog, bg="#161921")
    btn_frame.pack(pady=15)

    ok_btn = tk.Button(btn_frame, text="OK", command=on_ok, bg="#5c9dff", fg="white", font=("Segoe UI", 9, "bold"), width=10, relief=tk.FLAT)
    ok_btn.pack(side=tk.LEFT, padx=10)

    cancel_btn = tk.Button(btn_frame, text="Cancel", command=on_cancel, bg="#3a3a3a", fg="white", font=("Segoe UI", 9), width=10, relief=tk.FLAT)
    cancel_btn.pack(side=tk.LEFT, padx=10)

    dialog.grab_set()
    root.wait_window(dialog)

    username = result["username"]

    # Create user folders/files if needed
    user_path = os.path.join(USERS_DIR, username)
    os.makedirs(user_path, exist_ok=True)

    prefs_file = os.path.join(user_path, "preferences.json")
    if not os.path.exists(prefs_file):
        with open(prefs_file, "w") as f:
            json.dump({"theme": "light", "font_size": 12}, f)

    history_file = os.path.join(user_path, "history.json")
    if not os.path.exists(history_file):
        with open(history_file, "w") as f:
            json.dump([], f)

    projects_dir = os.path.join(user_path, "projects")
    os.makedirs(projects_dir, exist_ok=True)

    return username


if __name__ == "__main__":
    user = select_or_create_user()
    print(f"Logged in as: {user}")
