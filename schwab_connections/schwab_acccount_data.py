import json
from dataclasses import dataclass

import requests

from schwab_connections.schwab_auth import validate_access_token

base_url = "https://api.schwabapi.com/trader/v1"

@dataclass
class StreamerIds:
    schwab_client_customer_id: str
    schwab_client_correl_id: str

streamer_ids = StreamerIds(
    schwab_client_customer_id = None,
    schwab_client_correl_id = None
)

# requests hash value of accounts for checking if user is authorized
def check_if_authorized():

    validate_access_token()
    with open('schwab_connections/tokens.json', 'r') as file:
        token_data = json.load(file)

    access_token = token_data['access_token']

    response = requests.get(f"{base_url}/accounts/accountNumbers", headers={'Authorization': f'Bearer {access_token}'})

    if response.status_code == 200:
        return True
    else:
        return False

# retrieves streamer ids needed for websocket requests
# assigns ids to StreamerIds dataclass
def get_streamer_ids():

    validate_access_token()
    with open('schwab_connections/tokens.json', 'r') as file:
        token_data = json.load(file)

    access_token = token_data['access_token']
    response = requests.get(f"{base_url}/userPreference", headers={'Authorization': f'Bearer {access_token}'})

    streamer_ids_res = response.json()["streamerInfo"][0]
    streamer_ids.schwab_client_customer_id = streamer_ids_res.get('schwabClientCustomerId')
    streamer_ids.schwab_client_correl_id = streamer_ids_res.get('schwabClientCorrelId')

# returns account number
def get_account_num():

    validate_access_token()

    with open('schwab_connections/tokens.json', 'r') as file:
        token_data = json.load(file)

    access_token = token_data['access_token']
    response = requests.get(f"{base_url}/accounts/accountNumbers", headers={'Authorization': f'Bearer {access_token}'})

    account_num = response.json()[0]['hashValue']
    print(f"Account number: {account_num}")
    return account_num
