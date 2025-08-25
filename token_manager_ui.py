import tkinter as tk
from tkinter import messagebox
from core.token_manager import save_token, get_token, NETLIFY_SERVICE, VERCEL_SERVICE

class TokenManagerUI:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Manage Deployment Tokens")
        self.window.geometry("400x250")
        self.window.configure(bg="#0d1117")

        # Title
        tk.Label(self.window, text="🔐 Manage Deployment Tokens",
                 font=("Segoe UI", 12, "bold"), bg="#0d1117", fg="white").pack(pady=10)

        # Netlify Token
        tk.Label(self.window, text="Netlify Token:", bg="#0d1117", fg="white").pack(anchor="w", padx=20)
        self.netlify_entry = tk.Entry(self.window, width=40, show="*")
        self.netlify_entry.pack(padx=20, pady=5)

        # Pre-fill if already saved
        if get_token(NETLIFY_SERVICE):
            self.netlify_entry.insert(0, "************")

        # Vercel Token
        tk.Label(self.window, text="Vercel Token:", bg="#0d1117", fg="white").pack(anchor="w", padx=20, pady=(10,0))
        self.vercel_entry = tk.Entry(self.window, width=40, show="*")
        self.vercel_entry.pack(padx=20, pady=5)

        if get_token(VERCEL_SERVICE):
            self.vercel_entry.insert(0, "************")

        # Save Button
        tk.Button(self.window, text="Save Tokens", command=self.save_tokens,
                  bg="#238636", fg="white", relief="flat", width=20).pack(pady=20)

    def save_tokens(self):
        netlify_token = self.netlify_entry.get().strip()
        vercel_token = self.vercel_entry.get().strip()

        if netlify_token and netlify_token != "************":
            save_token(NETLIFY_SERVICE, netlify_token)

        if vercel_token and vercel_token != "************":
            save_token(VERCEL_SERVICE, vercel_token)

        messagebox.showinfo("Success", "✅ Tokens saved securely!")
        self.window.destroy()
