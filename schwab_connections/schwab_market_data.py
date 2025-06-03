import json
import threading

import requests
import websocket

from schwab_connections.schwab_acccount_data import get_streamer_ids, StreamerIds, streamer_ids
from schwab_connections.schwab_auth import validate_access_token

base_url = "https://api.schwabapi.com/marketdata/v1"
web_socket_url = "wss://streamer-api.schwab.com/ws"

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

# creates websocket object for live market data
# must be called before any other websocket methods
def open_market_data_websocket():

    # validates/retrieves necessary tokens and ids
    validate_access_token()
    with open('schwab_connections/tokens.json', 'r') as file:
        token_data = json.load(file)

    access_token = token_data['access_token']

    # only need to call get_streamer_ids() once per login
    get_streamer_ids()
    schwab_client_customer_id = streamer_ids.schwab_client_customer_id
    schwab_client_correl_id = streamer_ids.schwab_client_correl_id

    # event watches for valid login
    login_event = threading.Event()

    # websocket definitions
    def on_message(ws, message):
        print(f"Message: {message}")
        data = json.loads(message)
        command = data['response'][0]['command']
        response_code = data['response'][0]['content']['code']
        if response_code == 0 and command == "LOGIN":
            print("valid login")
            login_event.set()

    def on_error(ws, error):
        print(f"Error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print(f"Mkt Data web socket closed with code: {close_status_code}, message: {close_msg}")

    def on_open(ws):
        print("Websocket Open")

        login_payload = {
            'requestid': '1',
            'service': 'ADMIN',
            'command': 'LOGIN',
            'SchwabClientCustomerId': schwab_client_customer_id,
            'SchwabClientCorrelId': schwab_client_correl_id,
            'parameters': {
                'Authorization': access_token,
                "SchwabClientChannel": "IO",
                "SchwabClientFunctionId": "Tradeticket"
            }
        }

        ws.send(json.dumps(login_payload))
        print("sent login payload")

    # creates websocket object
    ws = websocket.WebSocketApp(
        web_socket_url,
        on_open=on_open,
        on_error=on_error,
        on_message=on_message,
        on_close=on_close
    )

    # starts websocket thread (uncomment threading when running gui)
    threading.Thread(target=ws.run_forever, daemon=True).start()
    # ws.run_forever()

    return ws, login_event

# opens web socket for real-time data streaming
def stream_stock_data(ws, symbol):

    # retrieves necessary ids
    schwab_client_customer_id = streamer_ids.schwab_client_customer_id
    schwab_client_correl_id = streamer_ids.schwab_client_correl_id

    # fields: 1: bid price, 2: ask price, 3: last price, 8: total volume, 10: high price, 11: low price, 12: close price,
    #         17: open price, 18: net change, 19: 52 week high, 20: 52 week low, 42: net % change
    mkt_data_payload = {
        'requestid': '2',
        'service': 'LEVELONE_EQUITIES',
        'command': 'SUBS',
        'SchwabClientCustomerId': schwab_client_customer_id,
        'SchwabClientCorrelId': schwab_client_correl_id,
        'parameters': {
            'keys': symbol,
            "fields": "1,2,3,8,10,11,12,17,18,19,20,42"
        }
    }

    print("opening data stream for ", symbol)
    ws.send(json.dumps(mkt_data_payload))
