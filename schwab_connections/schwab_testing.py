import base64
import os
import json

from dotenv import load_dotenv

import requests

from schwab_connections.schwab_acccount_data import get_account_num
from schwab_connections.schwab_auth import validate_access_token

# must validate access token before any API calls
validate_access_token()

with open('schwab_connections/tokens.json', 'r') as file:
    token_data = json.load(file)

access_token = token_data['access_token']
base_url = "https://api.schwabapi.com"

# all requests must include Authorization header with the access token
response = requests.get(f"{base_url}/trader/v1/accounts/accountNumbers", headers={'Authorization': f'Bearer {access_token}'})
print(response.json())

# market data calls

symbol = 'AAPL'
# request retrieves market data quote for a single symbol provided (can specify more fields if needed)
quote_response = requests.get(f"{base_url}/marketdata/v1/{symbol}/quotes?fields=quote", headers={'Authorization': f'Bearer {access_token}'})
print(quote_response.json())

# request retrieves price history candles based on the following params: periodType (day/week/month), period (ex: 5 would collect data from past 5 days/week/month), frequencyType (minute/hour/day), frequency (how frequently data is retrieved)
# ex: /marketdata/v1/pricehistory?symbol={symbol}&periodType=day&period=5&frequencyType=minute&frequency=15
# gets the price history for the past 5 days, and shows the price history at 15 min intervals across the past 5 days
price_history_candles_response = requests.get(f"{base_url}/marketdata/v1/pricehistory?symbol={symbol}&periodType=day&period=5&frequencyType=minute&frequency=15", headers={'Authorization': f'Bearer {access_token}'})
print(price_history_candles_response.json())


# preview order POST API call

account_num = get_account_num()

endpoint = f'/trader/v1/accounts/{account_num}/previewOrder'

# order data to be sent with request
mkt_order_data = {
  "orderType": "MARKET",
  "session": "NORMAL",
  "duration": "GOOD_TILL_CANCEL",
  "orderStrategyType": "SINGLE",
  "orderLegCollection": [
   {
    "instruction": "BUY",
    "quantity": 15,
    "instrument": {
     "symbol": "SPY",
     "assetType": "EQUITY"
    }
   }
  ]
}

# example for limit order data
limit_order_data = {
  "orderType": "LIMIT",
  "session": "NORMAL",
  "price": "100.00",
  "duration": "GOOD_TILL_CANCEL",
  "orderStrategyType": "SINGLE",
  "orderLegCollection": [
   {
    "instruction": "BUY",
    "quantity": 1,
    "instrument": {
     "symbol": "SPY",
     "assetType": "EQUITY"
    }
   }
  ]
}

# example for bracket order data
bracket_order_data = {
  "orderStrategyType": "TRIGGER",
  "session": "NORMAL",
  "duration": "GOOD_TILL_CANCEL",
  "orderType": "LIMIT",
  "price": 14.97,
  "orderLegCollection": [
   {
    "instruction": "BUY",
    "quantity": 5,
    "instrument": {
     "assetType": "EQUITY",
     "symbol": "SPY"
    }
   }
  ],
  "childOrderStrategies": [
   {
    "orderStrategyType": "OCO",
    "childOrderStrategies": [
     {
      "orderStrategyType": "SINGLE",
      "session": "NORMAL",
      "duration": "GOOD_TILL_CANCEL",
      "orderType": "LIMIT",
      "price": 15.27,
      "orderLegCollection": [
       {
        "instruction": "SELL",
        "quantity": 5,
        "instrument": {
         "assetType": "EQUITY",
         "symbol": "SPY"
        }
       }
      ]
     },
     {
      "orderStrategyType": "SINGLE",
      "session": "NORMAL",
      "duration": "GOOD_TILL_CANCEL",
      "orderType": "STOP",
      "stopPrice": 11.27,
      "orderLegCollection": [
       {
        "instruction": "SELL",
        "quantity": 5,
        "instrument": {
         "assetType": "EQUITY",
         "symbol": "SPY"
        }
       }
      ]
     }
    ]
   }
  ]
}

order_response = requests.post(f"{base_url}{endpoint}",
                              json=limit_order_data,
                              headers={'Authorization': f'Bearer {access_token}',
                                       'Content-Type': 'application/json'}
                              )
print(order_response.status_code)
print(order_response.json())