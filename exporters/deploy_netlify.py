import requests
import json
from core.token_manager import get_token, NETLIFY_SERVICE

def deploy_netlify(code):
    token = get_token(NETLIFY_SERVICE)
    if not token:
        return False, "❌ No Netlify token found. Please save it first."

    url = "https://api.netlify.com/api/v1/sites"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/zip"
    }

    # For Netlify, we need to upload a ZIP of the site contents.
    import io, zipfile
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("index.html", code)
    zip_buffer.seek(0)

    files = {
        "file": ("site.zip", zip_buffer, "application/zip")
    }

    response = requests.post(url, headers={"Authorization": f"Bearer {token}"}, files=files)

    if response.status_code in (200, 201):
        site_data = response.json()
        site_url = site_data.get("url", "Unknown URL")
        return True, f"✅ Deployed successfully on Netlify! 🌐 {site_url}"
    else:
        return False, f"❌ Deployment failed: {response.status_code} - {response.text}"
