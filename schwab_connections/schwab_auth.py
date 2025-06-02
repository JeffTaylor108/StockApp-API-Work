import base64
import os
import time
from dotenv import load_dotenv
import requests
import json


def get_app_key():
    load_dotenv()
    app_key = os.getenv("APP_KEY")
    return app_key

def get_app_secret():
    load_dotenv()
    app_secret = os.getenv("APP_SECRET")
    return app_secret

def get_auth_url():
    app_key = get_app_key()
    auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}&redirect_uri=https://127.0.0.1"
    return auth_url

def authorize(returned_link):

    app_key = get_app_key()
    app_secret = get_app_secret()

    returned_link = returned_link

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
    token_dict['refresh_expire_time'] = time.time() + 604800 # current epoch time + 7 days in seconds
    expires_in = token_dict['expires_in']
    token_dict['expire_time'] = time.time() + expires_in # returns epoch time + 1800 seconds

    tokens_json = json.dumps(token_dict, indent=4)
    with open("schwab_connections/tokens.json", "w") as token_file:
        token_file.write(tokens_json)

    print(token_dict)
    print("API access authorized")
    return True


# validates access token, refreshing it if needed
def validate_access_token():

    load_dotenv()
    app_key = os.getenv("APP_KEY")
    app_secret = os.getenv("APP_SECRET")

    with open('schwab_connections/tokens.json', 'r') as file:
        token_data = json.load(file)

    # checks if the current epoch time (with 10 second padding) is greater than or equal to the token expiry time
    if token_data['expire_time'] <= time.time() - 10:
        print("Access token expired")

        refresh_headers = {
            'Authorization': f'Basic {base64.b64encode(bytes(f"{app_key}:{app_secret}", "utf-8")).decode("utf-8")}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        refresh_data = {
            'grant_type': 'refresh_token',
            'refresh_token': token_data['refresh_token']
        }

        # request to refresh access token, using refresh token
        new_access_token_response = requests.post('https://api.schwabapi.com/v1/oauth/token', headers=refresh_headers, data=refresh_data)

        new_token_dict = new_access_token_response.json()
        new_token_dict['expire_time'] = time.time() + new_token_dict['expires_in']
        new_token_dict['refresh_expire_time'] = token_data['refresh_expire_time']

        # replaces old tokens with valid tokens
        new_tokens_json = json.dumps(new_token_dict, indent=4)
        with open("schwab_connections/tokens.json", "w") as token_file:
            token_file.write(new_tokens_json)

        print("Access token refreshed: ", new_token_dict)

    else:
        print('Access token valid!')

def get_refresh_expire_time():
    try:
        with open('schwab_connections/tokens.json', 'r') as file:
            token_data = json.load(file)
        print("refresh expire time: ", token_data.get('refresh_expire_time'))
        return token_data['refresh_expire_time']

    except Exception as e:
        print(e)
        return "No Token Found"

if __name__ == "__main__":
    authorize()