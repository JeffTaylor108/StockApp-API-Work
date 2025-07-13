from PyQt6.QtWidgets import QWidget, QLabel, QComboBox, QVBoxLayout
from ibapi.contract import Contract
from numpy.ma.core import append

from gui import styling
from ibapi_connections.contract_data import req_contract_from_symbol
from ibapi_connections.market_data import get_live_prices_and_volume, stop_mkt_data_stream, get_level2_market_data


class StockDataWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.stock_symbol_selected = None
        self.previous_stock_req_id = None

        # widgets added to layout
        widget_label = QLabel("Stock Data")

        # stock dropdown
        self.stock_symbol_dropdown = QComboBox()
        self.stock_symbol_dropdown.addItems(['AAPL', 'TSLA', 'AMZN', 'NVDA', 'GOOGL'])
        self.stock_symbol_dropdown.setEditable(True)
        self.stock_symbol_dropdown.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)
        self.stock_symbol_dropdown.activated.connect(self.get_stock_selected)
        self.app.stock_symbol_changed.connect(self.handle_symbol_change_signal)

        # data display
        self.price = QLabel("$")
        self.price_differential = QLabel("Price compared to open: ")
        self.volume = QLabel("Today's volume: ")
        self.bid_and_ask = QLabel("Bid/Ask: ")
        self.high_and_low = QLabel("Hi/Lo:")
        self.app.stock_prices_updated.connect(self.update_data)

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

        # gets stock selected on startup
        self.get_stock_selected()

        # fonts/styling
        widget_label.setFont(styling.heading_font)

    # make sure this is retrieving data from the right stream
    def get_stock_selected(self):
        symbol = self.stock_symbol_dropdown.currentText()
        self.stock_symbol_selected = symbol
        self.app.check_current_symbol(symbol)  # handles universal symbol change

        contract = req_contract_from_symbol(self.app, symbol)
        if contract is None:
            print(f"Could not find contract for symbol {symbol}")
            return

        get_live_prices_and_volume(self.app, contract)

    def update_data(self):
        stock_data = self.app.market_data
        print(f"STOCK DATA FOR {self.app.current_symbol}: {stock_data}")
        self.previous_stock_req_id = stock_data.req_id

        self.price.setText(f"Last Price: ${stock_data.last}")

        # handles if market never opened that day
        if stock_data.open == 0.0:
            self.price_differential.setText("Price compared to open: Data unavailable")
            self.volume.setText("Today's volume: Data unavailable")
            self.bid_and_ask.setText("Bid/Ask: Data unavailable")
            self.high_and_low.setText("Hi/Lo: Data unavailable")
            self.price_differential.setStyleSheet("color: gray;")
            self.volume.setStyleSheet("color: gray;")
            self.bid_and_ask.setStyleSheet("color: gray;")
            self.high_and_low.setStyleSheet("color: gray;")
        else:
            price_difference = round(stock_data.last - stock_data.open, 2)
            price_difference_percent = round(price_difference / stock_data.open * 100, 2)
            if price_difference >= 0:
                self.price_differential.setStyleSheet("color: green;")
            else:
                self.price_differential.setStyleSheet("color: red;")

            self.price_differential.setText(f"Price compared to open: {price_difference}    {price_difference_percent}%")
            self.volume.setText(f"Today's volume: {stock_data.volume}")
            self.bid_and_ask.setText(f"Bid/Ask: {stock_data.bid} x {stock_data.ask}")
            self.high_and_low.setText(f"Hi/Lo: {stock_data.high} x {stock_data.low}")

    def handle_symbol_change_signal(self):
        self.stock_symbol_dropdown.setCurrentText(self.app.current_symbol)
        self.get_stock_selected()