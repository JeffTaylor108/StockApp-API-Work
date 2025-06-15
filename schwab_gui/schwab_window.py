import json

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QTableWidget, \
    QGridLayout, QHBoxLayout

from gui import styling
from mongodb_connection.mongo_client import initialize_mongo_client
from schwab_connections.schwab_market_data import SchwabMarketData
from schwab_connections.schwab_auth import get_auth_url, authorize
from schwab_gui.preview_order_history import PreviewOrderHistoryWidget
from schwab_gui.price_history_graph_widget import SchwabPriceHistoryGraphWidget
from schwab_gui.schwab_order_entry_widget import SchwabOrderEntryWidget
from schwab_gui.schwab_stock_data_widget import SchwabStockDataWidget


class MainSchwabWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Charles Schwab API Trading GUI")
        self.current_stock = None
        try:
            self.mongo_client = initialize_mongo_client()
        except Exception as e:
            print(f'Error initializing mongo client, {e}')

        # widgets to be added to layout
        stock_data_widget = SchwabStockDataWidget(self.mongo_client)
        order_entry_widget = SchwabOrderEntryWidget(self.mongo_client)
        preview_order_history = PreviewOrderHistoryWidget(self.mongo_client)
        price_history_graph = SchwabPriceHistoryGraphWidget(self.mongo_client)

        # widget sizing
        stock_data_widget.setMinimumSize(300, 270)
        preview_order_history.setMinimumSize(840, 400)
        price_history_graph.setMinimumSize(600, 400)
        self.adjustSize()

        # updates preview_order table when new order is created
        order_entry_widget.order_created.connect(preview_order_history.populate_order_history_table)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(stock_data_widget)
        layout.addWidget(order_entry_widget)

        # horizontal layout
        horizontal_layout = QHBoxLayout()

        horizontal_layout.addLayout(layout)
        horizontal_layout.addWidget(price_history_graph)

        layout_wrapper = QVBoxLayout()
        layout_wrapper.addLayout(horizontal_layout)
        layout_wrapper.addWidget(preview_order_history)

        container = QWidget()
        container.setLayout(layout_wrapper)

        # sets window to display container
        self.setCentralWidget(container)
