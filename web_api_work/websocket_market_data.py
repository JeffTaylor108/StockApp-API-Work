import websocket
import time
import ssl
import requests
import json
from functools import partial
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
base_url = "https://localhost:5000/v1/api/"

def confirm_status():
    endpoint = 'iserver/auth/status'
    auth_req = requests.get(url=base_url+endpoint, verify=False)
    print(auth_req)

confirm_status()

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket closed with code: {close_status_code}, message: {close_msg}")

def on_open(ws, conids):
    print("Opened connection")
    time.sleep(3)

    for conid in conids:
        msg = f'smd+{conid}+{{"fields":["31","84","86"]}}' # smd is the topic for 'market data'
        print("Sending: ", msg)
        ws.send(msg)

# gets conids from stock symbols input
def get_conids_from_symbols():
    symbols = []
    conids = []
    endpoint = "iserver/secdef/search"
    while True:
        symbol = input("Enter the company symbol you want to open a web socket for: ")

        if symbol.lower() == "done":
            break
        symbols.append(symbol)

    for symbol in symbols:
        params = {
            'symbol': symbol.upper(),
            'secType': "STK",
            'name': False
        }
        request_url = base_url + endpoint
        conid_req = requests.get(url=request_url, verify=False, params=params)
        conids.append(conid_req.json()[0]['conid'])

    print(conids)
    return conids

# opens Web Socket
if __name__ == "__main__":
    conids = get_conids_from_symbols()
    ws = websocket.WebSocketApp(
        url="wss://localhost:5000/v1/api/ws",
        on_open=partial(on_open, conids=conids),
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever(sslopt={"cert_reqs":ssl.CERT_NONE})