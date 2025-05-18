from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QFrame, \
    QDialog, QDialogButtonBox, QComboBox, QHBoxLayout, QRadioButton, QButtonGroup
from PyQt6.QtCore import QSize, Qt, QTimer

from ibapi_connections.contract_data import req_contract_from_symbol
from ibapi_connections.market_data import get_live_prices

from ibapi.contract import Contract

from ibapi_connections.orders import submit_order


class OrderEntryWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        # stored as Contract object
        self.stock_selected: Contract = None

        # widgets added to layout
        widget_label = QLabel("Buy and Sell Stocks")

        # stock dropdown
        self.stock_symbol_dropdown = QComboBox()
        self.stock_symbol_dropdown.addItems(['AAPL', 'TSLA', 'AMZN', 'NVDA', 'GOOGL'])
        self.stock_symbol_dropdown.setEditable(True)
        self.stock_symbol_dropdown.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)
        self.stock_symbol_dropdown.activated.connect(self.get_stock_selected)

        # price display
        self.bid_price = QLabel("Bid Price: ") # tick 66
        self.ask_price = QLabel("Ask Price: ") # tick 67
        self.last_traded_price = QLabel("Last Traded Price: ") # tick 68
        self.app.stock_prices_updated.connect(self.update_prices) # triggers when signal is received from IB

        # order type dropdown
        order_type_label = QLabel("Select Order Type")
        self.order_type_dropdown = QComboBox()
        self.order_type_dropdown.addItems(['MKT', 'LMT'])
        self.order_type_dropdown.activated.connect(self.check_order_type)

        # limit price input
        limit_price_label = QLabel("Enter limit price: ")
        self.limit_price = QLineEdit()

        limit_price_layout = QVBoxLayout()
        limit_price_layout.addWidget(limit_price_label)
        limit_price_layout.addWidget(self.limit_price)
        self.limit_price_container = QWidget()
        self.limit_price_container.setLayout(limit_price_layout)
        self.limit_price_container.hide()

        # quantity input
        quantity_label = QLabel("Enter quantity to order:")
        self.quantity = QLineEdit()

        # buy/sell radio buttons
        self.buy_button = QRadioButton("BUY")
        self.sell_button = QRadioButton("SELL")

        self.buy_sell_group = QButtonGroup()
        self.buy_sell_group.addButton(self.buy_button)
        self.buy_sell_group.addButton(self.sell_button)

        # submit order button
        self.submit_button = QPushButton("Submit Order")
        self.submit_button.clicked.connect(self.submit_order)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(widget_label)
        layout.addWidget(self.stock_symbol_dropdown)
        layout.addWidget(self.bid_price)
        layout.addWidget(self.ask_price)
        layout.addWidget(self.last_traded_price)
        layout.addWidget(order_type_label)
        layout.addWidget(self.order_type_dropdown)
        layout.addWidget(self.limit_price_container)
        layout.addWidget(quantity_label)
        layout.addWidget(self.quantity)
        layout.addWidget(self.buy_button)
        layout.addWidget(self.sell_button)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

        # shows price for initial stock on app startup
        self.get_stock_selected()


    def get_stock_selected(self):
        print("Stock symbol selected: ", self.stock_symbol_dropdown.currentText())

        contract = req_contract_from_symbol(self.app, self.stock_symbol_dropdown.currentText())
        self.stock_selected = contract

        get_live_prices(self.app, contract)

    def update_prices(self):
        self.bid_price.setText(f"Bid Price: {self.app.bid_price}")
        self.ask_price.setText(f"Ask Price: {self.app.ask_price}")
        self.last_traded_price.setText(f"Last Traded Price: {self.app.last_traded_price}")

    def check_order_type(self):
        if self.order_type_dropdown.currentText() == "LMT":
            self.limit_price_container.show()
        else:
            self.limit_price_container.hide()

    def submit_order(self):

        if self.app.nextOrderId is None:
            QTimer.singleShot(100, self.submit_order)
            return

        contract = self.stock_selected
        order_type = self.order_type_dropdown.currentText()
        quantity: int = int(self.quantity.text())
        action = self.buy_sell_group.checkedButton().text()

        print(f"Contract: {contract},\n Order Type: {order_type}, Quantity: {quantity}, Action: {action}")

        if order_type == "LMT":
            limit_price = float(self.limit_price.text())
            submit_order(self.app, contract, action, order_type, quantity, limit_price)

        else:
            submit_order(self.app, contract, action, order_type, quantity)

        print("Order successfully submitted!")