import time

from schwab_connections.schwab_market_data import stream_stock_data, open_market_data_websocket

websocket, login_event = open_market_data_websocket()
if login_event.wait(timeout=5):
    stream_stock_data(websocket, 'AAPL')
else:
    print("time out")

while True:
    print('running')
    time.sleep(2)