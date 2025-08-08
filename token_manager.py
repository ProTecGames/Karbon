import keyring


NETLIFY_SERVICE = "Karbon_Netlify"
VERCEL_SERVICE = "Karbon_Vercel"

def save_token(service, token):
    """Save the token securely in the OS keyring."""
    keyring.set_password(service, "access_token", token)
    print(f"✅ Token for {service} saved securely.")

def get_token(service):
    """Retrieve the token from the OS keyring."""
    token = keyring.get_password(service, "access_token")
    if not token:
        print(f"⚠ No token found for {service}. Please set it first.")
    return token

if __name__ == "__main__":
    save_token(NETLIFY_SERVICE, input("Enter your Netlify token: ").strip())
    save_token(VERCEL_SERVICE, input("Enter your Vercel token: ").strip())

    print("Netlify token:", get_token(NETLIFY_SERVICE))
    print("Vercel token:", get_token(VERCEL_SERVICE))
