from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import *
from ibapi.order import *
import time
import threading
from app import StockApp
from account_data import account_summary_testing
from contract_data import req_contract_from_symbol
from market_data import get_live_volume, get_live_price
from orders import buy_stock, sell_stock


def main():

    # connects to TWS API on port 7497 (paper trading)
    app = StockApp()
    app.connect("127.0.0.1", 7497, 0)
    time.sleep(1)

    # starts app
    api_thread = threading.Thread(target=app.run)
    api_thread.start()

    # checks if app connected
    print(f"App is connected: {app.isConnected()}")

    # initializes order reqIds for session
    app.reqIds(-1)

    # method logic goes here
    testing = input("What stub do you want to test? ")

    if testing == "get_live_volume":
        contract = req_contract_from_symbol(app)
        print(contract)
        get_live_volume(app, contract)

    if testing == "get_live_price":
        contract = req_contract_from_symbol(app)
        print(contract.symbol)
        get_live_price(app, contract)

    if testing == "buy_stock":
        buy_stock(app)

    if testing == "sell_stock":
        sell_stock(app)

if __name__ == "__main__":
    main()