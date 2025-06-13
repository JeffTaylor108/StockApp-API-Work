import json

import requests

from schwab_connections.schwab_auth import validate_access_token

base_url = "https://api.schwabapi.com"

# post request to preview order
def place_preview_order(account_num, order_type, action, quantity, symbol, limit_price=None):

    validate_access_token()

    # fetches access token after validation
    with open('schwab_connections/tokens.json', 'r') as file:
        token_data = json.load(file)

    access_token = token_data['access_token']

    # json data to be transmitted in POST request
    order_data = {
        "orderType": order_type,
        "session": "NORMAL",
        "duration": "GOOD_TILL_CANCEL",
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [
            {
                "instruction": action,
                "quantity": quantity,
                "instrument": {
                    "symbol": symbol,
                    "assetType": "EQUITY"
                }
            }
        ]
    }

    if limit_price is not None:
        order_data['price'] = str(limit_price)

    # sends and receives POST request to preview order endpoint
    order_response = requests.post(f"{base_url}/trader/v1/accounts/{account_num}/previewOrder",
                                   json=order_data,
                                   headers={'Authorization': f'Bearer {access_token}',
                                            'Content-Type': 'application/json'}
                                   )

    return order_response.json()