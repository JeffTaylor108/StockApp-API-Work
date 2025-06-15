import json
import threading

import requests
import websocket
from PyQt6.QtCore import pyqtSignal, QObject

from schwab_connections.schwab_acccount_data import get_streamer_ids, streamer_ids
from schwab_connections.schwab_auth import validate_access_token


class SchwabMarketData(QObject):

    # pyqt6 signal for updating GUI
    stock_data_updated = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self.base_url = "https://api.schwabapi.com/marketdata/v1"
        self.web_socket_url = "wss://streamer-api.schwab.com/ws"
        self.ws = None

    def get_quotes(self, symbol):

        # must validate access token before any API calls
        validate_access_token()
        with open('schwab_connections/tokens.json', 'r') as file:
            token_data = json.load(file)

        access_token = token_data['access_token']

        quote_response = requests.get(f"{self.base_url}/{symbol}/quotes?fields=quote",
                                      headers={'Authorization': f'Bearer {access_token}'})

        print(quote_response.json())
        return quote_response.json()

    # creates websocket object for live market data
    def open_market_data_websocket(self, symbol):

        # validates/retrieves necessary tokens and ids
        validate_access_token()
        with open('schwab_connections/tokens.json', 'r') as file:
            token_data = json.load(file)

        access_token = token_data['access_token']

        # only need to call get_streamer_ids() once per login
        get_streamer_ids()
        schwab_client_customer_id = streamer_ids.schwab_client_customer_id
        schwab_client_correl_id = streamer_ids.schwab_client_correl_id

        # websocket definitions
        def on_message(ws, message):
            print(f"Message: {message}")
            data = json.loads(message)

            # accounts for heartbeat messages that don't contain 'response'
            if "response" in data:
                command = data['response'][0]['command']
                response_code = data['response'][0]['content']['code']
                if response_code == 0 and command == "LOGIN":
                    print("valid login")

            elif "data" in data:
                stock_data = data['data'][0]['content'][0]
                self.stock_data_updated.emit(stock_data)

        def on_error(ws, error):
            print(f"Error: {error}")

        def on_close(ws, close_status_code, close_msg):
            print(f"{symbol} Mkt Data web socket closed with code: {close_status_code}, message: {close_msg}")

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
                    "fields": "0,1,2,3,8,10,11,12,17,18,19,20,42"
                }
            }

            combined_payload = {
                "requests": [
                    login_payload,
                    mkt_data_payload
                ]
            }

            print("opening data stream for ", symbol)
            print(json.dumps(combined_payload))
            ws.send(json.dumps(combined_payload))

        # creates websocket object
        self.ws = websocket.WebSocketApp(
            self.web_socket_url,
            on_open=on_open,
            on_error=on_error,
            on_message=on_message,
            on_close=on_close
        )
        self.ws.run_forever()

    # safely starts websocket thread
    def run_market_data_socket(self, symbol):
        ws_thread = threading.Thread(target=lambda: self.open_market_data_websocket(symbol))
        ws_thread.daemon = True
        ws_thread.start()


    def fetch_price_history(self, symbol, period, frequency):
        # validate access token before API call
        validate_access_token()
        with open('schwab_connections/tokens.json', 'r') as file:
            token_data = json.load(file)

        access_token = token_data['access_token']

        # parses period and frequency
        period_value = period.split()[0]
        frequency_value = frequency.split()[0]
        print(period_value)

        price_history = requests.get(f"{self.base_url}/pricehistory?symbol={symbol}&periodType=day&"
                                     f"period={period_value}&frequencyType=minute&frequency={frequency_value}",
                                      headers={'Authorization': f'Bearer {access_token}'})
        data = price_history.json()
        return data['candles']