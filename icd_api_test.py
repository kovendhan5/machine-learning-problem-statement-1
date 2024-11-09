import os
import requests
from functools import lru_cache

# ICD API credentials (environment variables - KEEP THESE SECURE!)
CLIENT_ID = os.environ.get("YOUR_CLIENT_ID") 
CLIENT_SECRET = os.environ.get("YOUR_CLIENT_SECRET")  # Replace with your actual client secret
ICD_API_URL = "https://icdaccessmanagement.who.int/connect/token"

@lru_cache(maxsize=1)  # Cache the access token
def get_icd_access_token():
    url = f"{ICD_API_URL}/Token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        token_data = response.json()
        return token_data.get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error during access token retrieval: {e}")
        return None

def get_icd_codes(query):
    token = get_icd_access_token()
    if token is None:
        print("Error: Could not obtain ICD access token.")
        return []

    url = f"{ICD_API_URL}/GetICD11CodeInfo"
    headers = {
        "Accept": "application/json",
        "API-Version": "v2",
        "Authorization": f"Bearer {token}"
    }
    params = {"q": query, "useFlexisearch": "true"}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        icd_codes = [item["code"] for item in data.get("linearizations", []) if "code" in item]
        return icd_codes
    except requests.exceptions.RequestException as e:
        print(f"Error in ICD API request: {e}")
        return []

if __name__ == '__main__':
    query = "diabetes"  # Replace with your search query
    icd_codes = get_icd_codes(query)
    print("ICD Codes:", icd_codes)
