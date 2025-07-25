import os
from cryptography.fernet import Fernet

# Constants for file paths
KEY_FILE = "secret.key"
TOKEN_FILE = "token.enc"

# Constants for error messages
ERROR_NO_TOKEN = "No GitHub token found"
ERROR_INVALID_TOKEN = "Invalid GitHub token"
ERROR_ENCRYPTION = "Error encrypting token"
ERROR_DECRYPTION = "Error decrypting token"

# Constants for success messages
SUCCESS_TOKEN_SAVED = "GitHub token saved successfully"
SUCCESS_TOKEN_DELETED = "GitHub token deleted successfully"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    print("✅ Generated new encryption key")
    return key

def load_key():
    if not os.path.exists(KEY_FILE):
        print("ℹ️ No encryption key found, generating new one")
        return generate_key()
    return open(KEY_FILE, "rb").read()
    
def token_exists():
    """Check if a token file exists
    
    Returns:
        bool: True if token file exists, False otherwise
    """
    return os.path.exists(TOKEN_FILE)

def encrypt_token(token: str):
    """Encrypt the token using the key
    
    Args:
        token (str): GitHub Personal Access Token to encrypt
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not token or not isinstance(token, str) or token.strip() == "":
        print("❌ Invalid token provided")
        return False
        
    try:
        key = load_key()
        encoded_token = token.encode()
        f = Fernet(key)
        encrypted_token = f.encrypt(encoded_token)

        with open(TOKEN_FILE, "wb") as token_file:
            token_file.write(encrypted_token)
            
        print("✅ Token encrypted and saved successfully")
        return True
    except Exception as e:
        print(f"❌ Error encrypting token: {e}")
        return False

def decrypt_token():
    """Decrypt the token using the key
    
    Returns:
        str or None: Decrypted token if successful, None otherwise
    """
    try:
        if not token_exists():
            print("ℹ️ No token file found")
            return None

        key = load_key()
        with open(TOKEN_FILE, "rb") as token_file:
            encrypted_token = token_file.read()

        f = Fernet(key)
        decrypted_token = f.decrypt(encrypted_token)
        return decrypted_token.decode()
    except Exception as e:
        print(f"❌ Error decrypting token: {e}")
        return None
        
def clear_token():
    """Delete the stored token file
    
    Returns:
        bool: True if successful or if file didn't exist, False on error
    """
    try:
        if token_exists():
            os.remove(TOKEN_FILE)
            print("✅ Token file deleted successfully")
        else:
            print("ℹ️ No token file to delete")
        return True
    except Exception as e:
        print(f"❌ Error deleting token file: {e}")
        return False
