import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import webbrowser
import tempfile
import os
from core.ai_engine import generate_code_from_prompt, ai_status
from exporters.exporter import export_code
from core import prompt_history
try:
    from tkhtmlview import HTMLLabel
    HTML_AVAILABLE = True
except ImportError:
    HTML_AVAILABLE = False

try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False

from utils import preview as preview_utils

def open_html_in_browser(html_content, title="Preview"):
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file = f.name
        webbrowser.open(f'file://{temp_file}')
        return temp_file
    except Exception as e:
        print(f"Error opening HTML in browser: {e}")
        return None

class SimpleEmbeddedPreview:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.current_html = ""
        
    def update_content(self, html_content):
        try:
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

        self.device_var = tk.StringVar(value="Desktop")  # Default device

        self.header_title_label = None
        self.header_subtitle_label = None
        self.preview_title_label = None
        self.preview_desc_label_1 = None
        self.preview_desc_label_2 = None
        self.tips_title_label = None
        self.tip_labels = []
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

        self.header_title_label = tk.Label(
            header_frame,
            text="⚡ Code Editor",
            font=("Segoe UI", 20, "bold"),
            bg='#0d1117',
            fg='#58a6ff'
        )
        self.header_title_label.pack(anchor="w")

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

    def update_stats(self):
        """Update statistics display in header"""
        # This method can be implemented to show relevant stats
        pass

    def setup_update_placeholder(self):
        """Setup placeholder text for update input"""
        if self.update_placeholder:
            self.update_text.insert("1.0", self.update_placeholder)
            self.update_text.config(fg='#8b949e')  # Gray color for placeholder
        else:
            self.update_text.config(fg='#f0f6fc')  # Normal color

    def update_appearance(self, font_family, font_size, theme_colors):
        """Update the appearance of the editor view"""
        # Example implementation: update font and colors
        self.update_text.config(font=(font_family, font_size), bg=theme_colors.get('background', '#0d1117'), fg=theme_colors.get('foreground', '#f0f6fc'))
        # Update other UI elements as needed

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

        # Device selector dropdown for preview size
        device_options = ["Mobile", "Tablet", "Desktop"]
        device_selector = ttk.OptionMenu(
            header,
            self.device_var,
            self.device_var.get(),
            *device_options,
            command=self.on_device_change
        )
        device_selector.pack(side="right", padx=10, pady=10)

        content_area = tk.Frame(info_card, bg='#161b22')
        content_area.pack(fill="both", expand=True, padx=20, pady=20)

        if WEBVIEW_AVAILABLE:
            self.embedded_browser = SimpleEmbeddedPreview(content_area)
            self.html_preview = None

            self.preview_info_frame = tk.Frame(content_area, bg='white')
            self.preview_info_frame.pack(fill="both", expand=True, pady=(0, 20))

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

            def on_enter(e):
                preview_btn.configure(bg='#2ea043')

            def on_leave(e):
                preview_btn.configure(bg='#238636')

            preview_btn.bind("<Enter>", on_enter)
            preview_btn.bind("<Leave>", on_leave)

        elif HTML_AVAILABLE:
            HTMLLabel._default_style = ""

            self.html_preview = HTMLLabel(
                content_area,
                html="<div style='text-align: center; padding: 50px; color: #8b949e; font-family: Arial, sans-serif; background: white;'><h2>🌐 Live Website Preview</h2><p>Your generated website will render here</p><p style='font-size: 12px; color: #666;'>The actual website will appear, not the HTML code</p></div>",
                background='white',
                width=600,
                height=400
            )
            self.html_preview.pack(fill="both", expand=True, pady=(0, 20))

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

            def on_enter(e):
                preview_button.configure(bg='#2ea043')

            def on_leave(e):
                preview_button.configure(bg='#238636')

            preview_button.bind("<Enter>", on_enter)
            preview_button.bind("<Leave>", on_leave)

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
            tk.Label(
                content_area,
                text="🌐",
                font=("Segoe UI", 48),
                bg='#161b22'
            ).pack(pady=(40, 20))

            self.preview_desc_label_1 = tk.Label(
                content_area,
                text="HTML Preview not available",
                font=("Segoe UI", 14, "bold"),
                bg='#161b22',
                fg='#58a6ff'
            )
            self.preview_desc_label_1.pack()

            self.preview_desc_label_2 = tk.Label(
                content_area,
                text="Install tkhtmlview to enable embedded preview",
                font=("Segoe UI", 11),
                bg='#161b22',
                fg='#8b949e'
            )
            self.preview_desc_label_2.pack(pady=(5, 20))

        self.create_tips_section(content_area)

    def on_device_change(self, selected_device):
        """Handle device selection change for preview resizing"""
        preview_utils.set_device_size(selected_device)
        self.refresh_preview()

    def create_tips_section(self, parent):
        tips_frame = tk.Frame(parent, bg='#0d1117', relief='solid', bd=1)
        tips_frame.pack(fill="x", pady=(20, 0))

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

        self.status_bar_label = tk.Label(
            self.status_frame,
            text="Ready to edit • Make changes and see them live",
            font=("Segoe UI", 9),
            bg='#161b22',
            fg='#8b949e'
        )
        self.status_bar_label.pack(side="left", padx=20, pady=8)

        self.activity_indicator_label = tk.Label(
            self.status_frame,
            text="",
            font=("Segoe UI", 9),
            bg='#161b22',
            fg='#58a6ff'
        )
        self.activity_indicator_label.pack(side="right", padx=20, pady=8)

    # The rest of the methods remain unchanged, including refresh_preview, handle_update, etc.

    def refresh_preview(self):
        try:
            current_code = self.get_code()
            if current_code:
                # Inject CSS max-width based on device selection for responsive preview
                device_size = preview_utils.get_device_size()
                max_width_css = device_size.get("css_max_width", "1200px")
                # Wrap the code in a container div with max-width style
                wrapped_code = f"""
                <html>
                <head>
                <style>
                body {{
                    margin: 0;
                    padding: 10px;
                    display: flex;
                    justify-content: center;
                    background: #fff;
                }}
                #preview-container {{
                    max-width: {max_width_css};
                    width: 100%;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    border: 1px solid #ddd;
                }}
                </style>
                </head>
                <body>
                <div id="preview-container">
                {current_code}
                </div>
                </body>
                </html>
                """
                if WEBVIEW_AVAILABLE and hasattr(self, 'embedded_browser'):
                    if self.embedded_browser.update_content(wrapped_code):
                        self.preview_status.configure(text="● Refreshed", fg='#3fb950')
                        self.show_success("Preview opened in browser with full CSS support!")
                    else:
                        self.show_error("Failed to open preview in browser")
                elif HTML_AVAILABLE and hasattr(self, 'html_preview'):
                    simple_html = self.create_simple_html_preview(wrapped_code)
                    self.html_preview.set_html(simple_html)
                    self.preview_status.configure(text="● Refreshed", fg='#3fb950')
                    temp_file = open_html_in_browser(wrapped_code, "Karbon Preview")
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

    # Placeholder methods for missing functionality
    def handle_update(self):
        """Handle update button click"""
        pass

    def handle_undo(self):
        """Handle undo button click"""
        pass

    def handle_redo(self):
        """Handle redo button click"""
        pass

    def clear_update_input(self):
        """Clear the update input text"""
        pass

    def handle_export(self):
        """Handle export button click"""
        pass

    def save_file(self):
        """Handle save file button click"""
        pass

    def back_to_prompt(self):
        """Handle back to prompt button click"""
        pass

    def open_preview_in_browser(self):
        """Open preview in browser"""
        pass

    def test_preview(self):
        """Test preview functionality"""
        pass

    def open_in_browser(self):
        """Open in browser"""
        pass

    def create_simple_html_preview(self, html_content):
        """Create simple HTML preview"""
        return html_content

    def show_success(self, message):
        """Show success message"""
        print(f"Success: {message}")

    def show_error(self, message):
        """Show error message"""
        print(f"Error: {message}")

    def lighten_color(self, color):
        """Lighten a color for hover effects"""
        return color
