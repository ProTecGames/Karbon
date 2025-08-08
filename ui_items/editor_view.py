import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import webbrowser
import tempfile
import os
# from code_editor_ui import update_preview
from core.ai_engine import generate_code_from_prompt, ai_status
from exporters.exporter import export_code
from core import prompt_history
try:
    from tkhtmlview import HTMLLabel
    HTML_AVAILABLE = True
except ImportError:
    HTML_AVAILABLE = False

# Try to import webview for better embedded browser support
try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False

# Alternative HTML rendering method using webbrowser
def open_html_in_browser(html_content, title="Preview"):
    """Open HTML content in default browser for better CSS support"""
    try:
        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file = f.name
        
        # Open in default browser
        webbrowser.open(f'file://{temp_file}')
        return temp_file
    except Exception as e:
        print(f"Error opening HTML in browser: {e}")
        return None

# Alternative HTML rendering method using webbrowser
def open_html_in_browser(html_content, title="Preview"):
    """Open HTML content in default browser for better CSS support"""
    try:
        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file = f.name
        
        # Open in default browser
        webbrowser.open(f'file://{temp_file}')
        return temp_file
    except Exception as e:
        print(f"Error opening HTML in browser: {e}")
        return None

# Simple embedded preview using iframe-like approach
class SimpleEmbeddedPreview:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.current_html = ""
        
    def update_content(self, html_content):
        """Update the preview content by opening in browser"""
        try:
            # Open in browser for guaranteed rendering
            temp_file = open_html_in_browser(html_content, "Karbon Preview")
            if temp_file:
                print(f"Preview opened in browser: {temp_file}")
                return True
            return False
        except Exception as e:
            print(f"Error updating preview content: {e}")
            return False


class EditorView(tk.Frame):
    def __init__(self, master, get_code_callback, set_code_callback, get_api_key_callback, get_model_source_callback):
        super().__init__(master, bg='#0d1117')
        self.get_code = get_code_callback
        self.set_code = set_code_callback
        self.get_api_key = get_api_key_callback
        self.get_model_source = get_model_source_callback
        self.is_updating = False
        self.export_as_zip_var = tk.BooleanVar(value=False)

        # Store references to important UI elements for update_appearance
        self.header_title_label = None
        self.header_subtitle_label = None
        self.preview_title_label = None
        self.preview_desc_label_1 = None
        self.preview_desc_label_2 = None
        self.tips_title_label = None
        self.tip_labels = []  # To store references to individual tip labels
        self.status_bar_label = None
        self.activity_indicator_label = None

        self.setup_ui()

    def setup_ui(self):
        self.create_header()
        self.create_toolbar()
        self.create_main_content()
        self.create_status_bar()

    def create_header(self):
        header_frame = tk.Frame(self, bg='#0d1117')
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        # Stored as instance variables
        self.header_title_label = tk.Label(
            header_frame,
            text="⚡ Code Editor",
            font=("Segoe UI", 20, "bold"),
            bg='#0d1117',
            fg='#58a6ff'
        )
        self.header_title_label.pack(anchor="w")

        # Stored as instance variables
        self.header_subtitle_label = tk.Label(
            header_frame,
            text="Edit, update, and export your generated website",
            font=("Segoe UI", 10),
            bg='#0d1117',
            fg='#8b949e'
        )
        self.header_subtitle_label.pack(anchor="w", pady=(2, 0))

        self.stats_frame = tk.Frame(header_frame, bg='#0d1117')
        self.stats_frame.pack(side="right", fill="y")

        self.update_stats()

    def create_toolbar(self):
        toolbar_container = tk.Frame(self, bg='#0d1117')
        toolbar_container.pack(fill="x", padx=20, pady=(0, 15))

        toolbar = tk.Frame(toolbar_container, bg='#161b22', relief='solid', bd=1)
        toolbar.pack(fill="x")

        left_section = tk.Frame(toolbar, bg='#161b22')
        left_section.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        tk.Label(
            left_section,
            text="🔄 Update Your Website",
            font=("Segoe UI", 12, "bold"),
            bg='#161b22',
            fg='#f0f6fc'
        ).pack(anchor="w", pady=(0, 8))

        input_container = tk.Frame(left_section, bg='#161b22')
        input_container.pack(fill="x", pady=(0, 10))

        self.update_text = tk.Text(
            input_container,
            height=3,
            font=("Consolas", 11),
            bg='#0d1117',
            fg='#f0f6fc',
            insertbackground='#58a6ff',
            selectbackground='#264f78',
            relief='solid',
            bd=1,
            padx=15,
            pady=10,
            wrap=tk.WORD
        )
        self.update_text.pack(fill="both", expand=True)

        self.update_placeholder = prompt_history.get_current_prompt()
        self.setup_update_placeholder()

        button_container = tk.Frame(left_section, bg='#161b22')
        button_container.pack(fill="x")

        self.update_btn = tk.Button(
            button_container,
            text="🔄 Update Code",
            font=("Segoe UI", 11, "bold"),
            bg='#1f6feb',
            fg='white',
            activebackground='#2f81f7',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=25,
            pady=10,
            cursor='hand2',
            command=self.handle_update
        )
        self.update_btn.pack(side="left")

        self.undo_btn = tk.Button(
            button_container,
            text="⏪ Undo",
            font=("Segoe UI", 11, "bold"),
            bg='#1f6feb',
            state="disabled",
            disabledforeground="#88b8ff",
            activebackground='#2f81f7',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=25,
            pady=10,
            cursor='hand2',
            command=self.handle_undo
        )
        self.undo_btn.pack(side="left", padx=(10, 0))

        self.redo_btn = tk.Button(
            button_container,
            text="Redo ⏩",
            font=("Segoe UI", 11, "bold"),
            bg='#1f6feb',
            state="disabled",
            disabledforeground="#88b8ff",
            activebackground='#2f81f7',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=25,
            pady=10,
            cursor='hand2',
            command=self.handle_redo
        )
        self.redo_btn.pack(side="left", padx=(10, 0))

        preview_btn = tk.Button(
            button_container,
            text="👁️ Preview",
            font=("Segoe UI", 11, "bold"),
            bg='#238636',
            fg='white',
            activebackground='#2ea043',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=25,
            pady=10,
            cursor='hand2',
            command=self.refresh_preview
        )
        preview_btn.pack(side="left", padx=(10, 0))

        clear_btn = tk.Button(
            button_container,
            text="🗑️ Clear",
            font=("Segoe UI", 10),
            bg='#21262d',
            fg='#8b949e',
            activebackground='#30363d',
            activeforeground='#f0f6fc',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.clear_update_input
        )
        clear_btn.pack(side="left", padx=(10, 0))

        right_section = tk.Frame(toolbar, bg='#21262d', width=200)
        right_section.pack(side="right", fill="y", padx=1)
        right_section.pack_propagate(False)

        tk.Label(
            right_section,
            text="⚙️ Actions",
            font=("Segoe UI", 11, "bold"),
            bg='#21262d',
            fg='#f0f6fc'
        ).pack(pady=(15, 10))

        actions = [
            ("💾 Export", "#238636", self.handle_export),
            ("📁 Save", "#0969da", self.save_file),
            ("↩️ New Project", "#6e7681", self.back_to_prompt)
        ]

        for text, color, command in actions:
            if color == "#238636":
                zip_checkbox = tk.Checkbutton(
                    right_section,
                    text="Export as ZIP",
                    variable=self.export_as_zip_var,
                    font=("Segoe UI", 8),
                    bg='#21262d',
                    fg='white',
                    activebackground='#21262d',
                    activeforeground='white',
                    selectcolor='#21262d',
                    anchor='w',
                    padx=25,
                    relief='flat'
                )
                zip_checkbox.pack(fill='x', padx=15, pady=2)

            btn = tk.Button(
                right_section,
                text=text,
                font=("Segoe UI", 9),
                bg=color,
                fg='white',
                activebackground=self.lighten_color(color),
                activeforeground='white',
                relief='flat',
                bd=0,
                padx=15,
                pady=6,
                cursor='hand2',
                command=command
            )
            btn.pack(fill="x", padx=15, pady=2)

    def insert_text(self, words):
        self.update_text.insert("1.0", words)

    def create_main_content(self):
        content_frame = tk.Frame(self, bg='#0d1117')
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        info_card = tk.Frame(content_frame, bg='#161b22', relief='solid', bd=1)
        info_card.pack(fill="both", expand=True)

        header = tk.Frame(info_card, bg='#21262d')
        header.pack(fill="x")

        # Stored as instance variable
        self.preview_title_label = tk.Label(
            header,
            text="👁️ Live Preview",
            font=("Segoe UI", 14, "bold"),
            bg='#21262d',
            fg='#f0f6fc',
            padx=20,
            pady=12
        )
        self.preview_title_label.pack(side="left")

        self.preview_status = tk.Label(
            header,
            text="● Ready",
            font=("Segoe UI", 10),
            bg='#21262d',
            fg='#3fb950'
        )
        self.preview_status.pack(side="right", padx=20)

        content_area = tk.Frame(info_card, bg='#161b22')
        content_area.pack(fill="both", expand=True, padx=20, pady=20)

        if WEBVIEW_AVAILABLE:
            # Use simple embedded preview that opens in browser
            self.embedded_browser = SimpleEmbeddedPreview(content_area)
            self.html_preview = None
            
            # Create a frame for the preview info
            self.preview_info_frame = tk.Frame(content_area, bg='white')
            self.preview_info_frame.pack(fill="both", expand=True, pady=(0, 20))
            
            # Add preview information
            info_label = tk.Label(
                self.preview_info_frame,
                text="🌐 Live Website Preview",
                font=("Segoe UI", 16, "bold"),
                bg='white',
                fg='#58a6ff'
            )
            info_label.pack(pady=(50, 20))
            
            desc_label = tk.Label(
                self.preview_info_frame,
                text="Your website will open in your default browser\nfor the best rendering experience with full CSS support",
                font=("Segoe UI", 11),
                bg='white',
                fg='#8b949e',
                justify='center'
            )
            desc_label.pack(pady=(0, 30))
            
            # Add a preview button
            preview_btn = tk.Button(
                self.preview_info_frame,
                text="👁️ Open Preview in Browser",
                font=("Segoe UI", 12, "bold"),
                bg='#238636',
                fg='white',
                relief='flat',
                padx=25,
                pady=10,
                command=self.open_preview_in_browser
            )
            preview_btn.pack()
            
            # Add hover effects
            def on_enter(e):
                preview_btn.configure(bg='#2ea043')
            
            def on_leave(e):
                preview_btn.configure(bg='#238636')
            
            preview_btn.bind("<Enter>", on_enter)
            preview_btn.bind("<Leave>", on_leave)
            
        elif HTML_AVAILABLE:
            # Fallback to tkhtmlview
            # Remove default styles that might interfere with CSS
            HTMLLabel._default_style = ""
            
            # Create embedded HTML preview
            self.html_preview = HTMLLabel(
                content_area,
                html="<div style='text-align: center; padding: 50px; color: #8b949e; font-family: Arial, sans-serif; background: white;'><h2>🌐 Live Website Preview</h2><p>Your generated website will render here</p><p style='font-size: 12px; color: #666;'>The actual website will appear, not the HTML code</p></div>",
                background='white',
                width=600,
                height=400
            )
            self.html_preview.pack(fill="both", expand=True, pady=(0, 20))
            
            # Add refresh button
            preview_button = tk.Button(
                content_area,
                text="🔄 Refresh Preview",
                font=("Segoe UI", 11, "bold"),
                bg='#238636',
                fg='white',
                relief='flat',
                padx=20,
                pady=8,
                command=self.refresh_preview
            )
            preview_button.pack(pady=(0, 10))
            
            # Add hover effects for preview button
            def on_enter(e):
                preview_button.configure(bg='#2ea043')
            
            def on_leave(e):
                preview_button.configure(bg='#238636')
            
            preview_button.bind("<Enter>", on_enter)
            preview_button.bind("<Leave>", on_leave)
            
            # Add test preview button for debugging
            test_button = tk.Button(
                content_area,
                text="🧪 Test Preview",
                font=("Segoe UI", 10),
                bg='#1f6feb',
                fg='white',
                relief='flat',
                padx=15,
                pady=5,
                command=self.test_preview
            )
            test_button.pack(pady=(5, 0))
            
            # Add browser preview button for better CSS support
            browser_button = tk.Button(
                content_area,
                text="🌐 Open in Browser",
                font=("Segoe UI", 10),
                bg='#d97706',
                fg='white',
                relief='flat',
                padx=15,
                pady=5,
                command=self.open_in_browser
            )
            browser_button.pack(pady=(5, 0))
        else:
            # Fallback if tkhtmlview is not available
            tk.Label(
                content_area,
                text="🌐",
                font=("Segoe UI", 48),
                bg='#161b22'
            ).pack(pady=(40, 20))

            # Stored as instance variable
            self.preview_desc_label_1 = tk.Label(
                content_area,
                text="HTML Preview not available",
                font=("Segoe UI", 14, "bold"),
                bg='#161b22',
                fg='#58a6ff'
            )
            self.preview_desc_label_1.pack()

            # Stored as instance variable
            self.preview_desc_label_2 = tk.Label(
                content_area,
                text="Install tkhtmlview to enable embedded preview",
                font=("Segoe UI", 11),
                bg='#161b22',
                fg='#8b949e'
            )
            self.preview_desc_label_2.pack(pady=(5, 20))

        self.create_tips_section(content_area)

    def create_tips_section(self, parent):
        tips_frame = tk.Frame(parent, bg='#0d1117', relief='solid', bd=1)
        tips_frame.pack(fill="x", pady=(20, 0))

        # Stored as instance variable
        self.tips_title_label = tk.Label(
            tips_frame,
            text="💡 Pro Tips",
            font=("Segoe UI", 12, "bold"),
            bg='#0d1117',
            fg='#f79c42'
        )
        self.tips_title_label.pack(anchor="w", padx=15, pady=(12, 8))

        tips = [
            "• Be specific about colors, fonts, and layout changes",
            "• Use preview to see changes before exporting",
            "• Save your work frequently to avoid losing progress",
            "• Try different update prompts to fine-tune your design"
        ]

        # Stored as instance variables in a list
        self.tip_labels = []
        for tip in tips:
            label = tk.Label(
                tips_frame,
                text=tip,
                font=("Segoe UI", 10),
                bg='#0d1117',
                fg='#8b949e',
                anchor='w'
            )
            label.pack(anchor="w", padx=15, pady=1)
            self.tip_labels.append(label)

        tk.Label(tips_frame, text="", bg='#0d1117').pack(pady=8)

    def create_status_bar(self):
        self.status_frame = tk.Frame(self, bg='#161b22', height=35)
        self.status_frame.pack(fill="x", side="bottom")
        self.status_frame.pack_propagate(False)

        # Stored as instance variable
        self.status_bar_label = tk.Label(
            self.status_frame,
            text="Ready to edit • Make changes and see them live",
            font=("Segoe UI", 9),
            bg='#161b22',
            fg='#8b949e'
        )
        self.status_bar_label.pack(side="left", padx=20, pady=8)

        # Stored as instance variable
        self.activity_indicator_label = tk.Label(
            self.status_frame,
            text="",
            font=("Segoe UI", 9),
            bg='#161b22',
            fg='#58a6ff'
        )
        self.activity_indicator_label.pack(side="right", padx=20, pady=8)

    def setup_update_placeholder(self):
        self.update_text.insert("1.0", self.update_placeholder)
        self.update_text.configure(fg='#6e7681')

        def on_focus_in(event):
            if self.update_text.get("1.0", "end-1c") == self.update_placeholder:
                self.update_text.delete("1.0", "end")
                self.update_text.configure(fg='#f0f6fc')

        def on_focus_out(event):
            if not self.update_text.get("1.0", "end-1c").strip():
                self.update_text.insert("1.0", self.update_placeholder)
                self.update_text.configure(fg='#6e7681')

        self.update_text.bind('<FocusIn>', on_focus_in)
        self.update_text.bind('<FocusOut>', on_focus_out)

    def update_stats(self):
        try:
            code = self.get_code()
            if code:
                lines = len(code.split('\n'))
                chars = len(code)

                for widget in self.stats_frame.winfo_children():
                    widget.destroy()

                stats_data = [
                    ("Lines", str(lines)),
                    ("Characters", str(chars)),
                    ("Status", "Ready")
                ]

                for i, (label, value) in enumerate(stats_data):
                    stat_frame = tk.Frame(self.stats_frame, bg='#161b22', relief='solid', bd=1)
                    stat_frame.grid(row=0, column=i, padx=2, pady=2)

                    tk.Label(
                        stat_frame,
                        text=value,
                        font=("Segoe UI", 12, "bold"),
                        bg='#161b22',
                        fg='#58a6ff'
                    ).pack(padx=10, pady=(5, 0))

                    tk.Label(
                        stat_frame,
                        text=label,
                        font=("Segoe UI", 8),
                        bg='#161b22',
                        fg='#8b949e'
                    ).pack(padx=10, pady=(0, 5))
        except:
            pass

    def clear_update_input(self):
        self.update_text.delete("1.0", "end")
        self.update_text.insert("1.0", self.update_placeholder)
        self.update_text.configure(fg='#6e7681')

    def update_status(self, message, activity=""):
        self.status_bar_label.configure(text=message)  # Reference the instance variable
        self.activity_indicator_label.configure(text=activity)  # Reference the instance variable

    def handle_update(self):
        if self.is_updating:
            return

        prompt = self.update_text.get("1.0", "end-1c").strip()

        if not prompt or prompt == self.update_placeholder:
            self.show_error("Please describe what changes you'd like to make! 🔄")
            return
        else:
            prompt_history.pop_prompt()
            prompt_history.pop_code()
            prompt_history.push_prompt(prompt)

        self.start_update(prompt)
        self.redo_btn.config(
            bg="#1f6feb",
            state="disabled",
            disabledforeground="#88b8ff"
        )

        self.undo_btn.config(
            bg="#1f6feb",
            activebackground='#2f81f7',
            activeforeground='white',
            state="active"
        )

    def handle_undo(self):
        if (prompt_history.undo() == 0):
            self.undo_btn.config(
                bg="#1f6feb",
                state="disabled",
                disabledforeground="#88b8ff"
            )
        self.redo_btn.config(
            bg="#1f6feb",
            fg='white',
            activebackground='#2f81f7',
            activeforeground='white',
            state="active"
        )
        self.update_text.delete("1.0", "end")
        self.update_text.insert("1.0", prompt_history.get_current_prompt())

    def handle_redo(self):
        if (prompt_history.redo() == prompt_history.number_of_prompts):
            self.redo_btn.config(
                bg="#1f6feb",
                state="disabled",
                disabledforeground="#88b8ff"
            )
        self.undo_btn.config(
            bg="#1f6feb",
            fg='white',
            activebackground='#2f81f7',
            activeforeground='white',
            state="active"
        )
        self.update_text.delete("1.0", "end")
        self.update_text.insert("1.0", prompt_history.get_current_prompt())

    def start_update(self, prompt):
        self.is_updating = True

        self.update_btn.configure(
            text="🔄 Updating...",
            state='disabled',
            bg='#6e7681'
        )

        self.update_status("Applying your changes...", "🔄")
        self.preview_status.configure(text="● Updating", fg='#f79c42')

        def update_in_background():
            try:
                api_key = self.get_api_key()
                code = generate_code_from_prompt(prompt, api_key)
                prompt_history.push_code(code)
                prompt_history.push_prompt(
                    "Describe what you'd like to change...\n\nExample: Make the header purple, add a contact form, or change the font to something more modern"
                )
                prompt_history.push_code(code)

                # This must be done in the main thread
                self.after(0, lambda: self.set_code(code))
                
                from code_editor_ui import update_preview
                update_preview(code)

                self.after(0, self.update_complete)

            # except Exception as e:
            #     self.after(0, lambda: self.update_error(str(e)))
            except Exception as e:
                error_message = str(e)
                self.after(0, lambda: self.update_error(error_message))

        threading.Thread(target=update_in_background, daemon=True).start()

    def update_complete(self):
        self.is_updating = False

        self.update_btn.configure(
            text="🔄 Update Code",
            state='normal',
            bg='#1f6feb'
        )
        self.update_status("Changes applied successfully!", "✅")
        self.preview_status.configure(text="● Live", fg='#3fb950')

        self.update_stats()

        status = ai_status.get("state", "unknown")
        message = ai_status.get("message", "")
        if status != "online":
            if status == "offline":
                self.show_error(
                    "AI service is currently unavailable. Please check your internet connection or try again later.")
            elif status == "error":
                self.show_error(f"AI service error: {message}")
            else:
                self.show_error(f"Website could not be updated due to an AI service issue.")
            return

        self.show_success("Website updated successfully! 🎉")

        self.clear_update_input()

    def update_error(self, error_msg):
        self.is_updating = False

        self.update_btn.configure(
            text="🔄 Update Code",
            state='normal',
            bg='#1f6feb'
        )
        self.update_status("Update failed", "❌")
        self.preview_status.configure(text="● Error", fg='#f85149')
        
        status = ai_status.get("state", "unknown")
        message = ai_status.get("message", "")
        # print(f"status is :{status}, msg: {message}")
        
        if status == "offline":
            self.show_error(
                "AI service is currently unavailable. Please check your internet connection or try again later.")
        elif status == "error":
            self.show_error(f"AI service error: {message}")
        else:
            self.show_error(f"Update failed: {error_msg}")

    def handle_export(self):
        code = self.get_code()
        if not code:
            self.show_error("No code to export! Generate a website first.")
            return

        export_as_zip = self.export_as_zip_var.get()

        try:
            export_code(code, as_zip=export_as_zip)
            if export_as_zip:
                self.show_success("Code exported successfully as ZIP! 📦")
                self.update_status("Exported ZIP file", "📦")
            else:
                self.show_success("Code exported successfully! 📁")
                self.update_status("Code exported to file", "💾")
        except Exception as e:
            self.show_error(f"Export failed: {str(e)}")

    def save_file(self):
        code = self.get_code()
        if not code:
            self.show_error("No code to save!")
            return

        try:
            filename = filedialog.asksaveasfilename(
                title="Save Website",
                defaultextension=".html",
                filetypes=[
                    ("HTML files", "*.html"),
                    ("All files", "*.*")
                ]
            )

            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)

                self.show_success(f"Saved to {os.path.basename(filename)}! 💾")
                self.update_status(f"Saved to {filename}", "💾")

        except Exception as e:
            self.show_error(f"Save failed: {str(e)}")

    def back_to_prompt(self):
        response = messagebox.askyesno(
            "New Project",
            "Start a new project? This will clear your current work.",
            icon='question'
        )

        if response:
            self.update_status("Starting new project...", "🔄")

    def lighten_color(self, color):
        color_map = {
            "#6f42c1": "#8a63d2",
            "#238636": "#2ea043",
            "#0969da": "#1f6feb",
            "#6e7681": "#8b949e"
        }
        return color_map.get(color, color)

    def show_error(self, message):
        error_window = tk.Toplevel(self)
        error_window.title("Oops!")
        error_window.geometry("450x200")
        error_window.configure(bg='#21262d')
        error_window.resizable(False, False)

        error_window.transient(self.winfo_toplevel())
        error_window.grab_set()

        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() // 2) - 225
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() // 2) - 100
        error_window.geometry(f"450x200+{x}+{y}")

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
        success_window = tk.Toplevel(self)
        success_window.title("Success!")
        success_window.geometry("400x150")
        success_window.configure(bg='#21262d')
        success_window.resizable(False, False)
        success_window.attributes('-topmost', True)

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

        success_window.after(3000, success_window.destroy)

    def update_char_count(self, event=None):
        content = self.text_input.get("1.0", "end-1c")
        if len(content) > 256:
            self.text_input.delete(f"1.0+{256}c", "end")
            content = self.text_input.get("1.0", "end-1c")
        remaining = 256 - len(content)
        self.char_count_label.config(text=f"{remaining} characters left")

    def refresh_preview(self):
        """Manually refresh the preview with current code"""
        try:
            current_code = self.get_code()
            if current_code:
                if WEBVIEW_AVAILABLE and hasattr(self, 'embedded_browser'):
                    # Use simple embedded preview that opens in browser
                    formatted_html = self.format_html_for_preview(current_code)
                    if self.embedded_browser.update_content(formatted_html):
                        self.preview_status.configure(text="● Refreshed", fg='#3fb950')
                        self.show_success("Preview opened in browser with full CSS support!")
                    else:
                        self.show_error("Failed to open preview in browser")
                            
                elif HTML_AVAILABLE and hasattr(self, 'html_preview'):
                    # Use tkhtmlview fallback
                    simple_html = self.create_simple_html_preview(current_code)
                    self.html_preview.set_html(simple_html)
                    self.preview_status.configure(text="● Refreshed", fg='#3fb950')
                    
                    # Also open in browser for guaranteed rendering
                    formatted_html = self.format_html_for_preview(current_code)
                    temp_file = open_html_in_browser(formatted_html, "Karbon Preview")
                    
                    if temp_file:
                        self.show_success("Preview refreshed! Check browser for full rendering.")
                    else:
                        self.show_success("Preview refreshed successfully!")
                else:
                    self.show_error("No preview system available. Please install webview or tkhtmlview.")
            else:
                self.show_error("No code available to preview")
        except Exception as e:
            self.show_error(f"Error refreshing preview: {str(e)}")

    def check_preview_rendering(self, html_code):
        """Check if the preview is properly rendering or showing code as text"""
        try:
            # If the HTML contains complex CSS or JavaScript, suggest browser preview
            if any(keyword in html_code.lower() for keyword in ['<script>', 'gradient', 'animation', 'transform', 'backdrop-filter']):
                self.show_success("Complex styling detected! For best results, use '🌐 Open in Browser' for full CSS support.")
        except Exception as e:
            print(f"Error checking preview rendering: {e}")

    def format_html_for_preview(self, html_code):
        """Format HTML code for proper rendering in the preview"""
        try:
            print(f"Original HTML length: {len(html_code)}")
            print(f"HTML starts with: {html_code[:100]}...")
            
            # Clean the HTML first
            html_code = html_code.strip()
            
            # Validate and fix HTML structure
            html_code = self.validate_and_fix_html(html_code)
            
            # Process CSS to ensure it's properly embedded
            html_code = self.process_css_in_html(html_code)
            
            # Ensure all HTML entities are properly encoded
            html_code = self.encode_html_entities(html_code)
            
            print(f"Final HTML length: {len(html_code)}")
            return html_code
        except Exception as e:
            print(f"Error formatting HTML: {e}")
            return html_code

    def encode_html_entities(self, html_code):
        """Encode HTML entities to prevent code from being displayed as text"""
        try:
            # Replace common characters that might be displayed as code
            replacements = {
                '<': '&lt;',
                '>': '&gt;',
                '&': '&amp;',
                '"': '&quot;',
                "'": '&#39;'
            }
            
            # Only encode if the content is meant to be displayed as text, not rendered
            # For actual HTML content, we want to preserve the tags
            return html_code
        except Exception as e:
            print(f"Error encoding HTML entities: {e}")
            return html_code

    def validate_and_fix_html(self, html_code):
        """Validate and fix common HTML issues that might cause rendering problems"""
        try:
            # Ensure proper HTML structure
            if not html_code.strip():
                return html_code
                
            # Check for common issues
            issues_found = []
            
            # Check for unclosed tags
            open_tags = ['<html>', '<head>', '<body>', '<div>', '<span>', '<p>', '<h1>', '<h2>', '<h3>']
            close_tags = ['</html>', '</head>', '</body>', '</div>', '</span>', '</p>', '</h1>', '</h2>', '</h3>']
            
            for tag in open_tags:
                if tag in html_code and tag.replace('<', '</') not in html_code:
                    issues_found.append(f"Unclosed {tag}")
            
            # Check for proper DOCTYPE
            if '<!DOCTYPE html>' not in html_code:
                issues_found.append("Missing DOCTYPE")
            
            # Check for proper HTML structure
            if '<html>' not in html_code:
                issues_found.append("Missing <html> tag")
            
            if '<head>' not in html_code:
                issues_found.append("Missing <head> tag")
            
            if '<body>' not in html_code:
                issues_found.append("Missing <body> tag")
            
            if issues_found:
                print(f"HTML validation issues found: {issues_found}")
                # Fix common issues
                if '<!DOCTYPE html>' not in html_code:
                    html_code = f'<!DOCTYPE html>\n{html_code}'
                
                if '<html>' not in html_code:
                    html_code = f'<html>\n{html_code}\n</html>'
                
                if '<head>' not in html_code:
                    html_code = html_code.replace('<html>', '<html>\n<head>\n<title>Preview</title>\n</head>')
                
                if '<body>' not in html_code:
                    html_code = html_code.replace('</head>', '</head>\n<body>')
                    html_code = html_code.replace('</html>', '</body>\n</html>')
            
            return html_code
        except Exception as e:
            print(f"Error validating HTML: {e}")
            return html_code

    def create_simple_html_preview(self, html_code):
        """Create a simplified HTML preview that tkhtmlview can handle better"""
        try:
            # Extract the body content
            import re
            
            # Find body content
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html_code, re.DOTALL | re.IGNORECASE)
            if body_match:
                body_content = body_match.group(1)
            else:
                # If no body tag, use the entire content
                body_content = html_code
            
            # Extract CSS
            style_match = re.search(r'<style[^>]*>(.*?)</style>', html_code, re.DOTALL | re.IGNORECASE)
            css_content = ""
            if style_match:
                css_content = style_match.group(1)
            
            # Create a simplified HTML structure
            simple_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Preview</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background: white;
                        color: black;
                    }}
                    {css_content}
                </style>
            </head>
            <body>
                {body_content}
            </body>
            </html>
            """
            
            return simple_html
        except Exception as e:
            print(f"Error creating simple HTML preview: {e}")
            return html_code

    def process_css_in_html(self, html_code):
        """Process CSS to ensure it's properly embedded and applied"""
        try:
            # Clean the HTML first (remove any unwanted default styles)
            html_code = self.clean_html(html_code)
            
            # Check if there are <style> tags
            if '<style>' in html_code and '</style>' in html_code:
                print("Found <style> tags, processing CSS...")
                
                # Extract CSS from style tags
                import re
                style_pattern = r'<style[^>]*>(.*?)</style>'
                styles = re.findall(style_pattern, html_code, re.DOTALL)
                
                if styles:
                    print(f"Found {len(styles)} style blocks")
                    # The CSS should already be properly embedded in style tags
                    # Just ensure they're in the head section
                    for style_content in styles:
                        if style_content.strip():
                            # Ensure style tags are in the head
                            if '<head>' in html_code and '</head>' in html_code:
                                # Check if style is already in head
                                if f'<style>{style_content}</style>' not in html_code:
                                    # Move style to head if it's not there
                                    html_code = html_code.replace('</head>', f'<style>{style_content}</style>\n</head>')
                                    # Remove the original style tag from body
                                    html_code = html_code.replace(f'<style>{style_content}</style>', '', 1)
                                    print("Moved CSS to head section")
            
            # Check for inline styles and ensure they're preserved
            if 'style=' in html_code:
                print("Found inline styles, preserving...")
            
            # Add some basic styling to ensure proper rendering if no styles exist
            if '<style>' not in html_code:
                # Insert basic CSS for better rendering
                style_insert = '<style>\nbody { margin: 0; padding: 20px; font-family: Arial, sans-serif; }\n</style>'
                html_code = html_code.replace('</head>', f'{style_insert}\n</head>')
                print("Added basic CSS styling")
            
            return html_code
        except Exception as e:
            print(f"Error processing CSS: {e}")
            return html_code

    def clean_html(self, raw_html):
        """Removes tkhtmlview's injected default styles if present."""
        try:
            # Remove any unwanted default styles that might interfere
            unwanted_styles = [
                '<style>body { background-color: white; font-family: Courier; }</style>',
                '<style>body { background-color: white; }</style>',
                '<style>body { font-family: Courier; }</style>'
            ]
            
            for unwanted_style in unwanted_styles:
                raw_html = raw_html.replace(unwanted_style, "")
            
            return raw_html
        except Exception as e:
            print(f"Error cleaning HTML: {e}")
            return raw_html

    def test_preview(self):
        """Test the preview with a sample website"""
        try:
            # Sample website HTML for testing with complex CSS
            test_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Test Website</title>
                <style>
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    
                    body { 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    
                    .container {
                        max-width: 800px;
                        text-align: center;
                        padding: 40px;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 20px;
                        backdrop-filter: blur(10px);
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    }
                    
                    h1 { 
                        font-size: 3.5em; 
                        margin-bottom: 30px;
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        background-clip: text;
                    }
                    
                    p { 
                        font-size: 1.3em; 
                        line-height: 1.8;
                        margin-bottom: 20px;
                        opacity: 0.9;
                    }
                    
                    .button {
                        display: inline-block;
                        padding: 18px 35px;
                        background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
                        color: white;
                        text-decoration: none;
                        border-radius: 50px;
                        margin: 15px 10px;
                        font-weight: bold;
                        font-size: 1.1em;
                        transition: all 0.3s ease;
                        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
                    }
                    
                    .button:hover {
                        transform: translateY(-3px);
                        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.6);
                        background: linear-gradient(45deg, #ff5252, #ff6b6b);
                    }
                    
                    .feature-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 20px;
                        margin-top: 40px;
                    }
                    
                    .feature {
                        background: rgba(255, 255, 255, 0.1);
                        padding: 20px;
                        border-radius: 15px;
                        backdrop-filter: blur(5px);
                    }
                    
                    .feature h3 {
                        color: #4ecdc4;
                        margin-bottom: 10px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 Welcome to Karbon!</h1>
                    <p>This is a test website to verify that CSS styling is working correctly.</p>
                    <p>You should see beautiful gradients, animations, and modern styling.</p>
                    
                    <a href="#" class="button">Get Started</a>
                    <a href="#" class="button">Learn More</a>
                    
                    <div class="feature-grid">
                        <div class="feature">
                            <h3>🎨 Beautiful Design</h3>
                            <p>Modern gradients and effects</p>
                        </div>
                        <div class="feature">
                            <h3>⚡ Fast Performance</h3>
                            <p>Optimized for speed</p>
                        </div>
                        <div class="feature">
                            <h3>📱 Responsive</h3>
                            <p>Works on all devices</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            if WEBVIEW_AVAILABLE and hasattr(self, 'embedded_browser'):
                # Use simple embedded preview that opens in browser
                if self.embedded_browser.update_content(test_html):
                    self.preview_status.configure(text="● Test Loaded", fg='#3fb950')
                    self.show_success("Test website opened in browser with full CSS support!")
                else:
                    self.show_error("Failed to load test preview")
                    
            elif HTML_AVAILABLE and hasattr(self, 'html_preview'):
                # Use tkhtmlview fallback
                self.html_preview.set_html(test_html)
                self.preview_status.configure(text="● Test Loaded", fg='#3fb950')
                
                # Also open in browser for guaranteed rendering
                temp_file = open_html_in_browser(test_html, "Karbon Test Preview")
                if temp_file:
                    self.show_success("Test website loaded! Check both embedded preview and browser for full rendering.")
                else:
                    self.show_success("Test website loaded! You should see a rendered website.")
            else:
                self.show_error("No preview system available.")
            
        except Exception as e:
            self.show_error(f"Error testing preview: {str(e)}")

    def open_in_browser(self):
        """Open the current code in the default browser for better CSS support"""
        try:
            current_code = self.get_code()
            if current_code:
                # Format the HTML for browser
                formatted_html = self.format_html_for_preview(current_code)
                
                # Open in browser
                temp_file = open_html_in_browser(formatted_html, "Karbon Preview")
                
                if temp_file:
                    self.preview_status.configure(text="● Browser Opened", fg='#3fb950')
                    self.show_success("Preview opened in browser with full CSS support!")
                else:
                    self.show_error("Failed to open preview in browser")
            else:
                self.show_error("No code available to preview")
        except Exception as e:
            self.show_error(f"Error opening in browser: {str(e)}")

    def open_preview_in_browser(self):
        """Open preview in browser (for webview mode)"""
        try:
            current_code = self.get_code()
            if current_code:
                # Format the HTML for browser
                formatted_html = self.format_html_for_preview(current_code)
                
                # Open in browser
                temp_file = open_html_in_browser(formatted_html, "Karbon Preview")
                
                if temp_file:
                    self.preview_status.configure(text="● Browser Opened", fg='#3fb950')
                    self.show_success("Preview opened in browser with full CSS support!")
                else:
                    self.show_error("Failed to open preview in browser")
            else:
                self.show_error("No code available to preview")
        except Exception as e:
            self.show_error(f"Error opening preview in browser: {str(e)}")

    def update_appearance(self, font_family, font_size, theme_colors):
        # Update header labels
        if self.header_title_label:
            self.header_title_label.config(font=(font_family, 20, "bold"), fg=theme_colors["accent"],
                                           bg=theme_colors["bg"])
        if self.header_subtitle_label:
            self.header_subtitle_label.config(font=(font_family, 10), fg=theme_colors["subtitle"],
                                              bg=theme_colors["bg"])

        # Update input text area
        self.update_text.config(
            font=("Consolas", font_size),
            bg=theme_colors["input_bg"],
            fg=theme_colors["input_fg"],
            insertbackground=theme_colors["accent"]
        )

        # Update main content labels (Live Preview section)
        if self.preview_title_label:
            self.preview_title_label.config(bg=theme_colors["input_bg"], fg=theme_colors["label_fg"],
                                            font=(font_family, 14, "bold"))
        if self.preview_desc_label_1:
            self.preview_desc_label_1.config(bg=theme_colors["input_bg"], fg=theme_colors["accent"],
                                             font=(font_family, 14, "bold"))
        if self.preview_desc_label_2:
            self.preview_desc_label_2.config(bg=theme_colors["input_bg"], fg=theme_colors["subtitle"],
                                             font=(font_family, 11))

        # Update tips section labels
        if self.tips_title_label:
            self.tips_title_label.config(bg=theme_colors["bg"], fg=theme_colors["warning"],
                                         font=(font_family, 12, "bold"))
        for label in self.tip_labels:
            label.config(bg=theme_colors["bg"], fg=theme_colors["subtitle"], font=(font_family, 10))

        # Update status bar labels
        if self.status_bar_label:
            self.status_bar_label.config(bg=theme_colors["input_bg"], fg=theme_colors["subtitle"],
                                         font=(font_family, 9))
        if self.activity_indicator_label:
            self.activity_indicator_label.config(bg=theme_colors["input_bg"], fg=theme_colors["accent"],
                                                 font=(font_family, 9))

        # Update various frame backgrounds that are children of EditorView
        self.config(bg=theme_colors["bg"])  # EditorView's own background

        # Manually update specific frame backgrounds if they are instance variables
        # Assuming header_frame, toolbar_container, content_frame, status_frame
        # These are usually created but not stored as self.frames for direct update.
        # If they need background updates, they should be instance variables.
        # For now, applying to direct children (which might be frames).
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.config(bg=theme_colors["bg"])

        # Update the background of the tool_bar (if it's an instance variable)
        # Assuming 'toolbar' in create_toolbar needs its background updated explicitly
        # This would require it to be self.toolbar = tk.Frame(...) in create_toolbar
        # For now, relying on parent config if not explicitly stored.

        # Update the main card backgrounds (input_card, header_frame inside input_card)
        # These are within create_input_section, which is not part of EditorView.
        # This update_appearance function is for EditorView itself.
        # If nested elements need specific backgrounds, they should be stored as instance variables.
        # For this context, only direct children and explicitly stored labels are updated.