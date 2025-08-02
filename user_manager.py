import os
import json
from tkinter import Tk, simpledialog, messagebox

USERS_DIR = "users"

def select_or_create_user():
    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)

    existing_users = [d for d in os.listdir(USERS_DIR) if os.path.isdir(os.path.join(USERS_DIR, d))]

    root = Tk()
    root.withdraw()

    if existing_users:
        msg = f"Existing users: {', '.join(existing_users)}\nEnter your username (new or existing):"
    else:
        msg = "No users found. Enter a new username to create your profile:"

    username = simpledialog.askstring("Select or Create User", msg)

    if not username:
        messagebox.showerror("No Username", "Username is required to continue.")
        exit()

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
