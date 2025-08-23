import os
from cryptography.fernet import Fernet

# Paths
KEY_FILE = "secret.key"
TOKEN_FILE = "tokens.enc"

# Service constants
NETLIFY_SERVICE = "netlify"
VERCEL_SERVICE = "vercel"

# -------------------- Key Handling --------------------
def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key

def load_key():
    if not os.path.exists(KEY_FILE):
        return generate_key()
    return open(KEY_FILE, "rb").read()

# -------------------- Token Handling --------------------
def _load_tokens():
    """Decrypt and return stored tokens dict"""
    if not os.path.exists(TOKEN_FILE):
        return {}
    try:
        key = load_key()
        f = Fernet(key)
        with open(TOKEN_FILE, "rb") as f_enc:
            decrypted = f.decrypt(f_enc.read())
        return eval(decrypted.decode())
    except Exception:
        return {}

def _save_tokens(tokens: dict):
    """Encrypt and save tokens dict"""
    try:
        key = load_key()
        f = Fernet(key)
        encrypted = f.encrypt(str(tokens).encode())
        with open(TOKEN_FILE, "wb") as f_enc:
            f_enc.write(encrypted)
        return True
    except Exception as e:
        print(f"❌ Error saving tokens: {e}")
        return False

def save_token(service: str, token: str):
    tokens = _load_tokens()
    tokens[service] = token
    return _save_tokens(tokens)

def get_token(service: str):
    tokens = _load_tokens()
    return tokens.get(service)

def clear_token(service: str):
    tokens = _load_tokens()
    if service in tokens:
        del tokens[service]
        return _save_tokens(tokens)
    return True
