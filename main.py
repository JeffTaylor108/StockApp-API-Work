import sys
import time
import threading

from PyQt6.QtWidgets import QApplication

from ibapi_connections.app import StockApp
from ibapi_connections.contract_data import req_contract_from_symbol
from ibapi_connections.market_data import get_live_volume, get_live_price
from ibapi_connections.orders import buy_stock, deprecated_buy_stock, deprecated_sell_stock
from gui.main_window import MainWindow


def main():

    # connects to TWS API on port 7497 (paper trading)
    app = StockApp()
    app.connect("127.0.0.1", 7497, 0)
    time.sleep(1)

    # starts app
    api_thread = threading.Thread(target=app.run, daemon=True)
    api_thread.start()

    # checks if app connected
    print(f"App is connected: {app.isConnected()}")

    # initializes order reqIds for session
    app.reqIds(-1)

    # initalizing GUI
    gui = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()

    #testing(app)

    # no logic can go after this
    sys.exit(gui.exec())



# testing without GUI (GUI wont run if theres an input thread, so keep method commented out)
def testing(app):
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
        deprecated_buy_stock(app)

    if testing == "sell_stock":
        deprecated_sell_stock(app)

if __name__ == "__main__":
    main()