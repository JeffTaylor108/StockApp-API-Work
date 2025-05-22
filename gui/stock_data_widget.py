from PyQt6.QtWidgets import QWidget, QLabel, QComboBox, QVBoxLayout
from ibapi.contract import Contract
from numpy.ma.core import append

from ibapi_connections.contract_data import req_contract_from_symbol
from ibapi_connections.market_data import get_live_prices


class StockDataWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        # widgets added to layout
        widget_label = QLabel("Stock Data")

        # stock dropdown
        self.stock_symbol_dropdown = QComboBox()
        self.stock_symbol_dropdown.addItems(['AAPL', 'TSLA', 'AMZN', 'NVDA', 'GOOGL'])
        self.stock_symbol_dropdown.setEditable(True)
        self.stock_symbol_dropdown.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)
        self.stock_symbol_dropdown.activated.connect(self.get_stock_selected)

        # data display
        self.price = QLabel("Price goes here")
        self.price_differential = QLabel("Difference between todays open and close")
        self.volume = QLabel("todays volume")
        self.bid_and_ask = QLabel(" todays bid and ask (bid/ask: bid x ask format)")
        self.high_and_low = QLabel("todays high - todays low(Hi/Lo: high x low format)")

        # layout
        layout = QVBoxLayout()
        layout.addWidget(widget_label)
        layout.addWidget(self.stock_symbol_dropdown)
        layout.addWidget(self.price)
        layout.addWidget(self.price_differential)
        layout.addWidget(self.volume)
        layout.addWidget(self.bid_and_ask)
        layout.addWidget(self.high_and_low)

        self.setLayout(layout)

    # make sure this is retrieving data from the right stream
    def get_stock_selected(self):
        symbol = self.stock_symbol_dropdown.currentText()
        print("Stock symbol selected: ", symbol)

        contract = req_contract_from_symbol(self.app, symbol)
        stock_data = get_live_prices(self.app, contract)

        print(stock_data)

        self.price.setText(f"{stock_data['last']}")
        self.price_differential.setText(f"Price difference: {stock_data['close'] - stock_data['open']}")