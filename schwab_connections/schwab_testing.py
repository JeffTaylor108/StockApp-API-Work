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
order_data = {
  "orderId": 0,
  "orderStrategy": {
    "accountNumber": account_num,
    "advancedOrderType": "NONE",
    "closeTime": "2025-06-06T20:48:43.047Z",
    "enteredTime": "2025-06-06T20:48:43.047Z",
    "orderBalance": {
      "orderValue": 0,
      "projectedAvailableFund": 0,
      "projectedBuyingPower": 0,
      "projectedCommission": 0
    },
    "orderStrategyType": "SINGLE",
    "orderVersion": 0,
    "session": "NORMAL",
    "status": "AWAITING_PARENT_ORDER",
    "allOrNone": True,
    "discretionary": True,
    "duration": "DAY",
    "filledQuantity": 0,
    "orderType": "MARKET",
    "orderValue": 0,
    "price": 0,
    "quantity": 0,
    "remainingQuantity": 0,
    "sellNonMarginableFirst": True,
    "settlementInstruction": "REGULAR",
    "strategy": "NONE",
    "amountIndicator": "DOLLARS",
    "orderLegs": [
      {
        "askPrice": 0,
        "bidPrice": 0,
        "lastPrice": 0,
        "markPrice": 0,
        "projectedCommission": 0,
        "quantity": 0,
        "finalSymbol": "string",
        "legId": 0,
        "assetType": "EQUITY",
        "instruction": "BUY"
      }
    ]
  },
  "orderValidationResult": {
    "alerts": [
      {
        "validationRuleName": "string",
        "message": "string",
        "activityMessage": "string",
        "originalSeverity": "ACCEPT",
        "overrideName": "string",
        "overrideSeverity": "ACCEPT"
      }
    ],
    "accepts": [
      {
        "validationRuleName": "string",
        "message": "string",
        "activityMessage": "string",
        "originalSeverity": "ACCEPT",
        "overrideName": "string",
        "overrideSeverity": "ACCEPT"
      }
    ],
    "rejects": [
      {
        "validationRuleName": "string",
        "message": "string",
        "activityMessage": "string",
        "originalSeverity": "ACCEPT",
        "overrideName": "string",
        "overrideSeverity": "ACCEPT"
      }
    ],
    "reviews": [
      {
        "validationRuleName": "string",
        "message": "string",
        "activityMessage": "string",
        "originalSeverity": "ACCEPT",
        "overrideName": "string",
        "overrideSeverity": "ACCEPT"
      }
    ],
    "warns": [
      {
        "validationRuleName": "string",
        "message": "string",
        "activityMessage": "string",
        "originalSeverity": "ACCEPT",
        "overrideName": "string",
        "overrideSeverity": "ACCEPT"
      }
    ]
  },
  "commissionAndFee": {
    "commission": {
      "commissionLegs": [
        {
          "commissionValues": [
            {
              "value": 0,
              "type": "COMMISSION"
            }
          ]
        }
      ]
    },
    "fee": {
      "feeLegs": [
        {
          "feeValues": [
            {
              "value": 0,
              "type": "COMMISSION"
            }
          ]
        }
      ]
    },
    "trueCommission": {
      "commissionLegs": [
        {
          "commissionValues": [
            {
              "value": 0,
              "type": "COMMISSION"
            }
          ]
        }
      ]
    }
  }
}

order_response = requests.post(f"{base_url}{endpoint}",
                              headers={'Authorization': f'Bearer {access_token}',
                                       'Content-Type': 'application/json'},
                              json=order_data
                              )
print(order_response.status_code)
print(order_response.json())