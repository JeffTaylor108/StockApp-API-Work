import json

import requests

from schwab_connections.schwab_auth import validate_access_token

base_url = "https://api.schwabapi.com/marketdata/v1"
web_socket_url = "https://api.schwabapi.com/ws"

def get_quotes(symbol):

    # must validate access token before any API calls
    validate_access_token()
    with open('schwab_connections/tokens.json', 'r') as file:
        token_data = json.load(file)

    access_token = token_data['access_token']

    quote_response = requests.get(f"{base_url}/{symbol}/quotes?fields=quote",
                                  headers={'Authorization': f'Bearer {access_token}'})

    print(quote_response.json())
    return quote_response.json()

# opens web socket for real-time data streaming
def stream_stock_data(symbol):

    validate_access_token()
    with open('schwab_connections/tokens.json', 'r') as file:
        token_data = json.load(file)

    access_token = token_data['access_token']

