import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import webbrowser
import tempfile
import os
from ai_engine import generate_code_from_prompt
from exporter import export_code
from preview import update_preview
import prompt_history


class EditorView(tk.Frame):
    def __init__(self, master, get_code_callback, set_code_callback):
        super().__init__(master, bg='#0d1117')
        self.get_code = get_code_callback
        self.set_code = set_code_callback
        self.is_updating = False
        self.setup_ui()

    def setup_ui(self):
        # Create main layout
        self.create_header()
        self.create_toolbar()
        self.create_main_content()
        self.create_status_bar()

    def create_header(self):
        """Create the editor header with title and stats"""
        header_frame = tk.Frame(self, bg='#0d1117')
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        # Title section
        title_frame = tk.Frame(header_frame, bg='#0d1117')
        title_frame.pack(side="left", fill="y")
        
        tk.Label(
            title_frame,
            text="⚡ Code Editor",
            font=("Segoe UI", 20, "bold"),
            bg='#0d1117',
            fg='#58a6ff'
        ).pack(anchor="w")
        
        tk.Label(
            title_frame,
            text="Edit, update, and export your generated website",
            font=("Segoe UI", 10),
            bg='#0d1117',
            fg='#8b949e'
        ).pack(anchor="w", pady=(2, 0))
        
        # Stats section
        self.stats_frame = tk.Frame(header_frame, bg='#0d1117')
        self.stats_frame.pack(side="right", fill="y")
        
        self.update_stats()

    def create_toolbar(self):
        """Create modern toolbar with enhanced features"""
        toolbar_container = tk.Frame(self, bg='#0d1117')
        toolbar_container.pack(fill="x", padx=20, pady=(0, 15))
        
        # Main toolbar with card design
        toolbar = tk.Frame(toolbar_container, bg='#161b22', relief='solid', bd=1)
        toolbar.pack(fill="x")
        
        # Left section - Update controls
        left_section = tk.Frame(toolbar, bg='#161b22')
        left_section.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        
        tk.Label(
            left_section,
            text="🔄 Update Your Website",
            font=("Segoe UI", 12, "bold"),
            bg='#161b22',
            fg='#f0f6fc'
        ).pack(anchor="w", pady=(0, 8))
        
        # Input container
        input_container = tk.Frame(left_section, bg='#161b22')
        input_container.pack(fill="x", pady=(0, 10))
        
        # Modern text input for updates
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
        
        # Placeholder for update input
        self.update_placeholder = "Describe what you'd like to change...\n\nExample: Make the header purple, add a contact form, or change the font to something more modern"
        self.setup_update_placeholder()
        
        # Button container
        button_container = tk.Frame(left_section, bg='#161b22')
        button_container.pack(fill="x")
        
        # Update button
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

        #Undo button
        self.undo_btn = tk.Button(
            button_container,
            text="⏪ Undo",
            font=("Segoe UI", 11, "bold"),
            bg='#1f6feb',
            # fg='white',
            state="disabled",
            disabledforeground="white",
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

        #Redo button
        self.redo_btn = tk.Button(
            button_container,
            text="Redo ⏩",
            font=("Segoe UI", 11, "bold"),
            bg='#1f6feb',
            # fg='white',
            state="disabled",
            disabledforeground="white",
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
        
        # Clear button
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
        
        # Right section - Action buttons
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
        
        # Action buttons
        actions = [
            ("🌐 Preview", "#6f42c1", self.preview_in_browser),
            ("💾 Export", "#238636", self.handle_export),
            ("📁 Save", "#0969da", self.save_file),
            ("↩️ New Project", "#6e7681", self.back_to_prompt)
        ]
        
        for text, color, command in actions:
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
        """Create the main content area"""
        content_frame = tk.Frame(self, bg='#0d1117')
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Preview info card
        info_card = tk.Frame(content_frame, bg='#161b22', relief='solid', bd=1)
        info_card.pack(fill="both", expand=True)
        
        # Card header
        header = tk.Frame(info_card, bg='#21262d')
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="👁️ Live Preview",
            font=("Segoe UI", 14, "bold"),
            bg='#21262d',
            fg='#f0f6fc',
            padx=20,
            pady=12
        ).pack(side="left")
        
        # Status indicator
        self.preview_status = tk.Label(
            header,
            text="● Live",
            font=("Segoe UI", 10),
            bg='#21262d',
            fg='#3fb950'
        )
        self.preview_status.pack(side="right", padx=20)
        
        # Content area
        content_area = tk.Frame(info_card, bg='#161b22')
        content_area.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Preview illustration
        preview_icon = tk.Label(
            content_area,
            text="🌐",
            font=("Segoe UI", 48),
            bg='#161b22'
        )
        preview_icon.pack(pady=(40, 20))
        
        tk.Label(
            content_area,
            text="Your website preview opens in a separate window",
            font=("Segoe UI", 14, "bold"),
            bg='#161b22',
            fg='#58a6ff'
        ).pack()
        
        tk.Label(
            content_area,
            text="The preview updates automatically when you make changes",
            font=("Segoe UI", 11),
            bg='#161b22',
            fg='#8b949e'
        ).pack(pady=(5, 20))
        
        # Quick preview button
        quick_preview_btn = tk.Button(
            content_area,
            text="🚀 Open Preview Window",
            font=("Segoe UI", 12, "bold"),
            bg='#6f42c1',
            fg='white',
            activebackground='#8a63d2',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=30,
            pady=12,
            cursor='hand2',
            command=self.preview_in_browser
        )
        quick_preview_btn.pack(pady=(0, 40))
        
        # Tips section
        self.create_tips_section(content_area)

    def create_tips_section(self, parent):
        """Create tips section"""
        tips_frame = tk.Frame(parent, bg='#0d1117', relief='solid', bd=1)
        tips_frame.pack(fill="x", pady=(20, 0))
        
        tk.Label(
            tips_frame,
            text="💡 Pro Tips",
            font=("Segoe UI", 12, "bold"),
            bg='#0d1117',
            fg='#f79c42'
        ).pack(anchor="w", padx=15, pady=(12, 8))
        
        tips = [
            "• Be specific about colors, fonts, and layout changes",
            "• Use preview to see changes before exporting",
            "• Save your work frequently to avoid losing progress",
            "• Try different update prompts to fine-tune your design"
        ]
        
        for tip in tips:
            tk.Label(
                tips_frame,
                text=tip,
                font=("Segoe UI", 10),
                bg='#0d1117',
                fg='#8b949e',
                anchor='w'
            ).pack(anchor="w", padx=15, pady=1)
        
        tk.Label(tips_frame, text="", bg='#0d1117').pack(pady=8)

    def create_status_bar(self):
        """Create status bar"""
        self.status_frame = tk.Frame(self, bg='#161b22', height=35)
        self.status_frame.pack(fill="x", side="bottom")
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Ready to edit • Make changes and see them live",
            font=("Segoe UI", 9),
            bg='#161b22',
            fg='#8b949e'
        )
        self.status_label.pack(side="left", padx=20, pady=8)
        
        # Activity indicator
        self.activity_label = tk.Label(
            self.status_frame,
            text="",
            font=("Segoe UI", 9),
            bg='#161b22',
            fg='#58a6ff'
        )
        self.activity_label.pack(side="right", padx=20, pady=8)

    def setup_update_placeholder(self):
        """Setup placeholder for update input"""
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
        """Update the stats display"""
        try:
            code = self.get_code()
            if code:
                lines = len(code.split('\n'))
                chars = len(code)
                
                # Clear existing stats
                for widget in self.stats_frame.winfo_children():
                    widget.destroy()
                
                # Create stats display
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
        """Clear the update input"""
        self.update_text.delete("1.0", "end")
        self.update_text.insert("1.0", self.update_placeholder)
        self.update_text.configure(fg='#6e7681')

    def update_status(self, message, activity=""):
        """Update status bar"""
        self.status_label.configure(text=message)
        self.activity_label.configure(text=activity)

    def handle_update(self):
        """Handle update with enhanced UX"""
        if self.is_updating:
            return
            
        prompt = self.update_text.get("1.0", "end-1c").strip()
        
        if not prompt or prompt == self.update_placeholder:
            self.show_error("Please describe what changes you'd like to make! 🔄")
            return
        else:
            prompt_history.add(prompt)
            self.update_btn.config(state="active")
        
        self.start_update(prompt)

    def handle_undo(self):
        if (prompt_history.undo() == 1):
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
        if (prompt_history.redo() == prompt_history.number_of_prompts-1):
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
        """Start update process with visual feedback"""
        self.is_updating = True
        
        # Update button state
        self.update_btn.configure(
            text="🔄 Updating...",
            state='disabled',
            bg='#6e7681'
        )
        
        # Update status
        self.update_status("Applying your changes...", "🔄")
        self.preview_status.configure(text="● Updating", fg='#f79c42')
        
        # Start update in background
        def update_in_background():
            try:
                code = generate_code_from_prompt(prompt)
                prompt_history.code_of_prompts.append(code)
                self.set_code(code)
                update_preview(code)
                
                # Complete on main thread
                self.after(0, lambda: self.update_complete())
                
            except Exception as e:
                self.after(0, lambda: self.update_error(str(e)))
        
        threading.Thread(target=update_in_background, daemon=True).start()

    def update_complete(self):
        """Handle successful update"""
        self.is_updating = False
        
        # Reset button
        self.update_btn.configure(
            text="🔄 Update Code",
            state='normal',
            bg='#1f6feb'
        )
        
        # Update status
        self.update_status("Changes applied successfully!", "✅")
        self.preview_status.configure(text="● Live", fg='#3fb950')
        
        # Update stats
        self.update_stats()
        
        # Show success notification
        self.show_success("Website updated successfully! 🎉")
        
        # Clear input
        self.clear_update_input()

    def update_error(self, error_msg):
        """Handle update error"""
        self.is_updating = False
        
        # Reset button
        self.update_btn.configure(
            text="🔄 Update Code",
            state='normal',
            bg='#1f6feb'
        )
        
        # Update status
        self.update_status("Update failed", "❌")
        self.preview_status.configure(text="● Error", fg='#f85149')
        
        # Show error
        self.show_error(f"Update failed: {error_msg}")

    def handle_export(self):
        """Enhanced export with options"""
        code = self.get_code()
        if not code:
            self.show_error("No code to export! Generate a website first.")
            return
        
        try:
            export_code(code)
            self.show_success("Code exported successfully! 📁")
            self.update_status("Code exported to file", "💾")
        except Exception as e:
            self.show_error(f"Export failed: {str(e)}")

    def save_file(self):
        """Save code to custom location"""
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

    def preview_in_browser(self):
        """Open preview in browser"""
        # code = self.get_code()
        code = prompt_history.get_current_code()
        if not code:
            self.show_error("No code to preview!")
            return
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            # Open in browser
            webbrowser.open(f'file://{temp_path}')
            self.show_success("Preview opened in browser! 🌐")
            self.update_status("Preview opened in browser", "🌐")
            
        except Exception as e:
            self.show_error(f"Preview failed: {str(e)}")

    def back_to_prompt(self):
        """Go back to prompt view"""
        response = messagebox.askyesno(
            "New Project",
            "Start a new project? This will clear your current work.",
            icon='question'
        )
        
        if response:
            # This would need to be implemented in the main UI class
            self.update_status("Starting new project...", "🔄")

    def lighten_color(self, color):
        """Lighten a hex color"""
        color_map = {
            "#6f42c1": "#8a63d2",
            "#238636": "#2ea043", 
            "#0969da": "#1f6feb",
            "#6e7681": "#8b949e"
        }
        return color_map.get(color, color)

    def show_error(self, message):
        """Show error notification"""
        error_window = tk.Toplevel(self)
        error_window.title("Error")
        error_window.geometry("400x150")
        error_window.configure(bg='#21262d')
        error_window.resizable(False, False)
        error_window.attributes('-topmost', True)
        
        # Center the window
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() // 2) - 200
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() // 2) - 75
        error_window.geometry(f"400x150+{x}+{y}")
        
        tk.Label(
            error_window,
            text="⚠️",
            font=("Segoe UI", 24),
            bg='#21262d',
            fg='#f85149'
        ).pack(pady=(20, 10))
        
        tk.Label(
            error_window,
            text=message,
            font=("Segoe UI", 10),
            bg='#21262d',
            fg='#f0f6fc',
            wraplength=350,
            justify=tk.CENTER
        ).pack(pady=(0, 20))
        
        tk.Button(
            error_window,
            text="OK",
            font=("Segoe UI", 10),
            bg='#238636',
            fg='white',
            relief='flat',
            padx=20,
            pady=5,
            command=error_window.destroy
        ).pack()

    def show_success(self, message):
        """Show success notification"""
        success_window = tk.Toplevel(self)
        success_window.title("Success")
        success_window.geometry("350x120")
        success_window.configure(bg='#21262d')
        success_window.resizable(False, False)
        success_window.attributes('-topmost', True)
        
        # Position in top-right
        x = self.winfo_toplevel().winfo_x() + self.winfo_toplevel().winfo_width() - 370
        y = self.winfo_toplevel().winfo_y() + 50
        success_window.geometry(f"350x120+{x}+{y}")
        
        tk.Label(
            success_window,
            text="🎉",
            font=("Segoe UI", 20),
            bg='#21262d'
        ).pack(pady=(15, 5))
        
        tk.Label(
            success_window,
            text=message,
            font=("Segoe UI", 10),
            bg='#21262d',
            fg='#3fb950'
        ).pack()
        
        # Auto-close after 3 seconds
        success_window.after(3000, success_window.destroy)