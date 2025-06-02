import json

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QTableWidget, \
    QGridLayout

from schwab_connections.schwab_market_data import get_quotes, stream_stock_data
from schwab_connections.schwab_auth import get_auth_url, authorize


class MainSchwabWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Charles Schwab API Trading GUI")
        self.current_stock = None

        # widgets to be added to layout

        # stock symbol for quote retrieval
        quote_label = QLabel("Input stock symbol to see its quote data")
        self.symbol_input = QLineEdit()
        submit_symbol_button = QPushButton("Retrieve Quotes")
        submit_symbol_button.clicked.connect(self.get_live_stock_data)

        # quote data display
        self.quote_data_display = QTextEdit()
        self.quote_data_display.setReadOnly(True)

        # stock data grid
        grid_label = QLabel("Stock Data")

        self.data_labels = {}
        self.stock_data_grid = QGridLayout()

        fields = [
            "52 Week High", "52 Week Low", "Ask Price", "Bid Price", "Last Price", "Volume", "Open Price",
            "Close Price", "Low Price", "High Price", "Price Change", "% Price Change",
        ]

        for i, field in enumerate(fields):
            data_label_name = QLabel(f"{field}: ")
            data_value = QLabel("—")
            self.data_labels[field] = data_value

            # grid displays 2 fields per row
            self.grid.addWidget(data_label_name, i // 2, (i % 2) * 2)
            self.grid.addWidget(data_value, i // 2, (i % 2) * 2 + 1)


        # layout
        layout = QVBoxLayout()
        layout.addWidget(quote_label)
        layout.addWidget(self.symbol_input)
        layout.addWidget(submit_symbol_button)
        layout.addWidget(self.quote_data_display)
        layout.addWidget(grid_label)
        layout.addLayout(self.stock_data_grid)

        container = QWidget()
        container.setLayout(layout)

        # sets window to display container
        self.setCentralWidget(container)

    def get_stock_data(self):
        symbol = self.symbol_input.text()
        quote_data = get_quotes(symbol)
        self.current_stock = symbol

        quote_data_str = json.dumps(quote_data, indent=4)
        self.quote_data_display.setText(quote_data_str)

    def get_live_stock_data(self):
        symbol = self.symbol_input.text()
        stream_stock_data(symbol)