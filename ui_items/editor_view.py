import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import webbrowser
import tempfile
import os
from ai_engine import generate_code_from_prompt, ai_status
from exporter import export_code
from preview import update_preview
import prompt_history


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
            text="● Live",
            font=("Segoe UI", 10),
            bg='#21262d',
            fg='#3fb950'
        )
        self.preview_status.pack(side="right", padx=20)

        content_area = tk.Frame(info_card, bg='#161b22')
        content_area.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            content_area,
            text="🌐",
            font=("Segoe UI", 48),
            bg='#161b22'
        ).pack(pady=(40, 20))

        # Stored as instance variable
        self.preview_desc_label_1 = tk.Label(
            content_area,
            text="Your website preview opens in a separate window",
            font=("Segoe UI", 14, "bold"),
            bg='#161b22',
            fg='#58a6ff'
        )
        self.preview_desc_label_1.pack()

        # Stored as instance variable
        self.preview_desc_label_2 = tk.Label(
            content_area,
            text="The preview updates automatically when you make changes",
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
                model_source = self.get_model_source()
                code = generate_code_from_prompt(prompt, api_key, model_source)
                prompt_history.push_code(code)
                prompt_history.push_prompt(
                    "Describe what you'd like to change...\n\nExample: Make the header purple, add a contact form, or change the font to something more modern")
                prompt_history.push_code(code)
                self.set_code(code)
                update_preview(code)

                self.after(0, lambda: self.update_complete())

            except Exception as e:
                self.after(0, lambda exc=e: self.update_error(str(exc)))

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