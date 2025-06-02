import json

import requests

from schwab_connections.schwab_auth import validate_access_token

# requests hash value of accounts for checking if user is authorized
def check_if_authorized():

    validate_access_token()
    with open('schwab_connections/tokens.json', 'r') as file:
        token_data = json.load(file)

    access_token = token_data['access_token']
    base_url = "https://api.schwabapi.com/trader/v1/accounts/accountNumbers"

    response = requests.get(f"{base_url}", headers={'Authorization': f'Bearer {access_token}'})

    if response.status_code == 200:
        return True
    else:
        return False