import json

import requests

from schwab_connections.schwab_auth import validate_access_token


def get_quotes(symbol):

    # must validate access token before any API calls
    validate_access_token()

    with open('schwab_connections/tokens.json', 'r') as file:
        token_data = json.load(file)

    access_token = token_data['access_token']
    base_url = "https://api.schwabapi.com/marketdata/v1"

    quote_response = requests.get(f"{base_url}/{symbol}/quotes?fields=quote",
                                  headers={'Authorization': f'Bearer {access_token}'})

    print(quote_response.json())
    return quote_response.json()