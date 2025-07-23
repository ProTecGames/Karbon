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
    def __init__(self, parent, back_callback):
        super().__init__(parent, bg='#0d1117')
        self.back_callback = back_callback
        self.cache_file = "contributors_cache.json"
        self.cache_duration = 3600  # Cache for 1 hour
        self.owner = "ProTecGames"
        self.repo = "Karbon"
        self.contributors = []

        # Setup styles to match Karbon's theme
        self.setup_styles()

        # Create main container
        self.container = tk.Frame(self, bg='#0d1117')
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        # Create header with back and refresh buttons
        self.header_frame = tk.Frame(self.container, bg='#0d1117')
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
            font=("Segoe UI", 16, "bold"),
            bg='#0d1117',
            fg='#58a6ff'
        )
        self.title_label.pack(side="left", padx=(10, 0))

        self.refresh_button = ttk.Button(
            self.header_frame,
            text="Refresh",
            command=self.refresh_contributors,
            style="Modern.TButton"
        )
        self.refresh_button.pack(side="right")

        # Total contributions label
        self.total_label = tk.Label(
            self.container,
            text="Loading contributors...",
            font=("Segoe UI", 12),
            bg='#0d1117',
            fg='#8b949e'
        )
        self.total_label.pack(pady=10)

        # Loading spinner
        self.spinner_label = tk.Label(
            self.container,
            text="",
            font=("Segoe UI", 12),
            bg='#0d1117',
            fg='#58a6ff'
        )
        self.spinner_label.pack()

        # Contributors canvas with scrollbar
        self.canvas = tk.Canvas(self.container, bg='#0d1117', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#0d1117')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Start loading contributors
        self.load_contributors()

    def setup_styles(self):
        """Configure styles to match Karbon's theme"""
        style = ttk.Style()
        style.configure(
            "Modern.TButton",
            background='#238636',
            foreground='#0d1117',
            borderwidth=0,
            focuscolor='none',
            relief='flat',
            padding=(10, 5),
            font=("Segoe UI", 10)
        )
        style.map(
            "Modern.TButton",
            background=[('active', '#2ea043'), ('pressed', '#1a7f37')],
            foreground=[('active', '#0d1117'), ('pressed', '#0d1117')]
        )

    def show_loading(self):
        """Display a simple loading animation"""
        self.spinner_label.config(text="Loading...")
        threading.Thread(target=self.animate_spinner, daemon=True).start()

    def animate_spinner(self):
        """Simple text-based loading animation"""
        symbols = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        i = 0
        while self.spinner_label.winfo_exists():
            self.spinner_label.config(text=f"Loading {symbols[i % len(symbols)]}")
            i += 1
            time.sleep(0.1)
        self.spinner_label.config(text="")

    def load_contributors(self):
        """Load contributors from cache or API"""
        self.show_loading()
        threading.Thread(target=self.fetch_contributors, daemon=True).start()

    def fetch_contributors(self):
        """Fetch contributors from GitHub API or cache"""
        try:
            # Check cache
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    if time.time() - cache.get('timestamp', 0) < self.cache_duration:
                        self.contributors = cache['data']
                        self.update_ui()
                        return

            set_ai_status("connecting", "Fetching contributors from GitHub...")
            # Fetch from GitHub API
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}/stats/contributors"
            headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
            token = os.environ.get("GITHUB_TOKEN")  # Optional token for higher rate limits
            if token:
                headers["Authorization"] = f"Bearer {token}"

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            self.contributors = response.json()

            # Cache the results
            with open(self.cache_file, 'w') as f:
                json.dump({'timestamp': time.time(), 'data': self.contributors}, f)

            set_ai_status("online", "Successfully fetched contributors.")
            self.update_ui()

        except requests.exceptions.RequestException as e:
            set_ai_status("error", f"Failed to fetch contributors: {e}")
            self.total_label.config(text="Error: Could not fetch contributors.", fg='#f85149')
            self.spinner_label.config(text="")
        except Exception as e:
            set_ai_status("error", f"Unexpected error: {e}")
            self.total_label.config(text="Error: An unexpected error occurred.", fg='#f85149')
            self.spinner_label.config(text="")

    def refresh_contributors(self):
        """Force refresh contributors from API"""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        self.load_contributors()

    def update_ui(self):
        """Update the UI with contributor cards"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.contributors:
            self.total_label.config(text="No contributors found.", fg='#8b949e')
            self.spinner_label.config(text="")
            return

        # Sort by total commits (descending)
        self.contributors.sort(key=lambda x: x['total'], reverse=True)

        total_commits = sum(c['total'] for c in self.contributors)
        self.total_label.config(text=f"Total Contributions: {total_commits} commits", fg='#8b949e')

        # Create contributor cards
        for idx, contributor in enumerate(self.contributors):
            card = tk.Frame(self.scrollable_frame, bg='#21262d', padx=10, pady=10)
            card.grid(row=idx//3, column=idx%3, padx=5, pady=5, sticky="nsew")

            author = contributor['author']
            username = author['login']
            avatar_url = author['avatar_url']
            profile_url = author['html_url']
            commits = contributor['total']

            # Calculate total additions and deletions
            additions = sum(week['a'] for week in contributor['weeks'])
            deletions = sum(week['d'] for week in contributor['weeks'])

            # Load avatar
            try:
                with urllib.request.urlopen(avatar_url) as u:
                    raw_data = u.read()
                image = Image.open(io.BytesIO(raw_data))
                image = image.resize((50, 50), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                avatar_label = tk.Label(card, image=photo, bg='#21262d')
                avatar_label.image = photo  # Keep reference
                avatar_label.pack()
            except:
                avatar_label = tk.Label(card, text="No Avatar", bg='#21262d', fg='#8b949e', font=("Segoe UI", 10))
                avatar_label.pack()

            # Username (clickable link with tooltip)
            username_label = tk.Label(
                card,
                text=username,
                font=("Segoe UI", 10, "bold"),
                bg='#21262d',
                fg='#58a6ff',
                cursor="hand2"
            )
            username_label.pack()
            username_label.bind("<Button-1>", lambda e, url=profile_url: webbrowser.open(url))
            # Tooltip
            username_label.bind("<Enter>", lambda e, u=username: self.show_tooltip(e, f"Visit {u}'s GitHub profile"))
            username_label.bind("<Leave>", self.hide_tooltip)

            # Stats
            tk.Label(
                card,
                text=f"Commits: {commits}",
                font=("Segoe UI", 10),
                bg='#21262d',
                fg='#8b949e'
            ).pack()
            tk.Label(
                card,
                text=f"Additions: {additions}",
                font=("Segoe UI", 10),
                bg='#21262d',
                fg='#8b949e'
            ).pack()
            tk.Label(
                card,
                text=f"Deletions: {deletions}",
                font=("Segoe UI", 10),
                bg='#21262d',
                fg='#8b949e'
            ).pack()

            # Badges
            if idx == 0:
                tk.Label(
                    card,
                    text="🏆 Top Contributor",
                    font=("Segoe UI", 10),
                    bg='#21262d',
                    fg='#d29922'
                ).pack()
            elif commits == self.contributors[-1]['total'] and idx == len(self.contributors)-1:
                tk.Label(
                    card,
                    text="🌱 First Contributor",
                    font=("Segoe UI", 10),
                    bg='#21262d',
                    fg='#3fb950'
                ).pack()

        self.spinner_label.config(text="")

    def show_tooltip(self, event, text):
        """Show a tooltip near the widget"""
        x = event.widget.winfo_rootx() + 20
        y = event.widget.winfo_rooty() + 20
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tooltip,
            text=text,
            font=("Segoe UI", 8),
            bg='#21262d',
            fg='#f0f6fc',
            borderwidth=1,
            relief="solid",
            padx=5,
            pady=2
        )
        label.pack()

    def hide_tooltip(self, event):
        """Hide the tooltip"""
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
