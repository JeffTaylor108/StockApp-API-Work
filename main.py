import sys

from PyQt6.QtWidgets import QApplication
from schwab_gui.schwab_auth_window import SchwabAuthWindow


def main():

    # MOVED LOGIC TO TRADE_APP_SELECTION
    # ------------------------------------------------------------------
    # connects to TWS API on port 7497 (paper trading)
    # app = StockApp()
    # app.connect("127.0.0.1", 7497, 0)
    #
    # # starts app
    # thread = QThread()
    # app.moveToThread(thread)
    # thread.started.connect(app.run)
    # thread.start()
    #
    # # checks if app connected
    # print(f"App is connected: {app.isConnected()}")
    # ------------------------------------------------------------------

    # initializes GUI
    gui = QApplication(sys.argv)
    window = SchwabAuthWindow()
    window.show()

    # no logic can go after this
    sys.exit(gui.exec())

if __name__ == "__main__":
    main()