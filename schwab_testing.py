import base64
import os

import requests

app_key = os.getenv("APP_KEY")
app_secret = os.getenv("APP_SECRET")

auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}&redirect_uri=https://127.0.0.1"

print(f"Click to authenticate: {auth_url}")

# after auth link and user authenticates, schwab will redirect to a page that doesn't display anything
# the link schwab redirects to must be copy/pasted into the console
returned_link = input("Paste the returned url here:")

# code necessary for authentication
code = f"{returned_link[returned_link.index('code=')+5:returned_link.index('%40')]}@"

headers = {
    'Authorization': f'Basic {base64.b64encode(bytes(f"{app_key}:{app_secret}", "utf-8")).decode("utf-8")}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = {
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': 'https://127.0.0.1'
}

# responds with tokens necessary for interacting  with api
response = requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)

token_dict = response.json()
access_token = token_dict['access_token'] # token lasts 30 mins, must be refreshed by refresh token
refresh_token = token_dict['refresh_token'] # token lasts 1 week, after that auth must occur again

base_url = "https://api.schwabapi.com/trader/v1/"

# all requests must include Authorization header with the access token
response = requests.get(f"{base_url}/accounts/accountNumbers", headers={'Authorization': f'Bearer: {access_token}'})

print(response.json())
