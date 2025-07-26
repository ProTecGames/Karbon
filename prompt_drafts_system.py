"""
Complete Prompt Drafts System for Karbon
A standalone implementation that provides save, load, delete, and rename functionality for prompt drafts.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# ===== BACKEND MANAGER =====

class PromptDraftsManager:
    """Backend manager for handling prompt drafts operations"""
    
    def __init__(self, drafts_file="prompt_drafts.json"):
        self.drafts_file = drafts_file
        self.drafts = self.load_drafts()
    
    def load_drafts(self) -> Dict:
        """Load drafts from JSON file"""
        if os.path.exists(self.drafts_file):
            try:
                with open(self.drafts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading drafts: {e}")
                return {}
        return {}
    
    def save_drafts(self):
        """Save drafts to JSON file"""
        try:
            with open(self.drafts_file, 'w', encoding='utf-8') as f:
                json.dump(self.drafts, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving drafts: {e}")
    
    def save_draft(self, name: str, prompt: str) -> bool:
        """Save a new draft or update existing one"""
        if not name.strip() or not prompt.strip():
            return False
        
        self.drafts[name] = {
            'prompt': prompt,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        self.save_drafts()
        return True
    
    def get_draft(self, name: str) -> Optional[str]:
        """Get a draft by name"""
        if name in self.drafts:
            return self.drafts[name]['prompt']
        return None
    
    def get_all_drafts(self) -> List[Dict]:
        """Get all drafts with metadata"""
        drafts_list = []
        for name, data in self.drafts.items():
            drafts_list.append({
                'name': name,
                'prompt': data['prompt'],
                'created_at': data.get('created_at', ''),
                'updated_at': data.get('updated_at', ''),
                'preview': data['prompt'][:50] + '...' if len(data['prompt']) > 50 else data['prompt']
            })
        
        # Sort by updated_at (most recent first)
        drafts_list.sort(key=lambda x: x['updated_at'], reverse=True)
        return drafts_list
    
    def delete_draft(self, name: str) -> bool:
        """Delete a draft"""
        if name in self.drafts:
            del self.drafts[name]
            self.save_drafts()
            return True
        return False
    
    def rename_draft(self, old_name: str, new_name: str) -> bool:
        """Rename a draft"""
        if old_name in self.drafts and new_name.strip() and new_name not in self.drafts:
            draft_data = self.drafts[old_name]
            draft_data['updated_at'] = datetime.now().isoformat()
            self.drafts[new_name] = draft_data
            del self.drafts[old_name]
            self.save_drafts()
            return True
        return False
    
    def draft_exists(self, name: str) -> bool:
        """Check if a draft exists"""
        return name in self.drafts

# ===== UI COMPONENTS =====

class DraftsManagerUI(tk.Toplevel):
    """Main UI window for managing prompt drafts"""
    
    def __init__(self, parent, get_current_prompt_callback=None, load_draft_callback=None):
        super().__init__(parent)
        self.get_current_prompt = get_current_prompt_callback
        self.load_draft = load_draft_callback
        self.drafts_manager = PromptDraftsManager()
        
        self.setup_window()
        self.setup_ui()
        self.refresh_drafts()
    
    def setup_window(self):
        """Configure the main window"""
        self.title("Prompt Drafts Manager")
        self.geometry("600x500")
        self.configure(bg='#161b22')
        self.resizable(True, True)
        
        # Center the window
        self.transient(self.master)
        self.grab_set()
        
        # Position relative to parent
        x = self.master.winfo_x() + 50
        y = self.master.winfo_y() + 50
        self.geometry(f"600x500+{x}+{y}")
    
    def setup_ui(self):
        """Setup the main UI components"""
        # Header
        header_frame = tk.Frame(self, bg='#21262d', height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="📝 Prompt Drafts Manager",
            font=("Segoe UI", 16, "bold"),
            bg='#21262d',
            fg='#f0f6fc'
        ).pack(side="left", padx=20, pady=15)
        
        # Close button
        close_btn = tk.Button(
            header_frame,
            text="✕",
            font=("Segoe UI", 14, "bold"),
            bg='#21262d',
            fg='#8b949e',
            activebackground='#30363d',
            activeforeground='#f0f6fc',
            relief='flat',
            bd=0,
            padx=15,
            pady=10,
            cursor='hand2',
            command=self.destroy
        )
        close_btn.pack(side="right", padx=20, pady=10)
        
        # Action buttons frame
        actions_frame = tk.Frame(self, bg='#161b22')
        actions_frame.pack(fill="x", padx=20, pady=15)
        
        # Save current prompt button
        save_btn = tk.Button(
            actions_frame,
            text="💾 Save Current Prompt",
            font=("Segoe UI", 11, "bold"),
            bg='#238636',
            fg='white',
            activebackground='#2ea043',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.save_current_prompt
        )
        save_btn.pack(side="left", padx=(0, 10))
        
        # Refresh button
        refresh_btn = tk.Button(
            actions_frame,
            text="🔄 Refresh",
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
            command=self.refresh_drafts
        )
        refresh_btn.pack(side="left")
        
        # Drafts count label
        self.count_label = tk.Label(
            actions_frame,
            text="",
            font=("Segoe UI", 10),
            bg='#161b22',
            fg='#8b949e'
        )
        self.count_label.pack(side="right")
        
        # Main content area
        content_frame = tk.Frame(self, bg='#161b22')
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Scrollable drafts list
        self.setup_scrollable_list(content_frame)
    
    def setup_scrollable_list(self, parent):
        """Setup scrollable list for drafts"""
        # Create canvas and scrollbar
        canvas = tk.Canvas(parent, bg='#161b22', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='#161b22')
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        self.canvas = canvas
    
    def refresh_drafts(self):
        """Refresh the drafts list"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        drafts = self.drafts_manager.get_all_drafts()
        
        # Update count
        self.count_label.config(text=f"{len(drafts)} drafts")
        
        if not drafts:
            self.show_empty_state()
            return
        
        # Create draft cards
        for draft in drafts:
            self.create_draft_card(draft)
    
    def show_empty_state(self):
        """Show empty state when no drafts exist"""
        empty_frame = tk.Frame(self.scrollable_frame, bg='#161b22')
        empty_frame.pack(fill="both", expand=True, pady=50)
        
        tk.Label(
            empty_frame,
            text="📝",
            font=("Segoe UI", 48),
            bg='#161b22',
            fg='#30363d'
        ).pack()
        
        tk.Label(
            empty_frame,
            text="No drafts saved yet",
            font=("Segoe UI", 16, "bold"),
            bg='#161b22',
            fg='#8b949e'
        ).pack(pady=(10, 5))
        
        tk.Label(
            empty_frame,
            text="Save your current prompt to get started!",
            font=("Segoe UI", 12),
            bg='#161b22',
            fg='#6e7681'
        ).pack()
    
    def create_draft_card(self, draft):
        """Create a card for a single draft"""
        # Main card frame
        card = tk.Frame(self.scrollable_frame, bg='#0d1117', relief='solid', bd=1)
        card.pack(fill="x", pady=5, padx=5)
        
        # Header with name and actions
        header = tk.Frame(card, bg='#0d1117')
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        # Draft name
        name_label = tk.Label(
            header,
            text=draft['name'],
            font=("Segoe UI", 14, "bold"),
            bg='#0d1117',
            fg='#58a6ff',
            anchor='w'
        )
        name_label.pack(side="left", fill="x", expand=True)
        
        # Action buttons frame
        actions = tk.Frame(header, bg='#0d1117')
        actions.pack(side="right")
        
        # Load button
        load_btn = tk.Button(
            actions,
            text="📂 Load",
            font=("Segoe UI", 9),
            bg='#238636',
            fg='white',
            activebackground='#2ea043',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=12,
            pady=6,
            cursor='hand2',
            command=lambda: self.load_draft_action(draft['name'])
        )
        load_btn.pack(side="left", padx=2)
        
        # Rename button
        rename_btn = tk.Button(
            actions,
            text="✏️ Rename",
            font=("Segoe UI", 9),
            bg='#6f42c1',
            fg='white',
            activebackground='#8a63d2',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=12,
            pady=6,
            cursor='hand2',
            command=lambda: self.rename_draft_action(draft['name'])
        )
        rename_btn.pack(side="left", padx=2)
        
        # Delete button
        delete_btn = tk.Button(
            actions,
            text="🗑️ Delete",
            font=("Segoe UI", 9),
            bg='#da3633',
            fg='white',
            activebackground='#f85149',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=12,
            pady=6,
            cursor='hand2',
            command=lambda: self.delete_draft_action(draft['name'])
        )
        delete_btn.pack(side="left", padx=2)
        
        # Preview text
        preview_label = tk.Label(
            card,
            text=draft['preview'],
            font=("Segoe UI", 10),
            bg='#0d1117',
            fg='#8b949e',
            anchor='w',
            justify='left',
            wraplength=500
        )
        preview_label.pack(fill="x", padx=15, pady=(0, 10))
        
        # Metadata
        metadata_text = f"Created: {self.format_date(draft['created_at'])} | Updated: {self.format_date(draft['updated_at'])}"
        metadata_label = tk.Label(
            card,
            text=metadata_text,
            font=("Segoe UI", 8),
            bg='#0d1117',
            fg='#6e7681',
            anchor='w'
        )
        metadata_label.pack(fill="x", padx=15, pady=(0, 15))
        
        # Hover effects
        def on_enter(e):
            card.configure(bg='#21262d')
            header.configure(bg='#21262d')
            name_label.configure(bg='#21262d')
            actions.configure(bg='#21262d')
            preview_label.configure(bg='#21262d')
            metadata_label.configure(bg='#21262d')
        
        def on_leave(e):
            card.configure(bg='#0d1117')
            header.configure(bg='#0d1117')
            name_label.configure(bg='#0d1117')
            actions.configure(bg='#0d1117')
            preview_label.configure(bg='#0d1117')
            metadata_label.configure(bg='#0d1117')
        
        # Bind hover events
        for widget in [card, header, name_label, actions, preview_label, metadata_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
    
    def format_date(self, date_str):
        """Format ISO date string to readable format"""
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return "Unknown"
    
    def save_current_prompt(self):
        """Save the current prompt as a draft"""
        if not self.get_current_prompt:
            messagebox.showerror("Error", "No prompt input available")
            return
        
        current_prompt = self.get_current_prompt()
        if not current_prompt or current_prompt.strip() == "":
            messagebox.showwarning("Warning", "Please enter a prompt before saving")
            return
        
        # Ask for draft name
        name = simpledialog.askstring(
            "Save Draft",
            "Enter a name for this draft:",
            initialvalue="My Draft"
        )
        
        if name:
            name = name.strip()
            if self.drafts_manager.draft_exists(name):
                if messagebox.askyesno("Draft Exists", f"A draft named '{name}' already exists. Overwrite it?"):
                    self.drafts_manager.save_draft(name, current_prompt)
                    self.refresh_drafts()
                    messagebox.showinfo("Success", f"Draft '{name}' saved successfully!")
            else:
                self.drafts_manager.save_draft(name, current_prompt)
                self.refresh_drafts()
                messagebox.showinfo("Success", f"Draft '{name}' saved successfully!")
    
    def load_draft_action(self, name):
        """Load a draft into the prompt input"""
        prompt = self.drafts_manager.get_draft(name)
        if prompt and self.load_draft:
            self.load_draft(prompt)
            messagebox.showinfo("Success", f"Draft '{name}' loaded successfully!")
            self.destroy()  # Close the drafts manager
    
    def rename_draft_action(self, old_name):
        """Rename a draft"""
        new_name = simpledialog.askstring(
            "Rename Draft",
            f"Enter new name for '{old_name}':",
            initialvalue=old_name
        )
        
        if new_name and new_name.strip():
            new_name = new_name.strip()
            if new_name == old_name:
                return
            
            if self.drafts_manager.draft_exists(new_name):
                messagebox.showerror("Error", f"A draft named '{new_name}' already exists")
                return
            
            if self.drafts_manager.rename_draft(old_name, new_name):
                self.refresh_drafts()
                messagebox.showinfo("Success", f"Draft renamed to '{new_name}'")
            else:
                messagebox.showerror("Error", "Failed to rename draft")
    
    def delete_draft_action(self, name):
        """Delete a draft"""
        if messagebox.askyesno("Delete Draft", f"Are you sure you want to delete '{name}'?"):
            if self.drafts_manager.delete_draft(name):
                self.refresh_drafts()
                messagebox.showinfo("Success", f"Draft '{name}' deleted")
            else:
                messagebox.showerror("Error", "Failed to delete draft")

# ===== INTEGRATION HELPER =====

class PromptDraftsButton:
    """Helper class to add drafts button to existing prompt input"""
    
    def __init__(self, parent_frame, get_prompt_callback, set_prompt_callback):
        self.parent_frame = parent_frame
        self.get_prompt = get_prompt_callback
        self.set_prompt = set_prompt_callback
        self.drafts_window = None
        
        self.create_button()
    
    def create_button(self):
        """Create the drafts button"""
        self.drafts_btn = tk.Button(
            self.parent_frame,
            text="📝 Drafts",
            font=("Segoe UI", 11),
            bg='#0969da',
            fg='white',
            activebackground='#1f6feb',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.open_drafts_manager
        )
        return self.drafts_btn
    
    def open_drafts_manager(self):
        """Open the drafts manager window"""
        if self.drafts_window and self.drafts_window.winfo_exists():
            self.drafts_window.lift()
            return
        
        # Get the root window
        root = self.parent_frame.winfo_toplevel()
        
        self.drafts_window = DraftsManagerUI(
            root,
            get_current_prompt_callback=self.get_prompt,
            load_draft_callback=self.set_prompt
        )

# ===== DEMO APPLICATION =====

def create_demo_app():
    """Create a demo application to test the drafts system"""
    root = tk.Tk()
    root.title("Prompt Drafts System Demo")
    root.geometry("800x600")
    root.configure(bg='#0d1117')
    
    # Main frame
    main_frame = tk.Frame(root, bg='#0d1117')
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    tk.Label(
        main_frame,
        text="Prompt Drafts System Demo",
        font=("Segoe UI", 20, "bold"),
        bg='#0d1117',
        fg='#58a6ff'
    ).pack(pady=(0, 20))
    
    # Prompt input area
    tk.Label(
        main_frame,
        text="Enter your prompt:",
        font=("Segoe UI", 12),
        bg='#0d1117',
        fg='#f0f6fc'
    ).pack(anchor="w", pady=(0, 5))
    
    prompt_text = tk.Text(
        main_frame,
        height=8,
        font=("Consolas", 11),
        bg='#161b22',
        fg='#f0f6fc',
        insertbackground='#58a6ff',
        selectbackground='#264f78',
        relief='solid',
        bd=1,
        padx=15,
        pady=15,
        wrap=tk.WORD
    )
    prompt_text.pack(fill="both", expand=True, pady=(0, 15))
    
    # Buttons frame
    buttons_frame = tk.Frame(main_frame, bg='#0d1117')
    buttons_frame.pack(fill="x")
    
    # Helper functions for demo
    def get_current_prompt():
        return prompt_text.get("1.0", "end-1c").strip()
    
    def set_prompt(text):
        prompt_text.delete("1.0", "end")
        prompt_text.insert("1.0", text)
    
    # Create drafts button using helper class
    drafts_helper = PromptDraftsButton(buttons_frame, get_current_prompt, set_prompt)
    drafts_helper.drafts_btn.pack(side="left")
    
    # Generate button (demo)
    generate_btn = tk.Button(
        buttons_frame,
        text="🚀 Generate",
        font=("Segoe UI", 11, "bold"),
        bg='#238636',
        fg='white',
        activebackground='#2ea043',
        activeforeground='white',
        relief='flat',
        bd=0,
        padx=20,
        pady=10,
        cursor='hand2',
        command=lambda: messagebox.showinfo("Demo", "This is just a demo. In real app, this would generate code.")
    )
    generate_btn.pack(side="right")
    
    # Clear button (demo)
    clear_btn = tk.Button(
        buttons_frame,
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
        command=lambda: prompt_text.delete("1.0", "end")
    )
    clear_btn.pack(side="right", padx=(0, 10))
    
    return root

# ===== MAIN EXECUTION =====

if __name__ == "__main__":
    # Run demo application
    demo_app = create_demo_app()
    demo_app.mainloop()