from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QVBoxLayout

from gui import styling
from schwab_connections.schwab_market_data import SchwabMarketData


class SchwabStockDataWidget(QWidget):
    def __init__(self, mongo_client):
        super().__init__()
        self.mongo_client = mongo_client

        self.market_data_controller = SchwabMarketData()

        # widget label
        widget_label = QLabel("Stock Data")

        # stock symbol for quote retrieval
        quote_label = QLabel("Input stock symbol to see its quote data")
        self.symbol_input = QLineEdit()
        submit_symbol_button = QPushButton("Retrieve Quotes")
        submit_symbol_button.clicked.connect(self.get_live_stock_data)

        self.data_labels = {}
        self.stock_data_grid = QGridLayout()

        # connects to signal that updates stock data on emission
        self.market_data_controller.stock_data_updated.connect(self.handle_update_stock_data)

        fields = [
            "52 Week High", "52 Week Low", "Ask Price", "Bid Price", "Last Price", "Volume", "Open Price",
            "Close Price", "Low Price", "High Price", "Price Change", "% Price Change"
        ]

        for i, field in enumerate(fields):
            data_label_name = QLabel(f"{field}: ")
            data_value = QLabel("—")
            self.data_labels[field] = data_value

            # grid displays 2 fields per row
            self.stock_data_grid.addWidget(data_label_name, i // 2, (i % 2) * 2)
            self.stock_data_grid.addWidget(data_value, i // 2, (i % 2) * 2 + 1)

        layout = QVBoxLayout()
        layout.addWidget(widget_label)
        layout.addWidget(quote_label)
        layout.addWidget(self.symbol_input)
        layout.addWidget(submit_symbol_button)
        layout.addLayout(self.stock_data_grid)

        self.setLayout(layout)

        # fonts/styling
        widget_label.setFont(styling.heading_font)

    def get_live_stock_data(self):

        if self.market_data_controller.ws is not None:
            self.market_data_controller.ws.close()

        symbol = self.symbol_input.text()
        self.market_data_controller.run_market_data_socket(symbol)

    # finds label fields that match the update data transmitted from web socket and updates its value
    def handle_update_stock_data(self, data):
        print(data)

        # maps schwab's label for data to data labels present in GUI
        schwab_to_gui_fields = {
            "52WeekHigh": "52 Week High",
            "52WeekLow": "52 Week Low",
            "askPrice": "Ask Price",
            "bidPrice": "Bid Price",
            "lastPrice": "Last Price",
            "totalVolume": "Volume",
            "openPrice": "Open Price",
            "closePrice": "Close Price",
            "lowPrice": "Low Price",
            "highPrice": "High Price",
            "netChange": "Price Change",
            "netPercentChange": "% Price Change"
        }

        # maps schwab data labels to the integer that represents the data being sent
        schwab_labels = {
            "19": "52WeekHigh",
            "20": "52WeekLow",
            "2": "askPrice",
            "1": "bidPrice",
            "3": "lastPrice",
            "8": "totalVolume",
            "17": "openPrice",
            "12": "closePrice",
            "11": "lowPrice",
            "10": "highPrice",
            "18": "netChange",
            "42": "netPercentChange"
        }

        for key in data:
            print(f'key: {key}, value: {data[key]}')
            schwab_label = schwab_labels.get(key)
            gui_label = schwab_to_gui_fields.get(schwab_label)
            if gui_label in self.data_labels:
                data_value = round(data[key], 2)
                # changes % price change to correct format
                if key == '42':
                    self.data_labels[gui_label].setText(f'{str(data_value)}%')
                else:
                    self.data_labels[gui_label].setText(str(data_value))