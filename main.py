from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import *
from ibapi.order import *
import time
import threading
from app import StockApp
from account_data import account_summary_testing

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

    # method logic goes here
    account_summary_testing(app)


if __name__ == "__main__":
    main()