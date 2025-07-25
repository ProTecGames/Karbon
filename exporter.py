import os
import zipfile
from datetime import datetime
from tkinter import filedialog

from github import Github
from token_manager import decrypt_token


def validate_github_token(token=None):
    """Validate a GitHub token by attempting to get the user information

    Args:
        token (str, optional): The token to validate. If None, will attempt to decrypt stored token.

    Returns:
        tuple: (is_valid, username, error_message)
    """
    if token is None:
        token = decrypt_token()

    if not token:
        return False, None, "No token provided or stored"

    try:
        g = Github(token)
        user = g.get_user()
        username = user.login
        return True, username, None
    except Exception as e:
        return False, None, str(e)


def export_code(code: str, as_zip: bool = False):
    folder_selected = filedialog.askdirectory(title="Select Export Folder")
    if not folder_selected:
        return

    if as_zip:
        export_name = f"karbon_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(folder_selected, export_name)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("index.html", code)

        print(f"✅ Code exported as zip: {zip_path}")
    else:
        html_path = os.path.join(folder_selected, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"✅ Code exported as HTML: {html_path}")

    return folder_selected


def export_to_github(code: str, repo_name="karbon-export-demo"):
    print("🚀 export_to_github() called")

    # Validate GitHub token
    is_valid, username, error = validate_github_token()
    if not is_valid:
        print(f"❌ GitHub token validation failed: {error}")
        return None

    print(f"✅ Using GitHub token for user: {username}")

    try:
        # Get GitHub instance and user
        token = decrypt_token()
        g = Github(token)
        user = g.get_user()

        # Check if repo exists, create if not
        try:
            print(f"🔍 Looking for existing repository: {repo_name}")
            repo = user.get_repo(repo_name)
            print(f"✅ Found existing repository: {repo.html_url}")
        except Exception as repo_error:
            print(f"ℹ️ Repository not found, creating new one: {repo_name}")
            repo = user.create_repo(repo_name, description="Created with Karbon AI Web Builder")
            print(f"✅ Created new repository: {repo.html_url}")

        # Check if file exists, update or create
        try:
            print("🔍 Checking if index.html exists in repository")
            contents = repo.get_contents("index.html")
            print("✅ Found existing index.html, updating")
            repo.update_file("index.html", "Update index.html via Karbon", code, contents.sha)
            print("✅ Updated index.html in repository")
        except Exception as file_error:
            print("ℹ️ index.html not found, creating new file")
            repo.create_file("index.html", "Initial commit via Karbon", code)
            print("✅ Created index.html in repository")

        print("✅ Code successfully pushed to GitHub.")
        return repo.html_url
    except Exception as e:
        print(f"❌ GitHub export failed: {e}")
        return None

