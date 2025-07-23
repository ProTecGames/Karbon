import tkinter as tk
from tkinter import ttk

class ContributorsView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#1e1e1e")
        
        title = tk.Label(self, text="Contributors", font=("Helvetica", 20, "bold"), fg="#ffffff", bg="#1e1e1e")
        title.pack(pady=20)

        contributors = [
            "Prakhar Doneria",
            "Atharva Kinage",
            "Sharanya Achanta",
            "Rishika Goyal",
            "Rachel",
            "Tanmay Shah",
            "Pravalika Batchu",
            "Abhirami Ramadas 👋"
        ]

        for name in contributors:
            label = tk.Label(self, text=name, font=("Helvetica", 14), fg="#d4d4d4", bg="#1e1e1e")
            label.pack(pady=5)
