from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QFrame, \
    QDialog, QDialogButtonBox
from PyQt6.QtCore import QSize, Qt

import sys

from ibapi.contract import Contract

from gui.order_entry_widget import OrderEntryWidget
from gui.stock_news_widget import StockNewsWidget
from ibapi_connections.contract_data import req_contract_from_symbol
from ibapi_connections.market_data import get_live_prices, get_live_volume
from ibapi_connections.news import get_news_headlines
from ibapi_connections.orders import buy_stock, sell_stock


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("IB TWS API Trading GUI")

        # widgets to be added to layout
        # Order Entry widget
        self.order_entry_widget = OrderEntryWidget(app)

        # Stock News widget
        self.stock_news_widget = StockNewsWidget(app)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.order_entry_widget)
        layout.addWidget(self.stock_news_widget)

        # parent widget container for layout
        container = QWidget()
        container.setLayout(layout)

        # self.setFixedSize(QSize(500, 400))
        self.setCentralWidget(container) # sets window to display container


    # stops script on window close
    def closeEvent(self, event):
        print("Disconnecting from TWS")
        self.app.disconnect()
        event.accept()
