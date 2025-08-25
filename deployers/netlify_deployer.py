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
        "Content-Type": "application/json"
    }

    payload = {
        "name": "karbon-generated-site",
        "files": {
            "index.html": code
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code in (200, 201):
            return True, "✅ Deployed successfully on Netlify!"
        else:
            return False, f"❌ Deployment failed: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"
