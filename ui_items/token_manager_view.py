import tkinter as tk
from tkinter import ttk, messagebox
import threading
import webbrowser
import os
from core.token_manager import encrypt_token, decrypt_token, clear_token, token_exists, ERROR_NO_TOKEN, SUCCESS_TOKEN_SAVED
from exporters.exporter import validate_github_token

class TokenManagerView(ttk.Frame):
    def __init__(self, parent, back_callback):
        super().__init__(parent)
        self.back_callback = back_callback
        
        # Set background color using style
        self.style = ttk.Style()
        self.style.configure('TokenManager.TFrame', background='#0d1117')
        self.configure(style='TokenManager.TFrame')
        
        # Setup styles to match Karbon's theme
        self.setup_styles()
        
        # Create main container
        self.container = tk.Frame(self, bg='#0d1117')
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create header with back button
        self.header_frame = tk.Frame(self.container, bg='#0d1117')
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        self.back_button = ttk.Button(
            self.header_frame,
            text="Back",
            command=self.back_callback,
            style="Modern.TButton"
        )
        self.back_button.pack(side="left")
        
        self.title_label = tk.Label(
            self.header_frame,
            text="GitHub Token Manager",
            font=("Segoe UI", 16, "bold"),
            bg='#0d1117',
            fg='#58a6ff'
        )
        self.title_label.pack(side="left", padx=(10, 0))
        
        # Create token input frame
        self.token_frame = tk.Frame(self.container, bg='#161b22', padx=20, pady=20)
        self.token_frame.pack(fill="x", pady=10)
        
        # Token description
        self.description_label = tk.Label(
            self.token_frame,
            text="Enter your GitHub Personal Access Token (PAT) below. This token will be encrypted and stored locally on your machine.",
            font=("Segoe UI", 10),
            bg='#161b22',
            fg='#8b949e',
            wraplength=500,
            justify="left"
        )
        self.description_label.pack(fill="x", pady=(0, 10), anchor="w")
        
        # Token help link
        self.help_label = tk.Label(
            self.token_frame,
            text="How to create a GitHub token",
            font=("Segoe UI", 10, "underline"),
            bg='#161b22',
            fg='#58a6ff',
            cursor="hand2"
        )
        self.help_label.pack(fill="x", pady=(0, 20), anchor="w")
        self.help_label.bind("<Button-1>", self.open_token_help)
        
        # Token input
        self.token_input_frame = tk.Frame(self.token_frame, bg='#161b22')
        self.token_input_frame.pack(fill="x")
        
        self.token_label = tk.Label(
            self.token_input_frame,
            text="GitHub Token:",
            font=("Segoe UI", 10),
            bg='#161b22',
            fg='#f0f6fc'
        )
        self.token_label.pack(side="left")
        
        self.token_var = tk.StringVar()
        self.token_entry = ttk.Entry(
            self.token_input_frame,
            textvariable=self.token_var,
            width=40,
            show="•",
            style="Modern.TEntry"
        )
        self.token_entry.pack(side="left", padx=(10, 0))
        
        # Show/hide token button
        self.show_token_var = tk.BooleanVar(value=False)
        self.show_token_button = ttk.Checkbutton(
            self.token_input_frame,
            text="Show",
            variable=self.show_token_var,
            command=self.toggle_token_visibility,
            style="Modern.TCheckbutton"
        )
        self.show_token_button.pack(side="left", padx=(10, 0))
        
        # Token status
        self.status_frame = tk.Frame(self.token_frame, bg='#161b22')
        self.status_frame.pack(fill="x", pady=(20, 0))
        
        self.status_label = tk.Label(
            self.status_frame,
            text="",
            font=("Segoe UI", 10),
            bg='#161b22',
            fg='#8b949e'
        )
        self.status_label.pack(side="left")
        
        # Action buttons
        self.button_frame = tk.Frame(self.token_frame, bg='#161b22')
        self.button_frame.pack(fill="x", pady=(20, 0))
        
        self.save_button = ttk.Button(
            self.button_frame,
            text="Save Token",
            command=self.save_token,
            style="Modern.TButton"
        )
        self.save_button.pack(side="left")
        
        self.test_button = ttk.Button(
            self.button_frame,
            text="Test Connection",
            command=self.test_connection,
            style="Modern.TButton"
        )
        self.test_button.pack(side="left", padx=(10, 0))
        
        self.clear_button = ttk.Button(
            self.button_frame,
            text="Clear Token",
            command=self.clear_token,
            style="Warning.TButton"
        )
        self.clear_button.pack(side="right")
        
        # Security note
        self.security_frame = tk.Frame(self.container, bg='#0d1117', pady=20)
        self.security_frame.pack(fill="x")
        
        self.security_label = tk.Label(
            self.security_frame,
            text="🔒 Security Note: Your token is encrypted and stored locally. It is never transmitted to our servers.",
            font=("Segoe UI", 10, "italic"),
            bg='#0d1117',
            fg='#8b949e',
            wraplength=500,
            justify="left"
        )
        self.security_label.pack(fill="x")
        
        # Check if token exists and update UI
        self.check_token_status()
    
    def setup_styles(self):
        """Configure styles to match Karbon's theme"""
        style = ttk.Style()
        
        # Configure modern button style
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
        
        # Configure warning button style
        style.configure(
            "Warning.TButton",
            background='#da3633',
            foreground='#0d1117',
            borderwidth=0,
            focuscolor='none',
            relief='flat',
            padding=(10, 5),
            font=("Segoe UI", 10)
        )
        style.map(
            "Warning.TButton",
            background=[('active', '#f85149'), ('pressed', '#a40e26')],
            foreground=[('active', '#0d1117'), ('pressed', '#0d1117')]
        )
        
        # Configure modern entry style
        style.configure(
            "Modern.TEntry",
            fieldbackground='#21262d',
            foreground='#f0f6fc',
            borderwidth=1,
            relief='solid',
            insertcolor='white'
        )
        
        # Configure modern checkbutton style
        style.configure(
            "Modern.TCheckbutton",
            background='#161b22',
            foreground='#f0f6fc',
            indicatorcolor='#21262d',
            indicatorrelief='flat',
            font=("Segoe UI", 10)
        )
        style.map(
            "Modern.TCheckbutton",
            background=[('active', '#161b22')],
            foreground=[('active', '#f0f6fc')]
        )
    
    def check_token_status(self):
        """Check if a token exists and update the UI accordingly"""
        if token_exists():
            self.status_label.config(
                text="✅ Token is set and encrypted",
                fg='#3fb950'
            )
            # Mask the token in the entry field
            self.token_var.set("•" * 20)
            
            # Test the connection automatically
            self.test_connection()
        else:
            self.status_label.config(
                text="❌ No token set",
                fg='#f85149'
            )
            self.token_var.set("")
    
    def toggle_token_visibility(self):
        """Toggle between showing and hiding the token"""
        if self.show_token_var.get():
            # Show the actual token if it exists
            token = decrypt_token()
            if token:
                self.token_entry.config(show="")
                self.token_var.set(token)
        else:
            # Hide the token again
            self.token_entry.config(show="•")
            token = decrypt_token()
            if token:
                self.token_var.set("•" * 20)
    
    def save_token(self):
        """Encrypt and save the token"""
        token = self.token_var.get()
        if not token or token == "•" * 20:
            self.status_label.config(
                text="❌ Please enter a valid token",
                fg='#f85149'
            )
            return
        
        try:
            encrypt_token(token)
            self.status_label.config(
                text="✅ Token saved and encrypted successfully",
                fg='#3fb950'
            )
            # Reset the entry field to masked
            self.token_entry.config(show="•")
            self.token_var.set("•" * 20)
            self.show_token_var.set(False)
        except Exception as e:
            self.status_label.config(
                text=f"❌ Error saving token: {str(e)}",
                fg='#f85149'
            )
    
    def test_connection(self):
        """Test the GitHub connection with the current token"""
        self.status_label.config(
            text="🔄 Testing connection...",
            fg='#58a6ff'
        )
        
        # Run the test in a separate thread to avoid freezing the UI
        threading.Thread(target=self._test_connection_thread, daemon=True).start()
    
    def _test_connection_thread(self):
        """Thread function to test GitHub connection"""
        # Use the validate_github_token function from exporters/exporter.py
        is_valid, username, error = validate_github_token()
        
        if not is_valid:
            # Update UI in the main thread
            self.after(0, lambda: self.status_label.config(
                text=f"❌ Connection failed: {error}",
                fg='#f85149'
            ))
            return
        
        # Update UI in the main thread
        self.after(0, lambda: self.status_label.config(
            text=f"✅ Connected as {username}",
            fg='#3fb950'
        ))
    
    def clear_token(self):
        """Clear the stored token"""
        # Ask for confirmation
        result = messagebox.askyesno(
            "Confirm", 
            "Are you sure you want to delete your GitHub token?",
            icon="warning"
        )
        
        if not result:
            return
        
        # Use the clear_token function from core/token_manager.py
        success = clear_token()
        
        if success:
            self.status_label.config(
                text="✅ Token cleared successfully",
                fg='#3fb950'
            )
            self.token_var.set("")
        else:
            self.status_label.config(
                text="❌ Error clearing token",
                fg='#f85149'
            )
    
    def open_token_help(self, event):
        """Open GitHub token creation help page"""
        import webbrowser
        webbrowser.open("https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token")