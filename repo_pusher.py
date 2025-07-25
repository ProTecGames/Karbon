import os
from git import Repo
from token_manager import decrypt_token
from github import Github
from exporter import validate_github_token

def push_to_github(repo_dir, repo_name):
    """Push code to GitHub repository
    
    Args:
        repo_dir (str): Local directory containing the code
        repo_name (str): Name of the GitHub repository
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Validate GitHub token first
    is_valid, username, error = validate_github_token()
    if not is_valid:
        print(f"❌ GitHub token validation failed: {error}")
        return False
        
    print(f"✅ Using GitHub token for user: {username}")
    token = decrypt_token()

    if not token:
        print("❌ GitHub token not found.")
        return False

    remote_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"

    try:
        print(f"🔍 Checking repository directory: {repo_dir}")
        if not os.path.exists(os.path.join(repo_dir, ".git")):
            print("ℹ️ Initializing new Git repository")
            repo = Repo.init(repo_dir)
            repo.git.add(A=True)
            repo.index.commit("Initial commit from Karbon")
            print(f"ℹ️ Adding remote: {username}/{repo_name}")
            origin = repo.create_remote('origin', remote_url)
        else:
            print("ℹ️ Using existing Git repository")
            repo = Repo(repo_dir)
            repo.git.add(A=True)
            if repo.is_dirty() or len(repo.untracked_files) > 0:
                print("ℹ️ Committing changes")
                repo.index.commit("Update from Karbon")
                origin = repo.remote(name='origin')
            else:
                print("ℹ️ No changes to commit")
                origin = repo.remote(name='origin')

        print("📤 Pushing to GitHub...")
        origin.push(refspec='master:main')
        print(f"✅ Pushed to GitHub: {remote_url}")
        return True

    except Exception as e:
        print(f"❌ Push failed: {e}")
        return False
