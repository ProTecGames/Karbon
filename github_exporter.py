import os
from github import Github
from token_manager import decrypt_token
from exporter import validate_github_token

def create_repo(repo_name: str = "karbon-export-demo", description: str = "Created with Karbon AI Web Builder"):
    """Create a GitHub repository or return existing one
    
    Args:
        repo_name (str): Name of the repository to create or get
        description (str): Description for the repository if created
        
    Returns:
        Repository object or None if failed
    """
    # Validate GitHub token first
    is_valid, username, error = validate_github_token()
    if not is_valid:
        print(f"❌ GitHub token validation failed: {error}")
        return None
        
    print(f"✅ Using GitHub token for user: {username}")
    
    try:
        token = decrypt_token()
        g = Github(token)
        user = g.get_user()
        
        try:
            print(f"🔍 Looking for existing repository: {repo_name}")
            repo = user.get_repo(repo_name)
            print(f"✅ Repository {repo_name} already exists at {repo.html_url}")
        except Exception as repo_error:
            print(f"ℹ️ Creating new repository: {repo_name}")
            repo = user.create_repo(repo_name, description=description)
            print(f"✅ Repository {repo_name} created at {repo.html_url}")
            
        return repo
    except Exception as e:
        print(f"❌ Failed to create repository: {e}")
        return None
