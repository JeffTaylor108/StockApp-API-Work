from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QFrame, \
    QDialog, QDialogButtonBox
from PyQt6.QtCore import QSize, Qt

import sys

from ibapi.contract import Contract

from ibapi_connections.contract_data import req_contract_from_symbol
from ibapi_connections.market_data import get_live_price, get_live_volume
from ibapi_connections.news import get_news_headlines
from ibapi_connections.orders import buy_stock, sell_stock


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("IB TWS API Trading GUI")

        # widgets to be added to layout
        self.label = QLabel("Enter the stock symbol you would like to see data for: ")
        self.input = QLineEdit()

        self.get_price_button = QPushButton("Get Price Data")
        self.get_price_button.clicked.connect(self.get_price)

        self.get_volume_button = QPushButton("Get Volume Data")
        self.get_volume_button.clicked.connect(self.get_volume)

        self.get_news_button = QPushButton("Get Recent News Headlines")
        self.get_news_button.clicked.connect(self.get_news)

        # create divider
        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.buy_sell_label = QLabel("Buying/Selling stock input")
        self.buy_sell_input = QLineEdit()

        self.buy_stock_button = QPushButton("Buy")
        self.buy_stock_button.clicked.connect(self.buy_stock)

        self.sell_stock_button = QPushButton("Sell")
        self.sell_stock_button.clicked.connect(self.sell_stock)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.get_price_button)
        layout.addWidget(self.get_volume_button)
        layout.addWidget(self.get_news_button)
        layout.addWidget(self.line)
        layout.addWidget(self.buy_sell_label)
        layout.addWidget(self.buy_sell_input)
        layout.addWidget(self.buy_stock_button)
        layout.addWidget(self.sell_stock_button)

        # parent widget container for layout
        container = QWidget()
        container.setLayout(layout)

        # self.setFixedSize(QSize(500, 400))
        self.setCentralWidget(container) # sets window to display container


    def get_price(self):
        print("Price button clicked!")
        symbol = self.input.text().upper()
        contract:Contract = req_contract_from_symbol(self.app, symbol)
        print(contract)
        get_live_price(self.app, contract)

    def get_volume(self):
        print("Volume button clicked!")
        symbol = self.input.text().upper()
        contract:Contract = req_contract_from_symbol(self.app, symbol)
        print(contract)
        get_live_volume(self.app, contract)

    def get_news(self):
        print("News button clicked!")
        symbol = self.input.text().upper()
        contract:Contract = req_contract_from_symbol(self.app, symbol)
        print(contract)
        get_news_headlines(self.app, contract)

    def buy_stock(self):
        print("Buy stock button clicked!")
        symbol = self.buy_sell_input.text().upper()
        contract:Contract = req_contract_from_symbol(self.app, symbol)
        print(contract)

        dialog = BuySellDialog("buy")
        if dialog.exec():
            quantity = dialog.get_quantity()
            print(f"Quantity entered: {quantity}")
            buy_stock(self.app, contract, quantity)

        else:
            print("Purchase cancelled")

    def sell_stock(self):
        print("Sell stock button clicked!")
        symbol = self.buy_sell_input.text().upper()
        contract:Contract = req_contract_from_symbol(self.app, symbol)
        print(contract)

        dialog = BuySellDialog("sell")
        if dialog.exec():
            quantity = dialog.get_quantity()
            print(f"Quantity entered: {quantity}")
            sell_stock(self.app, contract, quantity)

        else:
            print("Purchase cancelled")


    # stops script on window close
    def closeEvent(self, event):
        print("Disconnecting from TWS")
        self.app.disconnect()
        event.accept()

class BuySellDialog(QDialog):
    def __init__(self, order_action):
        super().__init__()

        self.setWindowTitle("Quantity")

        if order_action == "buy":
            self.quantity_label = QLabel("How many would you like to purchase?")
        if order_action == "sell":
            self.quantity_label = QLabel("How many would you like to sell?")
        self.quantity_input = QLineEdit()

        buttons = (QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.quantity_label)
        layout.addWidget(self.quantity_input)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def get_quantity(self):
        return self.quantity_input.text()
