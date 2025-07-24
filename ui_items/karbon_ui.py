import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from ui_items.prompt_view import PromptView
from ui_items.editor_view import EditorView

class KarbonUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_styles()
        self.code = ""
        self.api_key = None
        self.model_source = None
        self.load_settings()

        # Create main container with gradient-like effect
        self.main_container = tk.Frame(root, bg='#0d1117')
        self.main_container.pack(fill="both", expand=True)

        # Add animated title bar
        self.create_title_bar()

        # Content area
        self.content_frame = tk.Frame(self.main_container, bg='#0d1117')
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Initialize views
        self.prompt_view = PromptView(self.content_frame, on_generate=self.handle_prompt_generated)
        self.editor_view = EditorView(self.content_frame, get_code_callback=self.get_code, set_code_callback=self.set_code, get_api_key_callback=self.get_api_key, get_model_source_callback=self.get_model_source)

        # Show prompt view initially
        self.prompt_view.pack(fill="both", expand=True)

        # Add status bar
        self.create_status_bar()

        # Start title animation
        self.animate_title()

    def setup_window(self):
        """Configure the main window with modern styling"""
        self.root.title("Karbon - AI Web Builder")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)

        # Set window icon and styling
        self.root.configure(bg='#0d1117')

        # Center the window
        self.center_window()

        # Make window slightly transparent for modern effect
        self.root.attributes('-alpha', 0.98)

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_styles(self):
        """Configure ttk styles for modern appearance"""
        style = ttk.Style()

        # Configure modern button style
        style.configure(
            "Modern.TButton",
            background='#238636',
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            relief='flat',
            padding=(20, 10)
        )

        style.map(
            "Modern.TButton",
            background=[('active', '#2ea043'), ('pressed', '#1a7f37')]
        )

        # Configure modern entry style
        style.configure(
            "Modern.TEntry",
            fieldbackground='#21262d',
            borderwidth=1,
            relief='solid',
            insertcolor='white'
        )

    def create_title_bar(self):
        """Create an animated title bar"""
        self.title_frame = tk.Frame(self.main_container, bg='#0d1117', height=80)
        self.title_frame.pack(fill="x", padx=20, pady=(20, 10))
        self.title_frame.pack_propagate(False)

        # Main title with gradient effect
        self.title_label = tk.Label(
            self.title_frame,
            text="⚡ KARBON",
            font=("Segoe UI", 28, "bold"),
            bg='#0d1117',
            fg='#58a6ff'
        )
        self.title_label.pack(side="left", pady=10)

        # Subtitle
        self.subtitle_label = tk.Label(
            self.title_frame,
            text="AI Web Builder",
            font=("Segoe UI", 12),
            bg='#0d1117',
            fg='#8b949e'
        )
        self.subtitle_label.pack(side="left", padx=(10, 0), pady=10)
        
        # Settings button
        settings_btn = tk.Button(
            self.title_frame,
            text="⚙️",
            font=("Segoe UI", 16),
            bg='#21262d',
            fg='#8b949e',
            activebackground='#30363d',
            activeforeground='#f0f6fc',
            relief='flat',
            bd=0,
            cursor='hand2',
            command=self.open_settings
        )
        settings_btn.pack(side="right", padx=(10, 0))


        # Status indicator
        self.status_indicator = tk.Label(
            self.title_frame,
            text="●",
            font=("Segoe UI", 20),
            bg='#0d1117',
            fg='#3fb950'
        )
        self.status_indicator.pack(side="right", pady=10)

        # Version label
        version_label = tk.Label(
            self.title_frame,
            text="v2.0",
            font=("Segoe UI", 10),
            bg='#0d1117',
            fg='#6e7681'
        )
        version_label.pack(side="right", padx=(0, 10), pady=10)

    def create_status_bar(self):
        """Create a modern status bar"""
        self.status_frame = tk.Frame(self.main_container, bg='#161b22', height=30)
        self.status_frame.pack(fill="x", side="bottom")
        self.status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            self.status_frame,
            text="Ready to create amazing web experiences",
            font=("Segoe UI", 9),
            bg='#161b22',
            fg='#8b949e'
        )
        self.status_label.pack(side="left", padx=20, pady=5)

        # Progress indicator (hidden initially)
        self.progress_var = tk.StringVar()
        self.progress_label = tk.Label(
            self.status_frame,
            textvariable=self.progress_var,
            font=("Segoe UI", 9),
            bg='#161b22',
            fg='#58a6ff'
        )
        self.progress_label.pack(side="right", padx=20, pady=5)

    def animate_title(self):
        """Animate the title with a subtle glow effect"""
        colors = ['#58a6ff', '#79c0ff', '#a5d6ff', '#79c0ff', '#58a6ff']
        self.color_index = 0

        def cycle_colors():
            if hasattr(self, 'title_label'):
                self.title_label.configure(fg=colors[self.color_index])
                self.color_index = (self.color_index + 1) % len(colors)
                self.root.after(2000, cycle_colors)

        cycle_colors()

    def animate_status_indicator(self):
        """Animate the status indicator during processing"""
        colors = ['#f85149', '#ff7b72', '#ffa198', '#ff7b72']
        for i, color in enumerate(colors):
            self.root.after(i * 200, lambda c=color: self.status_indicator.configure(fg=c))

        # Return to green after animation
        self.root.after(len(colors) * 200, lambda: self.status_indicator.configure(fg='#3fb950'))

    def update_status(self, message, progress=None):
        """Update status bar with message and optional progress"""
        self.status_label.configure(text=message)
        if progress:
            self.progress_var.set(progress)
        else:
            self.progress_var.set("")

    def transition_to_editor(self):
        """Smooth transition from prompt view to editor view"""
        # Update status
        self.update_status("Transitioning to editor...", "🔄")
        self.animate_status_indicator()

        # Fade out prompt view (simulate with pack/unpack)
        def fade_transition():
            self.prompt_view.pack_forget()

            # Show loading message briefly
            loading_frame = tk.Frame(self.content_frame, bg='#0d1117')
            loading_frame.pack(fill="both", expand=True)

            loading_label = tk.Label(
                loading_frame,
                text="✨ Preparing your code editor...",
                font=("Segoe UI", 16),
                bg='#0d1117',
                fg='#58a6ff'
            )
            loading_label.pack(expand=True)

            # Show editor after brief delay
            def show_editor():
                loading_frame.destroy()
                self.editor_view.pack(fill="both", expand=True)
                self.update_status("Code editor ready - Start building!", "✅")

            self.root.after(1000, show_editor)

        self.root.after(500, fade_transition)

    def get_code(self):
        return self.code

    def set_code(self, new_code):
        self.code = new_code
        self.update_status(f"Code updated - {len(new_code)} characters", "📝")

    def handle_prompt_generated(self, code):
        """Handle when code is generated from prompt"""
        self.code = code
        self.update_status("Code generated successfully!", "🎉")
        self.transition_to_editor()
        
    def get_api_key(self):
        return self.api_key

    def get_model_source(self):
        return self.model_source

    def save_settings(self):
        settings = {"api_key": self.api_key, "model_source": self.model_source}
        with open("settings.json", "w") as f:
            json.dump(settings, f)

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.api_key = settings.get("api_key")
                self.model_source = settings.get("model_source")

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x200")
        settings_window.configure(bg='#161b22')

        tk.Label(settings_window, text="API Key:", bg='#161b22', fg='white').pack(pady=(10,0))
        api_key_entry = tk.Entry(settings_window, width=50)
        api_key_entry.pack(pady=5)
        if self.api_key:
            api_key_entry.insert(0, self.api_key)

        tk.Label(settings_window, text="Model Source URL (optional):", bg='#161b22', fg='white').pack(pady=(10,0))
        model_source_entry = tk.Entry(settings_window, width=50)
        model_source_entry.pack(pady=5)
        if self.model_source:
            model_source_entry.insert(0, self.model_source)

        def save_and_close():
            self.api_key = api_key_entry.get()
            self.model_source = model_source_entry.get()
            self.save_settings()
            settings_window.destroy()

        save_btn = tk.Button(settings_window, text="Save", command=save_and_close)
        save_btn.pack(pady=10)


    def show_notification(self, message, type="info"):
        """Show a temporary notification"""
        colors = {
            "info": "#58a6ff",
            "success": "#3fb950",
            "warning": "#d29922",
            "error": "#f85149"
        }

        notification = tk.Toplevel(self.root)
        notification.title("")
        notification.geometry("300x80")
        notification.configure(bg='#21262d')
        notification.attributes('-topmost', True)
        notification.overrideredirect(True)

        # Position notification in top-right
        x = self.root.winfo_x() + self.root.winfo_width() - 320
        y = self.root.winfo_y() + 50
        notification.geometry(f"300x80+{x}+{y}")

        # Notification content
        tk.Label(
            notification,
            text=message,
            font=("Segoe UI", 10),
            bg='#21262d',
            fg=colors.get(type, "#58a6ff"),
            wraplength=280
        ).pack(expand=True, padx=10, pady=10)

        # Auto-close after 3 seconds
        notification.after(3000, notification.destroy)
