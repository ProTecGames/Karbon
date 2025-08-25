import requests
import json
from core.token_manager import get_token, VERCEL_SERVICE

def deploy_vercel(code):
    token = get_token(VERCEL_SERVICE)
    if not token:
        return False, "❌ No Vercel token found. Please save it first."

    url = "https://api.vercel.com/v13/deployments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "name": "karbon-generated-site",
        "files": [
            {
                "file": "index.html",
                "data": code
            }
        ],
        "target": "production"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code in (200, 201):
        return True, "✅ Deployed successfully on Vercel!"
    else:
        return False, f"❌ Deployment failed: {response.status_code} - {response.text}"

