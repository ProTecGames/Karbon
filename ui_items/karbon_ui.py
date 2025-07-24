import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from ui_items.prompt_view import PromptView
from ui_items.editor_view import EditorView
from ai_engine import ai_status
# Note: ContributorsPage has been temporarily removed to fix core functionality.
# from contributors_page import ContributorsPage 


EXAMPLES = {
    "Login Page": "Create a login page using HTML and Tailwind CSS",
    "Personal Portfolio Page": "Build a personal portfolio page with sections for About, Projects, and Contact",
    "Landing Page": "Design a landing page for a mobile app with a pricing section and testimonials",
    "Blog Homepage": "Create a dark-themed blog homepage with a navbar and featured articles",
    "Form": "Generate a simple form to collect name, email, and message with a submit button"
}


class KarbonUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_styles()
        self.code = ""
        self.api_key = None
        self.model_source = None


        # Create main container
        self.main_container = tk.Frame(root, bg='#0d1117')
        self.main_container.pack(fill="both", expand=True)

        # Add title bar
        self.create_title_bar()

        # Create a PanedWindow for a resizable layout
        self.paned_window = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Initialize views (prompt and editor)

        # Main container
        self.main_container = tk.Frame(root, bg='#0d1117')
        self.main_container.pack(fill="both", expand=True)

        # Animated title
        self.create_title_bar()

        # Resizable PanedWindow layout
        self.paned_window = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Prompt & Editor views (inside paned_window)

        self.prompt_view = PromptView(self.paned_window, on_generate=self.handle_prompt_generated)
        self.editor_view = EditorView(
            self.paned_window,
            get_code_callback=self.get_code,
            set_code_callback=self.set_code,
            get_api_key_callback=self.get_api_key,
            get_model_source_callback=self.get_model_source
        )

        # Add status bar at the bottom
        self.create_status_bar()

        # Start animations and status polling

        # Add views to paned_window (not packed individually)
        self.paned_window.add(self.prompt_view)
        self.paned_window.add(self.editor_view)

        # Layout from settings
        self.load_settings()

        # Menu bar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Export Code", command=self.export_code)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.destroy)

        # View controls
        self.example_var = tk.StringVar(value="🔽 Choose Example Prompt")
        PADDED_EXAMPLES = {key.ljust(30): prompt for key, prompt in EXAMPLES.items()}
        self.example_menu = tk.OptionMenu(
            self.main_container,
            self.example_var,
            *PADDED_EXAMPLES.keys(),
            command=lambda key: self.insert_example_prompt(key.strip())
        )
        self.example_menu.config(
            font=("Segoe UI", 10),
            bg="#21262d",
            fg="white",
            relief="flat",
            highlightthickness=0,
            width=24
        )
        dropdown_menu = self.example_menu["menu"]
        dropdown_menu.config(
            font=("Segoe UI", 10),
            bg="#21262d",
            fg="white",
            activebackground="#2ea043",
            activeforeground="white",
            tearoff=0
        )
        self.example_menu.pack(pady=(10, 0))

        # Contributors button and page
        self.contributors_page = ContributorsPage(self.main_container, self.show_prompt_view)
        self.contributors_button = ttk.Button(
            self.main_container,
            text="Contributors",
            command=self.show_contributors_page,
            style="Modern.TButton"
        )
        self.contributors_button.pack(pady=10)

        # Status bar
        self.create_status_bar()

        # Final UI polish

        self.animate_title()
        self.update_ai_status_indicator()

    def setup_window(self):
        """Configure the main window with modern styling"""
        self.root.title("Karbon - AI Web Builder")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        self.root.configure(bg='#0d1117')
        self.root.attributes('-alpha', 0.98)

        # Create Menu Bar
        self.menu_bar = tk.Menu(self.root, bg="#21262d", fg="#c9d1d9", activebackground="#30363d", activeforeground="#f0f6fc", relief="flat")
        self.root.config(menu=self.menu_bar)

        # --- File Menu ---
        file_menu = tk.Menu(self.menu_bar, tearoff=0, bg="#21262d", fg="#c9d1d9")
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Code", command=self.export_code)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)

        # --- View Menu ---
        view_menu = tk.Menu(self.menu_bar, tearoff=0, bg="#21262d", fg="#c9d1d9")
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        self.prompt_view_visible = tk.BooleanVar(value=True)
        self.editor_view_visible = tk.BooleanVar(value=False)
        view_menu.add_checkbutton(label="Prompt View", onvalue=True, offvalue=False, variable=self.prompt_view_visible, command=self.toggle_prompt_view)
        view_menu.add_checkbutton(label="Editor View", onvalue=True, offvalue=False, variable=self.editor_view_visible, command=self.toggle_editor_view)

        # --- Layouts Menu ---
        layouts_menu = tk.Menu(self.menu_bar, tearoff=0, bg="#21262d", fg="#c9d1d9")
        self.menu_bar.add_cascade(label="Layouts", menu=layouts_menu)
        layouts_menu.add_command(label="Default", command=self.layout_default)
        layouts_menu.add_command(label="Coding Focus", command=self.layout_coding_focus)
        layouts_menu.add_command(label="Preview Focus", command=self.layout_preview_focus)
        
        self.center_window()

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
        style.theme_use('clam')

        # Style for PanedWindow Sash
        style.configure("TPanedWindow", background='#0d1117')
        style.configure("TPanedWindow.Sash", background='#30363d', sashthickness=6, relief='flat', borderwidth=0)
        style.map("TPanedWindow.Sash", background=[('active', '#58a6ff')])

        # Style for Buttons and Entries
        style.configure("Modern.TButton", background='#238636', foreground='white', borderwidth=0, focuscolor='none', relief='flat', padding=(20, 10), font=("Segoe UI", 10))
        style.map("Modern.TButton", background=[('active', '#2ea043'), ('pressed', '#1a7f37')])
        style.configure("Modern.TEntry", fieldbackground='#21262d', borderwidth=1, relief='solid', insertcolor='white', foreground='white')

    def create_title_bar(self):
        """Create the main title bar with controls"""
        self.title_frame = tk.Frame(self.main_container, bg='#0d1117', height=80)
        self.title_frame.pack(fill="x", padx=20, pady=(20, 10))
        self.title_frame.pack_propagate(False)

        # Left side: Title and Subtitle
        self.title_label = tk.Label(self.title_frame, text="⚡ KARBON", font=("Segoe UI", 28, "bold"), bg='#0d1117', fg='#58a6ff')
        self.title_label.pack(side="left", pady=10)
        self.subtitle_label = tk.Label(self.title_frame, text="AI Web Builder", font=("Segoe UI", 12), bg='#0d1117', fg='#8b949e')
        self.subtitle_label.pack(side="left", padx=(10, 0), pady=10)


        # Right side: Controls and Status
        settings_btn = tk.Button(self.title_frame, text="⚙️", font=("Segoe UI", 16), bg='#21262d', fg='#8b949e', activebackground='#30363d', activeforeground='#f0f6fc', relief='flat', bd=0, cursor='hand2', command=self.open_settings)

        # --- NEW: Add Swap Panels Button ---
        swap_btn = tk.Button(
            self.title_frame, text="🔄", font=("Segoe UI", 16), bg='#21262d', fg='#8b949e',
            activebackground='#30363d', activeforeground='#f0f6fc', relief='flat', bd=0, cursor='hand2', command=self.swap_panels
        )
        swap_btn.pack(side="right", padx=(10, 0))
        # --- END NEW ---

        settings_btn = tk.Button(
            self.title_frame, text="⚙️", font=("Segoe UI", 16), bg='#21262d', fg='#8b949e',
            activebackground='#30363d', activeforeground='#f0f6fc', relief='flat', bd=0, cursor='hand2', command=self.open_settings
        )
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

        settings_btn.pack(side="right", padx=(10, 0))
        swap_btn = tk.Button(self.title_frame, text="🔄", font=("Segoe UI", 16), bg='#21262d', fg='#8b949e', activebackground='#30363d', activeforeground='#f0f6fc', relief='flat', bd=0, cursor='hand2', command=self.swap_panels)
        swap_btn.pack(side="right", padx=(10, 0))
        self.ai_status_label = tk.Label(self.title_frame, text="AI: Unknown", font=("Segoe UI", 10, "bold"), bg='#0d1117', fg='#d29922', anchor="e")
        self.ai_status_label.pack(side="right", padx=(0, 20), pady=5)
        version_label = tk.Label(self.title_frame, text="v2.0", font=("Segoe UI", 10), bg='#0d1117', fg='#6e7681')
        version_label.pack(side="right", padx=(0, 10), pady=10)
        self.status_indicator = tk.Label(self.title_frame, text="●", font=("Segoe UI", 20), bg='#0d1117', fg='#3fb950')
        self.status_indicator.pack(side="right", pady=10)

    def create_status_bar(self):
        """Create a modern status bar at the bottom"""
        self.status_frame = tk.Frame(self.main_container, bg='#161b22', height=30)
        self.status_frame.pack(fill="x", side="bottom")
        self.status_frame.pack_propagate(False)
        self.status_label = tk.Label(self.status_frame, text="Ready to create amazing web experiences", font=("Segoe UI", 9), bg='#161b22', fg='#8b949e')
        self.status_label.pack(side="left", padx=20, pady=5)
        self.progress_var = tk.StringVar()
        self.progress_label = tk.Label(self.status_frame, textvariable=self.progress_var, font=("Segoe UI", 9), bg='#161b22', fg='#58a6ff')
        self.progress_label.pack(side="right", padx=20, pady=5)

    def update_ai_status_indicator(self):
        """Polls and updates the AI status label color and text"""
        state = ai_status.get("state", "unknown")
        color_map = {"online": "#3fb950", "offline": "#f85149", "connecting": "#58a6ff", "error": '#d29922', "unknown": "#6e7681"}
        color = color_map.get(state, "#6e7681")
        self.ai_status_label.config(text=f"AI: {state.capitalize()}", fg=color)
        self.root.after(2000, self.update_ai_status_indicator)

    def animate_title(self):
        """Animates the title with a subtle glow effect"""
        colors = ['#58a6ff', '#79c0ff', '#a5d6ff', '#79c0ff', '#58a6ff']
        self.color_index = 0
        def cycle_colors():
            if hasattr(self, 'title_label') and self.title_label.winfo_exists():
                self.title_label.configure(fg=colors[self.color_index])
                self.color_index = (self.color_index + 1) % len(colors)
                self.root.after(2000, cycle_colors)
        cycle_colors()

    def update_status(self, message, progress=None):
        """Update status bar with a message and optional progress text"""
        self.status_label.configure(text=message)
        self.progress_var.set(progress if progress else "")

    def get_code(self):
        return self.code

    def set_code(self, new_code):
        self.code = new_code
        self.update_status(f"Code updated - {len(new_code)} characters", "📝")

    def handle_prompt_generated(self, code):
        """Callback for when code is generated from the prompt view"""
        self.code = code
        self.update_status("Code generated successfully!", "🎉")
        # Automatically switch to a split view to show the editor
        self.layout_preview_focus()

    def get_api_key(self):
        return self.api_key

    def get_model_source(self):
        return self.model_source

    def toggle_prompt_view(self):
        """Adds or removes the prompt view from the paned window."""
        is_present = self.prompt_view in self.paned_window.panes()
        if self.prompt_view_visible.get() and not is_present:
            # FIX: Use .add() instead of .insert() to avoid the error on an empty paned window.
            # This correctly adds the prompt view as the first pane.
            self.paned_window.add(self.prompt_view, weight=1)
        elif not self.prompt_view_visible.get() and is_present:
            self.paned_window.forget(self.prompt_view)

    def toggle_editor_view(self):
        """Adds or removes the editor view from the paned window."""
        is_present = self.editor_view in self.paned_window.panes()
        if self.editor_view_visible.get() and not is_present:
            self.paned_window.add(self.editor_view, weight=1)
        elif not self.editor_view_visible.get() and is_present:
            self.paned_window.forget(self.editor_view)

    def swap_panels(self):
        """Swaps the order of the panels in the PanedWindow."""
        panes = self.paned_window.panes()
        if len(panes) == 2:
            self.paned_window.forget(panes[0])
            self.paned_window.add(panes[0])

    def layout_default(self):
        """Applies the default layout (prompt view only)."""
        self.prompt_view_visible.set(True)
        self.editor_view_visible.set(False)
        self.toggle_prompt_view()
        self.toggle_editor_view()

    def layout_coding_focus(self):
        """Applies the coding focus layout (editor view only)."""
        self.prompt_view_visible.set(False)
        self.editor_view_visible.set(True)
        self.toggle_prompt_view()
        self.toggle_editor_view()

    def layout_preview_focus(self):
        """Applies a split-screen layout."""
        self.prompt_view_visible.set(True)
        self.editor_view_visible.set(True)
        self.toggle_prompt_view()
        self.toggle_editor_view()
        # Apply sash position after a short delay to ensure window is drawn
        self.root.after(100, lambda: self.paned_window.sash_place(0, self.root.winfo_width() // 2, 0))

    def save_settings(self):
        """Saves API keys and layout settings to settings.json."""
        sash_position = None
        if len(self.paned_window.panes()) > 1:
            try:
                sash_position = self.paned_window.sashpos(0)
            except tk.TclError:
                sash_position = self.root.winfo_width() // 2

        layout_settings = {
            "prompt_view_visible": self.prompt_view_visible.get(),
            "editor_view_visible": self.editor_view_visible.get(),
            "sash_position": sash_position
        }
        settings = {"api_key": self.api_key, "model_source": self.model_source, "layout": layout_settings}
        try:
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=4)
        except IOError as e:
            print(f"Error saving settings: {e}")

    def load_settings(self):
        """Loads API keys and applies the saved layout from settings.json."""
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    self.api_key = settings.get("api_key")
                    self.model_source = settings.get("model_source")
                    layout_settings = settings.get("layout")

                    if layout_settings:
                        self.prompt_view_visible.set(layout_settings.get("prompt_view_visible", True))
                        self.editor_view_visible.set(layout_settings.get("editor_view_visible", False))
                        sash_position = layout_settings.get("sash_position")

                        self.toggle_prompt_view()
                        self.toggle_editor_view()

                        def apply_sash():
                            if sash_position is not None and len(self.paned_window.panes()) > 1:
                                try: self.paned_window.sash_place(0, sash_position, 0)
                                except tk.TclError: pass
                        self.root.after(100, apply_sash)
                        return
            except (json.JSONDecodeError, KeyError, IOError) as e:
                print(f"Error reading settings.json ({e}), using default layout.")
        
        self.layout_default()

    def open_settings(self):
        """Opens the settings dialog window."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x250")
        settings_window.configure(bg='#161b22')
        settings_window.transient(self.root)
        settings_window.grab_set()

        tk.Label(settings_window, text="API Key:", bg='#161b22', fg='white', font=("Segoe UI", 10)).pack(pady=(20,0))
        api_key_entry = ttk.Entry(settings_window, width=50, style="Modern.TEntry")
        api_key_entry.pack(pady=5, padx=20)
        if self.api_key:
            api_key_entry.insert(0, self.api_key)

        tk.Label(settings_window, text="Model Source URL (optional):", bg='#161b22', fg='white', font=("Segoe UI", 10)).pack(pady=(10,0))
        model_source_entry = ttk.Entry(settings_window, width=50, style="Modern.TEntry")
        model_source_entry.pack(pady=5, padx=20)
        if self.model_source:
            model_source_entry.insert(0, self.model_source)

        def save_and_close():
            self.api_key = api_key_entry.get()
            self.model_source = model_source_entry.get()
            self.save_settings()
            settings_window.destroy()

        save_btn = ttk.Button(settings_window, text="Save & Close", command=save_and_close, style="Modern.TButton")
        save_btn.pack(pady=20)

    def export_code(self):
        """Exports the current code to HTML/CSS/JS files."""
        from exporter import export_code
        if not self.code:
            self.show_notification("There is no code to export.", "warning")
            return
        try:
            export_code(self.code)
            self.show_notification("Code exported successfully!", "success")
        except Exception as e:
            self.show_notification(f"Failed to export code: {e}", "error")

    def show_notification(self, message, n_type="info"):
        """Shows a temporary notification pop-up."""
        colors = {"info": "#58a6ff", "success": "#3fb950", "warning": "#d29922", "error": "#f85149"}
        notification = tk.Toplevel(self.root)
        notification.overrideredirect(True)
        notification.attributes('-topmost', True)
        notification.configure(bg='#21262d', relief="solid", borderwidth=1)
        
        x = self.root.winfo_x() + self.root.winfo_width() - 320
        y = self.root.winfo_y() + 50
        notification.geometry(f"300x80+{x}+{y}")

        tk.Label(notification, text=message, font=("Segoe UI", 10), bg='#21262d', fg=colors.get(n_type, "#58a6ff"), wraplength=280).pack(expand=True, padx=10, pady=10)
        notification.after(3000, notification.destroy)
