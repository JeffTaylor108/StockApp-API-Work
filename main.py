import sys
import time
import threading

from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QApplication

from ibapi_connections.app import StockApp
from ibapi_connections.account_data import currently_held_positions
from ibapi_connections.contract_data import req_contract_from_symbol
from ibapi_connections.market_data import get_live_prices_and_volume
from gui.main_window import MainWindow
from schwab_gui.schwab_auth_window import SchwabAuthWindow
from schwab_gui.schwab_window import MainSchwabWindow


def main():

    # connects to TWS API on port 7497 (paper trading)
    app = StockApp()
    app.connect("127.0.0.1", 7497, 0)

    # starts app
    thread = QThread()
    app.moveToThread(thread)
    thread.started.connect(app.run)
    thread.start()

    # checks if app connected
    print(f"App is connected: {app.isConnected()}")

    # initalizing GUI (uncomment after testing schwab gui)
    # gui = QApplication(sys.argv)
    # window = MainWindow(app)
    # window.show()

    # testing for Schwab GUI
    gui = QApplication(sys.argv)
    window = SchwabAuthWindow()
    window.show()

    # no logic can go after this
    sys.exit(gui.exec())

if __name__ == "__main__":
    main()