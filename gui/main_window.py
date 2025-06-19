from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QFrame, \
    QDialog, QDialogButtonBox, QHBoxLayout, QTabWidget
from PyQt6.QtCore import QSize, Qt

import sys

from ibapi.contract import Contract

from gui.activity_widget import ActivityWidget
from gui.market_scanner_widget import MarketScannerWidget
from gui.order_entry_widget import OrderEntryWidget
from gui.portfolio_widget import PortfolioWidget
from gui.stock_data_widget import StockDataWidget
from gui.stock_graph_widget import StockGraphWidget
from gui.stock_news_widget import StockNewsWidget
from ibapi_connections.contract_data import req_contract_from_symbol
from ibapi_connections.market_data import get_live_prices_and_volume
from ibapi_connections.news import get_news_headlines


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("IB TWS API Trading GUI")

        # widgets to be added to layout

        # Order Entry widget
        #self.order_entry_widget = OrderEntryWidget(app)

        # Stock News widget
        self.stock_news_widget = StockNewsWidget(app)

        # Stock Graphs widget
        #self.stock_graphs_widget = StockGraphWidget(app)

        # Stock Data Widget
        #self.stock_data_widget = StockDataWidget(app)

        # Portfolio Widget
        self.portfolio_widget = PortfolioWidget(app)

        # Activity Widget
        self.activity_widget = ActivityWidget(app)

        # Market Scanner Widget
        self.market_scanner_widget = MarketScannerWidget(app)

        # Portfolio/Market Scanner tabs
        tab_widget = QTabWidget()
        portfolio_tab = self.portfolio_widget
        scanner_tab = self.market_scanner_widget

        tab_widget.addTab(portfolio_tab, "Portfolio")
        tab_widget.addTab(scanner_tab, "Market Scanner")

        # widget sizing
        # self.order_entry_widget.setMinimumSize(250, 600)
        # self.stock_data_widget.setMinimumSize(250, 600)
        # self.stock_graphs_widget.setMinimumSize(700, 600)
        self.portfolio_widget.setMinimumSize(650, 600)
        self.activity_widget.setMinimumSize(500, 300)

        # horizontal layout
        side_layout = QHBoxLayout()
        # side_layout.addWidget(self.order_entry_widget)
        # side_layout.addWidget(self.stock_data_widget)
        # side_layout.addWidget(self.stock_graphs_widget)
        side_layout.addWidget(tab_widget)

        # horizontal bottom layout
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.activity_widget)
        bottom_layout.addWidget(self.stock_news_widget)

        # layout
        layout = QVBoxLayout()
        layout.addLayout(side_layout)
        layout.addLayout(bottom_layout)

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
