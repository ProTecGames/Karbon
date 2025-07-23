import tkinter as tk
from tkinter import ttk
import threading
from ui_items.prompt_view import PromptView
from ui_items.editor_view import EditorView
from ai_engine import ai_status
from contributors_page import ContributorsPage

EXAMPLES = {
    "Login Page": "Create a login page using HTML and Tailwind CSS",
    "Personal Portfolio Page": "Build a personal portfolio page with sections for About, Projects, and Contact",
    "Landing Page": "Design a landing page for a mobile app with a pricing section and testimonials",
    "Blog Homepage": "Create a dark-themed blog homepage with a navbar and featured articles",
    "Form": "Generate a simple form to collect name, email, and message with a submit button"
}

class KarbonUI:
    def insert_example_prompt(self, choice: str):
        print(f"Inserting: {choice}")
        """Inserts selected example prompt into the prompt input field."""
        example_text = EXAMPLES.get(choice.strip(), "")
    
        if example_text:
            try:
                self.prompt_view.text_input.configure(state="normal")  # Ensure editable
                self.prompt_view.text_input.delete("1.0", "end")       # Clear previous
                self.prompt_view.text_input.insert("1.0", example_text)  # Insert new
                self.prompt_view.text_input.see("1.0")                 # Scroll to top
                self.prompt_view.text_input.update_idletasks()       # Force update
                self.prompt_view.placeholder_active = False
                self.prompt_view.text_input.configure(fg='#f0f6fc')
                current_text = self.prompt_view.text_input.get("1.0", "end-1c")
                print("📦 Current Text in Box:", repr(current_text))
                print("Prompt inserted successfully.")
            except Exception as e:
                print("❌ Error inserting text:", e)

    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_styles()
        self.code = ""

        # Create menu bar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Export Code", command=self.export_code)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.destroy)

        # Main container
        self.main_container = tk.Frame(root, bg='#0d1117')
        self.main_container.pack(fill="both", expand=True)

        # Animated title
        self.create_title_bar()

        # Content area
        self.content_frame = tk.Frame(self.main_container, bg='#0d1117')
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Example Prompt Dropdown
        self.example_var = tk.StringVar()
        self.example_var.set("🔽 Choose Example Prompt")
        PADDED_EXAMPLES = {key.ljust(30): prompt for key, prompt in EXAMPLES.items()}
        self.example_menu = tk.OptionMenu(
            self.content_frame,
            self.example_var,
            *PADDED_EXAMPLES.keys(),
            command=lambda key: self.insert_example_prompt(key.strip())
        )

        # Style the visible OptionMenu button
        self.example_menu.config(
            font=("Segoe UI", 10),
            bg="#21262d",
            fg="white",
            relief="flat",
            highlightthickness=0,
            width=24
        )

        # Style the dropdown list (menu part)
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

        # Contributors button
        self.contributors_page = ContributorsPage(self.content_frame, self.show_prompt_view)
        self.contributors_button = ttk.Button(
            self.content_frame,
            text="Contributors",
            command=self.show_contributors_page,
            style="Modern.TButton"
        )
        self.contributors_button.pack(pady=10)

        # Prompt view
        self.prompt_view = PromptView(

            self.content_frame,
            on_generate=self.handle_prompt_generated
        )

        self.prompt_view.pack(fill="both", expand=True)

        # Editor view, initialized but not packed yet
        self.editor_view = EditorView(
            self.content_frame,
            get_code_callback=self.get_code,
            set_code_callback=self.set_code
        )

        # Add status bar and animation
        self.create_status_bar()
        self.animate_title()
        self.update_ai_status_indicator()

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
        
        # Configure modern button style with darker text
        style.configure(
            "Modern.TButton",
            background='#238636',
            foreground='#0d1117',  # Changed to dark color for visibility
            borderwidth=0,
            focuscolor='none',
            relief='flat',
            padding=(20, 10),
            font=("Segoe UI", 10)
        )
        
        style.map(
            "Modern.TButton",
            background=[('active', '#2ea043'), ('pressed', '#1a7f37')],
            foreground=[('active', '#0d1117'), ('pressed', '#0d1117')]
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

        self.ai_status_label = tk.Label(
            self.title_frame,
            text="AI: Unknown",
            font=("Segoe UI", 10, "bold"),
            bg='#161b22',
            fg='#d29922',
            anchor="e"
        )
        self.ai_status_label.pack(side="right", padx=(0, 20), pady=5)

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

    def update_ai_status_indicator(self):
        state = ai_status.get("state", "unknown")
        message = ai_status.get("message", "")
        color_map = {
            "online": "#3fb950",
            "offline": "#f85149",
            "connecting": "#58a6ff",
            "error": '#d29922',
            "unknown": "#6e7681"
        }
        color = color_map.get(state, "#6e7681")
        self.ai_status_label.config(text=f"AI: {state.capitalize()}", fg=color)
        # Poll every 2 seconds
        self.root.after(2000, self.update_ai_status_indicator)

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

    def clear_content(self):
        """Clear all content from the main content frame"""
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()

    def show_contributors_page(self):
        """Show the ContributorsPage in content_frame"""
        self.clear_content()
        self.contributors_page.pack(fill='both', expand=True)
        self.update_status("Viewing contributors", "👥")

    def show_prompt_view(self):
        """Show the PromptView in content_frame"""
        self.clear_content()
        self.example_var.set("🔽 Choose Example Prompt")  # Reset dropdown
        self.example_menu.pack(pady=(10, 0))
        self.contributors_button.pack(pady=10)
        self.prompt_view.pack(fill='both', expand=True)
        self.update_status("Ready to create amazing web experiences", "🚀")

    def export_code(self):
        """Export code using existing functionality"""
        from ai_engine import generate_code_from_prompt
        from exporter import export_code
        prompt = self.prompt_view.text_input.get("1.0", tk.END).strip()
        if not prompt:
            self.show_notification("Please enter a description", "error")
            return
        code = generate_code_from_prompt(prompt)
        export_code(code)
        self.show_notification("Code exported successfully!", "success")

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