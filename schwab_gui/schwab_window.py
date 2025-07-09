from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy

from mongodb_connection.mongo_client import initialize_mongo_client
from schwab_gui.preview_order_history import PreviewOrderHistoryWidget
from schwab_gui.price_history_graph_widget import SchwabPriceHistoryGraphWidget
from schwab_gui.schwab_order_entry_widget import SchwabOrderEntryWidget
from schwab_gui.schwab_stock_data_widget import SchwabStockDataWidget
from gui.trade_app_selection import TradeAppSelectionWidget


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
        trading_app_selector_widget = TradeAppSelectionWidget(self)
        stock_data_widget = SchwabStockDataWidget(self.mongo_client)
        order_entry_widget = SchwabOrderEntryWidget(self.mongo_client)
        preview_order_history = PreviewOrderHistoryWidget(self.mongo_client)
        price_history_graph = SchwabPriceHistoryGraphWidget(self.mongo_client)

        # widget sizing
        stock_data_widget.setMinimumSize(300, 270)
        order_entry_widget.setMinimumSize(370, 300)
        preview_order_history.setMinimumSize(840, 200)
        price_history_graph.setMinimumSize(600, 850)

        order_entry_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # updates preview_order table when new order is created
        order_entry_widget.order_created.connect(preview_order_history.populate_order_history_table)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(trading_app_selector_widget, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(stock_data_widget, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(order_entry_widget, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addStretch()

        # horizontal layout
        horizontal_layout = QHBoxLayout()

        horizontal_layout.addLayout(layout)
        horizontal_layout.addWidget(price_history_graph)

        layout_wrapper = QVBoxLayout()
        layout_wrapper.addLayout(horizontal_layout, stretch=3)
        layout_wrapper.addWidget(preview_order_history, stretch=1)

        container = QWidget()
        container.setLayout(layout_wrapper)

        # sets window to display container
        self.setCentralWidget(container)
