import json
import requests

def get_cognito_public_keys():
    region = "YOUR_REGION"
    pool_id = "YOUR_POOL_ID"
    url = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json"

    resp = requests.get(url)
    return json.dumps(json.loads(resp.text)["keys"][1])