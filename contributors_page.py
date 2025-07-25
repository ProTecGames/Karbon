import tkinter as tk
from tkinter import ttk
import requests
import json
import os
from PIL import Image, ImageTk
import urllib.request
import io
import threading
import time
import webbrowser
from ai_engine import set_ai_status

class ContributorsPage(tk.Frame):
    def __init__(self, parent, back_callback, root=None):
        super().__init__(parent, bg='#0d1117')
        self.back_callback = back_callback
        self.root = root or parent.winfo_toplevel()
        self.cache_file = "contributors_cache.json"
        self.cache_duration = 3600
        self.owner = "ProTecGames"
        self.repo = "Karbon"
        self.contributors = []

        self.font_family = "Segoe UI"
        self.font_size = 10
        self.theme_colors = {
            "bg": "#0d1117",
            "label_fg": "#f0f6fc",
            "input_bg": "#161b22",
            "input_fg": "#f0f6fc",
            "accent": "#58a6ff",
            "subtitle": "#8b949e",
            "error": "#f85149",
            "warning": "#d29922",
            "success": "#3fb950"
        }

        self.container = tk.Frame(self, bg=self.theme_colors['bg'])
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self.header_frame = tk.Frame(self.container, bg=self.theme_colors['bg'])
        self.header_frame.pack(fill="x")

        self.back_button = ttk.Button(
            self.header_frame,
            text="Back",
            command=self.back_callback,
            style="Modern.TButton"
        )
        self.back_button.pack(side="left")

        self.title_label = tk.Label(
            self.header_frame,
            text="Karbon Contributors",
            font=(self.font_family, 16, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['accent']
        )
        self.title_label.pack(side="left", padx=(10, 0))

        self.refresh_button = ttk.Button(
            self.header_frame,
            text="Refresh",
            command=self.refresh_contributors,
            style="Modern.TButton"
        )
        self.refresh_button.pack(side="right")

        self.total_label = tk.Label(
            self.container,
            text="Loading contributors...",
            font=(self.font_family, 12),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['subtitle']
        )
        self.total_label.pack(pady=10)

        self.spinner_label = tk.Label(
            self.container,
            text="",
            font=(self.font_family, 12),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['accent']
        )
        self.spinner_label.pack()

        self.canvas = tk.Canvas(self.container, bg=self.theme_colors['bg'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview, style="Vertical.TScrollbar")
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.theme_colors['bg'])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.update_appearance(self.font_family, self.font_size, self.theme_colors)

        self.load_contributors()

    def setup_styles(self):
        style = ttk.Style()
        style.configure(
            "Modern.TButton",
            background=self.theme_colors['accent'],
            foreground=self.theme_colors['label_fg'],
            borderwidth=0,
            focuscolor='none',
            relief='flat',
            padding=(10, 5),
            font=(self.font_family, self.font_size)
        )
        style.map(
            "Modern.TButton",
            background=[('active', self.theme_colors['accent']), ('pressed', self.theme_colors['accent'])],
            foreground=[('active', self.theme_colors['label_fg']), ('pressed', self.theme_colors['label_fg'])]
        )
        style.configure("Vertical.TScrollbar",
            background=self.theme_colors["input_bg"],
            troughcolor=self.theme_colors["bg"],
            bordercolor=self.theme_colors["input_bg"],
            arrowcolor=self.theme_colors["label_fg"]
        )
        style.map("Vertical.TScrollbar",
            background=[('active', self.theme_colors["accent"])],
            arrowcolor=[('active', self.theme_colors["label_fg"])]
        )

    def show_loading(self):
        self.spinner_label.config(text="Loading...")
        self.animate_spinner()

    def animate_spinner(self):
        symbols = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        if not hasattr(self, 'spinner_index'):
            self.spinner_index = 0
        
        try:
            if self.spinner_label.winfo_exists() and self.spinner_label.cget('text').startswith('Loading'):
                self.spinner_label.config(text=f"Loading {symbols[self.spinner_index % len(symbols)]}")
                self.spinner_index += 1
                self.root.after(100, self.animate_spinner)
        except tk.TclError:
            pass

    def load_contributors(self):
        self.show_loading()
        threading.Thread(target=self.fetch_contributors, daemon=True).start()

    def fetch_contributors(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    if time.time() - cache.get('timestamp', 0) < self.cache_duration:
                        self.contributors = cache['data']
                        self.root.after(0, self.update_ui)
                        return

            set_ai_status("connecting", "Fetching contributors from GitHub...")
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}/stats/contributors"
            headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
            token = os.environ.get("GITHUB_TOKEN")
            if token:
                headers["Authorization"] = f"Bearer {token}"

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            self.contributors = response.json()

            with open(self.cache_file, 'w') as f:
                json.dump({'timestamp': time.time(), 'data': self.contributors}, f)

            set_ai_status("online", "Successfully fetched contributors.")
            self.root.after(0, self.update_ui)

        except requests.exceptions.RequestException as e:
            set_ai_status("error", f"Failed to fetch contributors: {e}")
            self.root.after(0, lambda: self.total_label.config(text="Error: Could not fetch contributors.", fg=self.theme_colors['error']))
            self.root.after(0, lambda: self.spinner_label.config(text=""))
        except Exception as e:
            set_ai_status("error", f"Unexpected error: {e}")
            self.root.after(0, lambda: self.total_label.config(text="Error: An unexpected error occurred.", fg=self.theme_colors['error']))
            self.root.after(0, lambda: self.spinner_label.config(text=""))

    def refresh_contributors(self):
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        self.load_contributors()

    def update_ui(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.contributors:
            self.total_label.config(text="No contributors found.", fg=self.theme_colors['subtitle'])
            self.spinner_label.config(text="")
            return

        self.contributors.sort(key=lambda x: x['total'], reverse=True)

        total_commits = sum(c['total'] for c in self.contributors)
        self.total_label.config(text=f"Total Contributions: {total_commits} commits", fg=self.theme_colors['subtitle'])

        for idx, contributor in enumerate(self.contributors):
            card = tk.Frame(self.scrollable_frame, bg=self.theme_colors['input_bg'], padx=10, pady=10)
            card.grid(row=idx//3, column=idx%3, padx=5, pady=5, sticky="nsew")

            author = contributor['author']
            username = author['login']
            avatar_url = author['avatar_url']
            profile_url = author['html_url']
            commits = contributor['total']

            additions = sum(week['a'] for week in contributor['weeks'])
            deletions = sum(week['d'] for week in contributor['weeks'])

            try:
                with urllib.request.urlopen(avatar_url) as u:
                    raw_data = u.read()
                image = Image.open(io.BytesIO(raw_data))
                image = image.resize((50, 50), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                avatar_label = tk.Label(card, image=photo, bg=self.theme_colors['input_bg'])
                avatar_label.image = photo
                avatar_label.pack()
            except:
                avatar_label = tk.Label(card, text="No Avatar", bg=self.theme_colors['input_bg'], fg=self.theme_colors['subtitle'], font=(self.font_family, self.font_size))
                avatar_label.pack()

            username_label = tk.Label(
                card,
                text=username,
                font=(self.font_family, self.font_size, "bold"),
                bg=self.theme_colors['input_bg'],
                fg=self.theme_colors['accent'],
                cursor="hand2"
            )
            username_label.pack()
            username_label.bind("<Button-1>", lambda e, url=profile_url: webbrowser.open(url))
            username_label.bind("<Enter>", lambda e, u=username: self.show_tooltip(e, f"Visit {u}'s GitHub profile"))
            username_label.bind("<Leave>", self.hide_tooltip)

            tk.Label(
                card,
                text=f"Commits: {commits}",
                font=(self.font_family, self.font_size),
                bg=self.theme_colors['input_bg'],
                fg=self.theme_colors['label_fg']
            ).pack()
            tk.Label(
                card,
                text=f"Additions: {additions}",
                font=(self.font_family, self.font_size),
                bg=self.theme_colors['input_bg'],
                fg=self.theme_colors['label_fg']
            ).pack()
            tk.Label(
                card,
                text=f"Deletions: {deletions}",
                font=(self.font_family, self.font_size),
                bg=self.theme_colors['input_bg'],
                fg=self.theme_colors['label_fg']
            ).pack()

            if idx == 0:
                tk.Label(
                    card,
                    text="🏆 Top Contributor",
                    font=(self.font_family, self.font_size),
                    bg=self.theme_colors['input_bg'],
                    fg=self.theme_colors['warning']
                ).pack()
            elif commits == self.contributors[-1]['total'] and idx == len(self.contributors)-1:
                tk.Label(
                    card,
                    text="🌱 First Contributor",
                    font=(self.font_family, self.font_size),
                    bg=self.theme_colors['input_bg'],
                    fg=self.theme_colors['success']
                ).pack()

        self.spinner_label.config(text="")

    def show_tooltip(self, event, text):
        x = event.widget.winfo_rootx() + 20
        y = event.widget.winfo_rooty() + 20
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tooltip,
            text=text,
            font=(self.font_family, 8),
            bg=self.theme_colors['input_bg'],
            fg=self.theme_colors['label_fg'],
            borderwidth=1,
            relief="solid",
            padx=5,
            pady=2
        )
        label.pack()

    def hide_tooltip(self, event):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()

    def update_appearance(self, font_family, font_size, theme_colors):
        self.font_family = font_family
        self.font_size = font_size
        self.theme_colors = theme_colors

        self.configure(bg=self.theme_colors["bg"])
        self.container.configure(bg=self.theme_colors["bg"])
        self.header_frame.configure(bg=self.theme_colors["bg"])
        self.canvas.configure(bg=self.theme_colors["bg"])
        self.scrollable_frame.configure(bg=self.theme_colors["bg"])

        self.title_label.configure(
            font=(self.font_family, 16, "bold"),
            bg=self.theme_colors["bg"],
            fg=self.theme_colors["accent"]
        )
        self.total_label.configure(
            font=(self.font_family, 12),
            bg=self.theme_colors["bg"],
            fg=self.theme_colors["subtitle"]
        )
        self.spinner_label.configure(
            font=(self.font_family, 12),
            bg=self.theme_colors["bg"],
            fg=self.theme_colors["accent"]
        )

        self.setup_styles()

        self.update_ui()
