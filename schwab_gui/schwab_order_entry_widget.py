import json

from PyQt6.QtWidgets import QWidget, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QTextEdit, \
    QGroupBox, QFormLayout

from gui import styling
from mongodb_connection.order_entries import insert_order_entry, fetch_order_entries
from schwab_connections.schwab_acccount_data import get_account_num
from schwab_connections.schwab_market_data import SchwabMarketData
from schwab_connections.schwab_preview_order import place_preview_order

class SchwabOrderEntryWidget(QWidget):
    def __init__(self, mongo_client):
        super().__init__()
        self.mongo_client = mongo_client

        self.market_data_controller = SchwabMarketData()
        self.current_symbol = "AAPL"
        self.account_num = "" # stores hashed account num needed for orders

        # widget label
        widget_label = QLabel("Preview Potential Orders")

        # symbol input
        self.symbol_input = QLineEdit(self.current_symbol)
        self.find_symbol_button = QPushButton("Search")
        self.find_symbol_button.clicked.connect(self.get_live_price_data)

        # symbol banner widgets/layout
        self.symbol_label = QLabel(self.current_symbol)
        self.last_price = QLabel("Last price: $")

        symbol_banner = QHBoxLayout()
        symbol_banner.addWidget(self.symbol_label)
        symbol_banner.addWidget(self.last_price)

        # updates price fields when websocket data transmitted
        self.market_data_controller.stock_data_updated.connect(self.handle_websocket_update)

        # quantity input
        quantity_label = QLabel("Quantity")
        self.quantity_input = QLineEdit()

        # order type selection
        order_type_label = QLabel("Order Type")
        self.order_type_dropdown = QComboBox()
        self.order_type_dropdown.addItems(['MARKET', 'LIMIT'])
        self.order_type_dropdown.activated.connect(self.check_order_type)

        # order details banner
        quantity_layout = QVBoxLayout()
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(self.quantity_input)

        order_type_layout = QVBoxLayout()
        order_type_layout.addWidget(order_type_label)
        order_type_layout.addWidget(self.order_type_dropdown)

        order_details_banner = QHBoxLayout()
        order_details_banner.addLayout(quantity_layout)
        order_details_banner.addLayout(order_type_layout)

        # limit price input
        limit_price_label = QLabel("Enter limit price in USD: ")
        self.limit_price = QLineEdit()

        # limit price container
        limit_price_layout = QVBoxLayout()
        limit_price_layout.addWidget(limit_price_label)
        limit_price_layout.addWidget(self.limit_price)
        self.limit_price_container = QWidget()
        self.limit_price_container.setLayout(limit_price_layout)
        self.limit_price_container.hide()

        # order banner widgets/layout
        self.bid_price = QLabel("Sell at: $")
        self.sell_button = QPushButton("Sell")
        self.sell_button.clicked.connect(self.preview_sell_order)
        self.ask_price = QLabel("Buy at: $")
        self.buy_button = QPushButton("Buy")
        self.buy_button.clicked.connect(self.preview_buy_order)

        order_banner = QHBoxLayout()
        order_banner.addWidget(self.bid_price)
        order_banner.addWidget(self.sell_button)
        order_banner.addWidget(self.ask_price)
        order_banner.addWidget(self.buy_button)

        # order preview display
        preview_label = QLabel("Preview Order Entry")
        note_label = QLabel("NOTE: there is no paper trading endpoint, so this will show you the preview of you order without placing one")

        # order details preview box
        self.order_group = QGroupBox("Order Details")
        order_preview_layout = QVBoxLayout()

        self.preview_symbol = QLabel("Symbol: ")
        order_preview_layout.addWidget(self.preview_symbol)

        self.preview_order_type = QLabel("Order Type: ")
        order_preview_layout.addWidget(self.preview_order_type)

        self.preview_action = QLabel("Action: ")
        order_preview_layout.addWidget(self.preview_action)

        # 'askPrice' if Market BUY order, 'bidPrice' if Market SELL order, 'price' if Limit order
        self.preview_individual_price = QLabel("Market Price: ")
        order_preview_layout.addWidget(self.preview_individual_price)

        self.preview_quantity = QLabel("Quantity: ")
        order_preview_layout.addWidget(self.preview_quantity)

        self.preview_total_value = QLabel("Total Order Value: ")
        order_preview_layout.addWidget(self.preview_total_value)

        self.preview_status = QLabel("Order Status: ")
        order_preview_layout.addWidget(self.preview_status)

        self.order_group.setLayout(order_preview_layout)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(widget_label)
        layout.addWidget(self.symbol_input)
        layout.addWidget(self.find_symbol_button)
        layout.addLayout(symbol_banner)
        layout.addLayout(order_details_banner)
        layout.addWidget(self.limit_price_container)
        layout.addLayout(order_banner)
        layout.addWidget(preview_label)
        layout.addWidget(note_label)
        layout.addWidget(self.order_group)

        self.setLayout(layout)

        self.order_group.hide()
        self.get_live_price_data()
        self.account_num = get_account_num()

        # styling
        widget_label.setFont(styling.heading_font)
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: gray;")

    # gets live price data for symbol input (if valid)
    def get_live_price_data(self):

        if self.market_data_controller.ws is not None:
            self.market_data_controller.ws.close()

        symbol = self.symbol_input.text()
        self.market_data_controller.run_market_data_socket(symbol)

    # updates price data on data transmission
    def handle_websocket_update(self, data):
        for key in data:
            if key == '1':
                bid_price = round(data[key], 2)
                self.bid_price.setText(f"Bid price: ${bid_price}")
            if key == '2':
                ask_price = round(data[key], 2)
                self.ask_price.setText(f"Ask price: ${ask_price}")
            if key == '3':
                last_price = round(data[key], 2)
                self.last_price.setText(f"Last price: ${last_price}")

    # if order type is limit, shows limit order details
    def check_order_type(self):
        if self.order_type_dropdown.currentText() == "LIMIT":
            self.limit_price_container.show()
        else:
            self.limit_price_container.hide()

    # sends preview of buy order
    def preview_buy_order(self):

        order_type = self.order_type_dropdown.currentText()
        quantity = self.quantity_input.text()

        if order_type == "LIMIT":
            limit_price = self.limit_price.text()
            order_preview = place_preview_order(self.account_num, order_type, "BUY", quantity, self.current_symbol, limit_price)
        else:
            order_preview = place_preview_order(self.account_num, order_type, "BUY", quantity, self.current_symbol)
        print(order_preview)

        self.update_preview_box(order_preview)

    # sends preview of sell order
    def preview_sell_order(self):

        order_type = self.order_type_dropdown.currentText()
        quantity = self.quantity_input.text()

        if order_type == "LIMIT":
            limit_price = self.limit_price.text()
            order_preview = place_preview_order(self.account_num, order_type, "SELL", quantity, self.current_symbol, limit_price)
        else:
            order_preview = place_preview_order(self.account_num, order_type, "SELL", quantity, self.current_symbol)
        print(order_preview)

        self.update_preview_box(order_preview)

    def update_preview_box(self, order_preview):
        if not self.order_group.isVisible():
            self.order_group.show()

        symbol = order_preview['orderStrategy']['orderLegs'][0]['finalSymbol']
        order_type = order_preview['orderStrategy']['orderType']
        action = order_preview['orderStrategy']['orderLegs'][0]['instruction']

        if action == "BUY" and order_type == "MARKET":
            individual_price = order_preview['orderStrategy']['orderLegs'][0]['askPrice']
        elif action == "SELL" and order_type == "MARKET":
            individual_price = order_preview['orderStrategy']['orderLegs'][0]['bidPrice']
        elif order_type == "LIMIT":
            individual_price = order_preview['orderStrategy']['price']

        quantity = order_preview['orderStrategy']['quantity']
        order_value = order_preview['orderStrategy']['orderValue']
        status = order_preview['orderStrategy']['status']

        self.preview_symbol.setText(symbol)
        self.preview_order_type.setText(f'Order Type: {order_type}')
        self.preview_action.setText(f'Action: {action}')
        self.preview_individual_price.setText(f'Individual Price: {individual_price}')
        self.preview_quantity.setText(f'Quantity: {quantity}')
        self.preview_total_value.setText(f'Total Order Value: {order_value}')
        self.preview_status.setText(f'Status: {status}')

        # inserts order into database
        try:
            insert_order_entry(self.mongo_client, order_preview)
        except Exception as e:
            print(f'Error inserting order document: {e}')
