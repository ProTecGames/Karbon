import tkinter as tk
from tkinter import ttk, messagebox
import threading
from ai_engine import generate_code_from_prompt
from preview import update_preview


class PromptView(tk.Frame):
    def __init__(self, master, on_generate):
        super().__init__(master, bg='#0d1117')
        self.on_generate = on_generate
        self.is_generating = False
        self.setup_ui()
        self.bind_all("<Control-g>", lambda event: self.handle_generate())
        self.bind_all("<Control-e>", lambda event: self.export_project())
        self.bind_all("<Control-Shift-c>", lambda event: self.clear_input())

    def setup_ui(self):
        # Hero section with animated gradient background
        self.create_hero_section()

        # Main input card
        self.create_input_section()

        # Features showcase
        self.create_features_section()

        # Quick examples
        self.create_examples_section()

        # Start animations
        self.animate_elements()

    def create_hero_section(self):
        """Create the hero section with animated elements"""
        hero_frame = tk.Frame(self, bg='#0d1117')
        hero_frame.pack(fill="x", pady=(30, 20))

        # Animated welcome text
        self.welcome_label = tk.Label(
            hero_frame,
            text="⚡ Welcome to Karbon",
            font=("Segoe UI", 32, "bold"),
            bg='#0d1117',
            fg='#58a6ff'
        )
        self.welcome_label.pack(pady=(0, 10))

        # Subtitle with typewriter effect
        self.subtitle_label = tk.Label(
            hero_frame,
            text="",
            font=("Segoe UI", 14),
            bg='#0d1117',
            fg='#8b949e'
        )
        self.subtitle_label.pack()

        # Start typewriter effect
        self.typewriter_text = "Transform your ideas into stunning web experiences with AI"
        self.typewriter_index = 0
        self.typewriter_effect()

    def create_input_section(self):
        """Create the main input section with modern card design"""
        # Main card container
        card_container = tk.Frame(self, bg='#0d1117')
        card_container.pack(fill="x", padx=50, pady=30)

        # Card with subtle shadow effect
        input_card = tk.Frame(card_container, bg='#161b22', relief='solid', bd=1)
        input_card.pack(fill="x")

        # Card header
        header_frame = tk.Frame(input_card, bg='#21262d')
        header_frame.pack(fill="x")

        tk.Label(
            header_frame,
            text="🎨 Describe Your Vision",
            font=("Segoe UI", 16, "bold"),
            bg='#21262d',
            fg='#f0f6fc',
            padx=25,
            pady=15
        ).pack(anchor="w")

        # Input area
        input_frame = tk.Frame(input_card, bg='#161b22')
        input_frame.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        # Modern text input with placeholder
        self.text_input = tk.Text(
            input_frame,
            height=6,
            font=("Consolas", 12),
            bg='#0d1117',
            fg='#f0f6fc',
            insertbackground='#58a6ff',
            selectbackground='#264f78',
            relief='solid',
            bd=1,
            padx=20,
            pady=15,
            wrap=tk.WORD
        )
        self.text_input.pack(fill="both", expand=True, pady=(10, 15))

        # Placeholder functionality
        self.placeholder_text = "Describe your dream website... \n\nExample: Create a modern portfolio website with dark theme, smooth animations, and a contact form. Include sections for projects, skills, and about me."
        self.setup_placeholder()

        # Button container
        button_frame = tk.Frame(input_card, bg='#161b22')
        button_frame.pack(fill="x", padx=25, pady=(0, 25))

        # Generate button with loading animation
        self.generate_btn = tk.Button(
            button_frame,
            text="🚀 Generate My Website",
            font=("Segoe UI", 14, "bold"),
            bg='#238636',
            fg='white',
            activebackground='#2ea043',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=40,
            pady=15,
            cursor='hand2',
            command=self.handle_generate
        )
        self.generate_btn.pack(side="right")

        # Secondary actions
        self.create_secondary_buttons(button_frame)

    def create_secondary_buttons(self, parent):
        """Create secondary action buttons"""
        # Clear button
        clear_btn = tk.Button(
            parent,
            text="🗑️ Clear",
            font=("Segoe UI", 11),
            bg='#21262d',
            fg='#8b949e',
            activebackground='#30363d',
            activeforeground='#f0f6fc',
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.clear_input
        )
        clear_btn.pack(side="right", padx=(0, 15))

        # Random idea button
        random_btn = tk.Button(
            parent,
            text="🎲 Surprise Me",
            font=("Segoe UI", 11),
            bg='#6f42c1',
            fg='white',
            activebackground='#8a63d2',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.random_idea
        )
        random_btn.pack(side="right", padx=(0, 10))

    def create_features_section(self):
        """Create features showcase"""
        features_frame = tk.Frame(self, bg='#0d1117')
        features_frame.pack(fill="x", padx=50, pady=20)

        tk.Label(
            features_frame,
            text="✨ What Makes Karbon Special",
            font=("Segoe UI", 18, "bold"),
            bg='#0d1117',
            fg='#f0f6fc'
        ).pack(pady=(0, 20))

        # Features grid
        features_container = tk.Frame(features_frame, bg='#0d1117')
        features_container.pack(fill="x")

        features = [
            ("🤖", "AI-Powered", "Advanced AI creates professional websites from simple descriptions"),
            ("⚡", "Lightning Fast", "Generate complete websites in seconds, not hours"),
            ("🎨", "Beautiful Design", "Modern, responsive designs that look great everywhere"),
            ("🔧", "Fully Customizable", "Edit and modify the generated code to match your vision")
        ]

        for i, (icon, title, desc) in enumerate(features):
            feature_card = tk.Frame(features_container, bg='#161b22', relief='solid', bd=1)
            feature_card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="ew")

            # Configure grid weights
            features_container.grid_columnconfigure(0, weight=1)
            features_container.grid_columnconfigure(1, weight=1)

            tk.Label(
                feature_card,
                text=icon,
                font=("Segoe UI", 24),
                bg='#161b22'
            ).pack(pady=(15, 5))

            tk.Label(
                feature_card,
                text=title,
                font=("Segoe UI", 12, "bold"),
                bg='#161b22',
                fg='#58a6ff'
            ).pack()

            tk.Label(
                feature_card,
                text=desc,
                font=("Segoe UI", 9),
                bg='#161b22',
                fg='#8b949e',
                wraplength=200,
                justify=tk.CENTER
            ).pack(pady=(5, 15), padx=15)

    def create_examples_section(self):
        """Create quick examples section"""
        examples_frame = tk.Frame(self, bg='#0d1117')
        examples_frame.pack(fill="x", padx=50, pady=20)

        tk.Label(
            examples_frame,
            text="🚀 Quick Start Ideas",
            font=("Segoe UI", 16, "bold"),
            bg='#0d1117',
            fg='#f0f6fc'
        ).pack(anchor="w", pady=(0, 15))

        examples = [
            "💼 Professional portfolio with project showcase and contact form",
            "🛍️ E-commerce store with product catalog and shopping cart",
            "📱 Mobile-first landing page with call-to-action buttons",
            "📊 Dashboard with charts and data visualization",
            "📝 Blog platform with article management and comments",
            "🍔 Restaurant website with menu and online ordering"
        ]

        for example in examples:
            example_btn = tk.Button(
                examples_frame,
                text=example,
                font=("Segoe UI", 10),
                bg='#21262d',
                fg='#8b949e',
                activebackground='#30363d',
                activeforeground='#58a6ff',
                relief='flat',
                bd=0,
                padx=20,
                pady=12,
                cursor='hand2',
                anchor='w',
                command=lambda ex=example: self.set_example(ex)
            )
            example_btn.pack(fill="x", pady=2)

            # Hover effect
            def on_enter(e, btn=example_btn):
                btn.configure(bg='#30363d', fg='#58a6ff')
            def on_leave(e, btn=example_btn):
                btn.configure(bg='#21262d', fg='#8b949e')

            example_btn.bind("<Enter>", on_enter)
            example_btn.bind("<Leave>", on_leave)

    def setup_placeholder(self):
        """Setup placeholder functionality"""
        self.text_input.insert("1.0", self.placeholder_text)
        self.text_input.configure(fg='#6e7681')

        def on_focus_in(event):
            if self.text_input.get("1.0", "end-1c") == self.placeholder_text:
                self.text_input.delete("1.0", "end")
                self.text_input.configure(fg='#f0f6fc')

        def on_focus_out(event):
            if not self.text_input.get("1.0", "end-1c").strip():
                self.text_input.insert("1.0", self.placeholder_text)
                self.text_input.configure(fg='#6e7681')

        self.text_input.bind('<FocusIn>', on_focus_in)
        self.text_input.bind('<FocusOut>', on_focus_out)

    def typewriter_effect(self):
        """Animate subtitle with typewriter effect"""
        if self.typewriter_index < len(self.typewriter_text):
            current_text = self.typewriter_text[:self.typewriter_index + 1]
            self.subtitle_label.configure(text=current_text)
            self.typewriter_index += 1
            self.after(50, self.typewriter_effect)
        else:
            # Add blinking cursor effect
            self.blink_cursor()

    def blink_cursor(self):
        """Add blinking cursor effect"""
        current_text = self.subtitle_label.cget("text")
        if current_text.endswith("_"):
            self.subtitle_label.configure(text=current_text[:-1])
        else:
            self.subtitle_label.configure(text=current_text + "_")
        self.after(500, self.blink_cursor)

    def animate_elements(self):
        """Animate UI elements"""
        # Animate welcome text color
        colors = ['#58a6ff', '#79c0ff', '#a5d6ff', '#79c0ff']
        color_index = [0]

        def animate_welcome():
            self.welcome_label.configure(fg=colors[color_index[0] % len(colors)])
            color_index[0] += 1
            self.after(3000, animate_welcome)

        animate_welcome()

    def set_example(self, example):
        """Set example text in input"""
        self.text_input.delete("1.0", "end")
        # Remove emoji and clean up text
        clean_example = " ".join(example.split()[1:])
        self.text_input.insert("1.0", clean_example)
        self.text_input.configure(fg='#f0f6fc')

    def clear_input(self):
        """Clear input field"""
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", self.placeholder_text)
        self.text_input.configure(fg='#6e7681')

    def random_idea(self):
        """Generate a random project idea"""
        import random

        templates = [
            "modern portfolio website with dark theme and smooth animations",
            "e-commerce platform with product reviews and secure checkout",
            "social media dashboard with real-time notifications",
            "food delivery app with restaurant listings and order tracking",
            "fitness tracker with workout plans and progress charts",
            "online learning platform with video courses and quizzes",
            "real estate website with property search and virtual tours",
            "music streaming app with playlists and recommendations",
            "travel booking site with hotel and flight search",
            "cryptocurrency tracker with live prices and portfolio management"
        ]

        styles = ["minimalist", "colorful", "professional", "creative", "elegant"]
        features = ["responsive design", "mobile-first approach", "accessibility features", "SEO optimization"]

        random_idea = f"Create a {random.choice(styles)} {random.choice(templates)} with {random.choice(features)}"

        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", random_idea)
        self.text_input.configure(fg='#f0f6fc')

    def handle_generate(self):
        """Handle generate button click with enhanced UX"""
        if self.is_generating:
            return

        prompt = self.text_input.get("1.0", "end-1c").strip()

        if not prompt or prompt == self.placeholder_text:
            self.show_error("Please describe your website idea first! 💡")
            return

        if len(prompt) < 10:
            self.show_error("Please provide more details about your website. The more specific you are, the better the result! 🎯")
            return

        self.start_generation(prompt)

    def start_generation(self, prompt):
        """Start the generation process with visual feedback"""
        self.is_generating = True

        # Update button to loading state
        self.generate_btn.configure(
            text="🔄 Creating Magic...",
            state='disabled',
            bg='#6e7681'
        )

        # Show progress indicator
        self.show_progress()

        # Start generation in background thread
        def generate_in_background():
            try:
                # Get API key and model source from the main UI
                api_key = self.master.master.master.get_api_key()
                model_source = self.master.master.master.get_model_source()
                code = generate_code_from_prompt(prompt, api_key, model_source)
                update_preview(code)

                # Call completion on main thread
                self.after(0, lambda: self.generation_complete(code))

            except Exception as e:
                self.after(0, lambda: self.generation_error(str(e)))

        threading.Thread(target=generate_in_background, daemon=True).start()

    def show_progress(self):
        """Show animated progress indicator"""
        progress_texts = [
            "🔄 Analyzing your idea...",
            "🎨 Designing the layout...",
            "⚡ Generating HTML & CSS...",
            "🚀 Adding interactive features...",
            "✨ Finalizing your website..."
        ]

        self.progress_index = 0

        def update_progress():
            if self.is_generating and self.progress_index < len(progress_texts):
                self.generate_btn.configure(text=progress_texts[self.progress_index])
                self.progress_index += 1
                self.after(1500, update_progress)

        update_progress()

    def generation_complete(self, code):
        """Handle successful generation"""
        self.is_generating = False

        # Reset button
        self.generate_btn.configure(
            text="🚀 Generate My Website",
            state='normal',
            bg='#238636'
        )

        # Show success notification
        self.show_success("Website generated successfully! 🎉")

        # Call the callback
        self.on_generate(code)

    def generation_error(self, error_msg):
        """Handle generation error"""
        self.is_generating = False

        # Reset button
        self.generate_btn.configure(
            text="🚀 Generate My Website",
            state='normal',
            bg='#238636'
        )

        # Show error
        self.show_error(f"Oops! Something went wrong: {error_msg}")

    def show_error(self, message):
        """Show enhanced error dialog"""
        error_window = tk.Toplevel(self)
        error_window.title("Oops!")
        error_window.geometry("450x200")
        error_window.configure(bg='#21262d')
        error_window.resizable(False, False)

        # Center the window
        error_window.transient(self.winfo_toplevel())
        error_window.grab_set()

        # Center position
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() // 2) - 225
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() // 2) - 100
        error_window.geometry(f"450x200+{x}+{y}")

        # Error icon and title
        tk.Label(
            error_window,
            text="⚠️",
            font=("Segoe UI", 32),
            bg='#21262d',
            fg='#f85149'
        ).pack(pady=(20, 10))

        tk.Label(
            error_window,
            text=message,
            font=("Segoe UI", 11),
            bg='#21262d',
            fg='#f0f6fc',
            wraplength=400,
            justify=tk.CENTER
        ).pack(pady=10, padx=20)

        # OK button
        tk.Button(
            error_window,
            text="Got it! 👍",
            font=("Segoe UI", 11),
            bg='#238636',
            fg='white',
            relief='flat',
            padx=30,
            pady=10,
            command=error_window.destroy
        ).pack(pady=20)

    def show_success(self, message):
        """Show success notification"""
        success_window = tk.Toplevel(self)
        success_window.title("Success!")
        success_window.geometry("400x150")
        success_window.configure(bg='#21262d')
        success_window.resizable(False, False)
        success_window.attributes('-topmost', True)

        # Auto-position in top-right
        x = self.winfo_toplevel().winfo_x() + self.winfo_toplevel().winfo_width() - 420
        y = self.winfo_toplevel().winfo_y() + 50
        success_window.geometry(f"400x150+{x}+{y}")

        tk.Label(
            success_window,
            text="🎉",
            font=("Segoe UI", 24),
            bg='#21262d'
        ).pack(pady=(20, 5))

        tk.Label(
            success_window,
            text=message,
            font=("Segoe UI", 12),
            bg='#21262d',
            fg='#3fb950'
        ).pack(pady=5)

        # Auto-close after 3 seconds
        success_window.after(3000, success_window.destroy)
