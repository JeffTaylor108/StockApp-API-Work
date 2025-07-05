import re

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QFrame, \
    QDialog, QDialogButtonBox, QComboBox, QHBoxLayout, QRadioButton, QButtonGroup, QStyle, QGroupBox, QListWidget
from PyQt6.QtCore import QSize, Qt, QTimer

from gui import styling
from ibapi_connections.contract_data import req_contract_from_symbol
from ibapi_connections.market_data import get_live_prices_and_volume

from ibapi.contract import Contract

from ibapi_connections.orders import submit_order, submit_bracket_order


class OrderEntryWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        # stored as Contract object
        self.stock_selected: Contract = None

        # checks if bracket order is attached
        self.is_bracket_order = False

        # widgets added to layout
        widget_label = QLabel("Buy and Sell Stocks")

        # stock dropdown
        self.stock_symbol_dropdown = QComboBox()
        self.stock_symbol_dropdown.addItems(['AAPL', 'TSLA', 'AMZN', 'NVDA', 'GOOGL'])
        self.stock_symbol_dropdown.setEditable(True)
        self.stock_symbol_dropdown.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)
        self.stock_symbol_dropdown.activated.connect(self.get_stock_selected)
        self.app.stock_symbol_changed.connect(self.handle_symbol_change_signal)

        # price display
        price_display_label = QLabel("Live Data (15 min delay):")
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
        limit_price_label = QLabel("Enter limit price in USD: ")
        self.limit_price = QLineEdit()
        self.limit_price.textChanged.connect(self.handle_limit_price_change)

        # limit price container
        limit_price_layout = QVBoxLayout()
        limit_price_layout.addWidget(limit_price_label)
        limit_price_layout.addWidget(self.limit_price)
        self.limit_price_container = QWidget()
        self.limit_price_container.setLayout(limit_price_layout)
        self.limit_price_container.hide()

        # quantity input
        quantity_label = QLabel("Enter quantity to order:")
        self.quantity = QLineEdit()
        self.quantity.textChanged.connect(self.handle_quantity_change)

        # buy/sell radio buttons
        self.buy_button = QRadioButton("BUY")
        self.buy_button.pressed.connect(self.set_bracket_order_dropdowns)
        self.sell_button = QRadioButton("SELL")
        self.sell_button.pressed.connect(self.set_bracket_order_dropdowns)

        self.buy_sell_group = QButtonGroup()
        self.buy_sell_group.addButton(self.buy_button)
        self.buy_sell_group.addButton(self.sell_button)
        self.buy_sell_group.buttonClicked.connect(self.get_estimated_cost)

        # estimated cost display
        self.estimated_cost = QLabel("")
        self.estimated_cost.setWordWrap(True)
        self.estimated_cost.hide()

        # bracket order button
        bracket_order_label = QLabel("Attach a bracket to order?")

        # horizontal layout for bracket label/button
        bracket_label_button_layout = QHBoxLayout()
        bracket_label_button_layout.addWidget(bracket_order_label)

        # bracket order inputs
        profit_taker_label = QLabel("Profit Taker:")
        self.profit_taker_input = QLineEdit()
        self.profit_taker_dropdown = QComboBox()
        self.profit_taker_dropdown.currentIndexChanged.connect(self.set_profit_taker_from_dropdown)

        stop_loss_label = QLabel("Stop Loss:")
        self.stop_loss_dropdown = QComboBox()
        self.stop_loss_input = QLineEdit()
        self.stop_loss_dropdown.currentIndexChanged.connect(self.set_stop_loss_from_dropdown)

        self.attach_bracket_button = QPushButton("Attach Bracket")
        self.attach_bracket_button.clicked.connect(self.attach_bracket)
        self.remove_bracket_button = QPushButton("Remove Bracket")
        self.remove_bracket_button.clicked.connect(self.remove_bracket)

        # bracket order input container
        bracket_order_layout = QVBoxLayout()
        profit_taker_horizontal_bar = QHBoxLayout()
        stop_loss_horizontal_bar = QHBoxLayout()
        bracket_order_layout.addWidget(profit_taker_label)
        profit_taker_horizontal_bar.addWidget(self.profit_taker_input, stretch=1)
        profit_taker_horizontal_bar.addWidget(self.profit_taker_dropdown, stretch=1)
        bracket_order_layout.addLayout(profit_taker_horizontal_bar)
        bracket_order_layout.addWidget(stop_loss_label)
        stop_loss_horizontal_bar.addWidget(self.stop_loss_input, stretch=1)
        stop_loss_horizontal_bar.addWidget(self.stop_loss_dropdown, stretch=1)
        bracket_order_layout.addLayout(stop_loss_horizontal_bar)
        bracket_order_layout.addWidget(self.attach_bracket_button)
        bracket_order_layout.addWidget(self.remove_bracket_button)

        self.bracket_order_container = QWidget()
        self.bracket_order_container.setLayout(bracket_order_layout)

        # order preview box
        self.order_preview_box = QGroupBox("Order Preview")
        order_preview_layout = QVBoxLayout()

        self.preview_symbol = QLabel(f"Symbol: {self.stock_symbol_dropdown.currentText()}")
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

        self.preview_brackets_label = QLabel("Brackets: ")
        self.preview_brackets = QListWidget()
        order_preview_layout.addWidget(self.preview_brackets_label)
        order_preview_layout.addWidget(self.preview_brackets)
        self.preview_brackets.hide()

        self.order_preview_box.setLayout(order_preview_layout)

        # submit order button
        self.submit_button = QPushButton("Submit Order")
        self.submit_button.clicked.connect(self.submit_order)

        # layout
        top_layout = QVBoxLayout()
        top_layout.addWidget(widget_label)
        top_layout.addWidget(self.stock_symbol_dropdown)
        top_layout.addWidget(price_display_label)
        top_layout.addWidget(self.bid_price)
        top_layout.addWidget(self.ask_price)
        top_layout.addWidget(self.last_traded_price)
        top_layout.addWidget(order_type_label)
        top_layout.addWidget(self.order_type_dropdown)
        top_layout.addWidget(self.limit_price_container)
        top_layout.addWidget(quantity_label)
        top_layout.addWidget(self.quantity)
        top_layout.addWidget(self.buy_button)
        top_layout.addWidget(self.sell_button)
        top_layout.addLayout(bracket_label_button_layout)
        top_layout.addWidget(self.bracket_order_container)
        top_layout.addWidget(self.submit_button)
        top_layout.addWidget(self.estimated_cost)

        top_container = QWidget()
        top_container.setLayout(top_layout)

        layout = QVBoxLayout()
        layout.addWidget(top_container, stretch=3)
        layout.addWidget(self.order_preview_box, stretch=1)

        self.setLayout(layout)

        # shows price for initial stock on app startup
        self.get_stock_selected()

        # fonts/styling
        widget_label.setFont(styling.heading_font)
        price_display_label.setFont(styling.heading_font)
        bracket_order_label.setFont(styling.heading_font)


    def get_stock_selected(self):

        # assigns stock selected to current stock
        self.app.check_current_symbol(self.stock_symbol_dropdown.currentText())
        print("Stock symbol selected: ", self.stock_symbol_dropdown.currentText())

        contract = req_contract_from_symbol(self.app, self.stock_symbol_dropdown.currentText())
        self.stock_selected = contract

        get_live_prices_and_volume(self.app, contract)

    def update_prices(self):
        if self.app.market_data.bid == -1:
            self.bid_price.setText(f'Bid Price: <span style="color: gray;">Market Closed</span>')
        else:
            self.bid_price.setText(f"Bid Price: ${self.app.market_data.bid}")

        if self.app.market_data.ask == -1:
            self.ask_price.setText(f'Ask Price: <span style="color: gray;">Market Closed</span>')
        else:
            self.ask_price.setText(f"Ask Price: ${self.app.market_data.ask}")

        self.last_traded_price.setText(f"Last Traded Price: ${self.app.market_data.last}")

    def check_order_type(self):
        if self.order_type_dropdown.currentText() == "LMT":
            self.limit_price_container.show()
            self.preview_order_type.setText("Order Type: LMT")
        else:
            self.limit_price_container.hide()
            self.preview_order_type.setText("Order Type: MKT")

    # checks to make sure all user input are valid before running get_estimated_cost
    def handle_limit_price_change(self):
        if self.buy_sell_group.checkedButton() and self.limit_price.text().isdigit() and self.quantity.text().isdigit():
            self.get_estimated_cost()
        else:
            return

    # checks to make sure all user input are valid before running get_estimated_cost
    def handle_quantity_change(self):
        self.preview_quantity.setText(f"Quantity: {self.quantity.text()}")
        if self.buy_sell_group.checkedButton() and self.quantity.text().isdigit():
            self.get_estimated_cost()
        else:
            return

    def get_estimated_cost(self):
        if self.order_type_dropdown.currentText() == "MKT":
            if self.buy_sell_group.checkedButton().text() == "BUY":

                # uses last price if market closed
                if self.app.market_data.ask != 0:
                    buy_cost = round(self.app.market_data.ask * int(self.quantity.text()), 2)

                    self.preview_individual_price.setText(f"Individual Price: ${self.app.market_data.ask}")
                    self.preview_total_value.setText(f"Total Buy Cost: ${buy_cost}")
                else:
                    buy_cost = round(self.app.market_data.last * int(self.quantity.text()), 2)

                    self.preview_individual_price.setText(f"Individual Price: ${self.app.market_data.last}")
                    self.preview_total_value.setText(f"Total Buy Cost: ${buy_cost}")

            elif self.buy_sell_group.checkedButton().text() == "SELL":

                # uses last price if market closed
                if self.app.market_data.bid != 0:
                    sell_price = round(self.app.market_data.bid * int(self.quantity.text()), 2)

                    self.preview_individual_price.setText(f"Individual Price: ${self.app.market_data.bid}")
                    self.preview_total_value.setText(f"Total Sell Value: ${sell_price}")
                else:
                    sell_price = round(self.app.market_data.last * int(self.quantity.text()), 2)

                    self.preview_individual_price.setText(f"Individual Price: ${self.app.market_data.last}")
                    self.preview_total_value.setText(f"Total Sell Value: ${sell_price}")

        if self.order_type_dropdown.currentText() == "LMT":

            if self.buy_sell_group.checkedButton().text() == "BUY":
                buy_cost = float(self.limit_price.text()) * int(self.quantity.text())

                self.preview_individual_price.setText(f"Individual Price: ${self.limit_price.text()}")
                self.preview_total_value.setText(f"Total Buy Cost if Triggered: ${buy_cost}")

            elif self.buy_sell_group.checkedButton().text() == "SELL":
                sell_price = float(self.limit_price.text()) * int(self.quantity.text())

                self.preview_individual_price.setText(f"Individual Price: ${self.limit_price.text()}")
                self.preview_total_value.setText(f"Total Sell Value if Triggered: ${sell_price}")

        self.estimated_cost.show()


    def submit_order(self):

        if self.app.nextOrderId is None:
            QTimer.singleShot(100, self.submit_order)
            return

        contract = self.stock_selected
        order_type = self.order_type_dropdown.currentText()
        quantity: int = int(self.quantity.text())
        action = self.buy_sell_group.checkedButton().text()

        print(f"Contract: {contract},\n Order Type: {order_type}, Quantity: {quantity}, Action: {action}")

        if order_type == "LMT": # checks if limit order
            limit_price = float(self.limit_price.text())

            if self.is_bracket_order: # checks if bracket order
                take_profit = float(self.profit_taker_input.text())
                stop_loss = float(self.stop_loss_input.text())

                submit_bracket_order(self.app, contract, action, order_type, quantity, take_profit, stop_loss, limit_price)
            else:
                submit_order(self.app, contract, action, order_type, quantity, limit_price)

        else:

            if self.is_bracket_order: # checks if bracket order
                take_profit = float(self.profit_taker_input.text())
                stop_loss = float(self.stop_loss_input.text())

                submit_bracket_order(self.app, contract, action, order_type, quantity, take_profit, stop_loss)
            else:
                submit_order(self.app, contract, action, order_type, quantity)

        print("Order successfully submitted!")

    def handle_symbol_change_signal(self):
        symbol = self.app.current_symbol
        self.stock_symbol_dropdown.setCurrentText(symbol)
        self.preview_symbol.setText(f"Symbol: {symbol}")

    def attach_bracket(self):

        self.is_bracket_order = True

        self.preview_brackets_label.setText("Brackets:")
        self.preview_brackets.show()
        self.preview_brackets.addItem(f"Profit Taker: ${self.profit_taker_input.text()}")
        self.preview_brackets.addItem(f"Stop Loss: ${self.stop_loss_input.text()}")

        print('Bracket attached!')

    def remove_bracket(self):

        self.is_bracket_order = False
        self.profit_taker_input.clear()
        self.stop_loss_input.clear()

        self.preview_brackets_label.setText("Brackets: None")
        self.preview_brackets.hide()
        self.preview_brackets.clear()

        print('Bracket removed!')

    # sets bracket order dropdown with values ranging from 10-100% of the stock's price
    def set_bracket_order_dropdowns(self):
        button_pressed = self.sender()

        if button_pressed.text() == "BUY":
            self.preview_action.setText("Action: BUY")

            price_text = self.ask_price.text()
            _, _, price = price_text.partition("$")

            self.profit_taker_dropdown.clear()
            self.stop_loss_dropdown.clear()

            self.profit_taker_dropdown.addItem("---")
            self.stop_loss_dropdown.addItem("---")

            for i in range(1, 11):
                formatted_price = f"{round(i * 0.10 * 100)}%"
                self.profit_taker_dropdown.addItem(f"ASK + {formatted_price}")
                self.stop_loss_dropdown.addItem(f"ASK - {formatted_price}")

        if button_pressed.text() == "SELL":
            self.preview_action.setText("Action: SELL")

            price_text = self.ask_price.text()
            _, _, price = price_text.partition("$")

            self.profit_taker_dropdown.clear()
            self.stop_loss_dropdown.clear()

            self.profit_taker_dropdown.addItem("---")
            self.stop_loss_dropdown.addItem("---")

            for i in range(1, 11):
                formatted_price = f"{round(i * 0.10 * 100)}%"
                self.profit_taker_dropdown.addItem(f"BID + {formatted_price}")
                self.stop_loss_dropdown.addItem(f"BID - {formatted_price}")

    # sets profit taker input to what was selected from dropdown
    def set_profit_taker_from_dropdown(self):
        if self.profit_taker_dropdown.currentText() != "---":
            dropdown_text = self.profit_taker_dropdown.currentText()
            percentage = re.search(r'(\d+)%', dropdown_text)
            percentage = percentage.group(1)

            checked_button = self.buy_sell_group.checkedButton()
            input_text = ''
            if checked_button is not None:
                if checked_button.text() == "BUY":
                    price_text = self.ask_price.text()

                    # checks if ask price is unavailable
                    if price_text.contains('Market Closed'):
                        price_text = self.last_traded_price.text()

                    _, _, price = price_text.partition("$")
                    input_text = round(float(price) + round((float(percentage) / 100) * float(price), 2), 2)

                if checked_button.text() == "SELL":
                    price_text = self.bid_price.text()
                    _, _, price = price_text.partition("$")
                    input_text = round(float(price) + round((float(percentage) / 100) * float(price), 2), 2)

        else:
            input_text = ""

        self.profit_taker_input.setText(str(input_text))

    # sets stop loss input to what was selected from dropdown
    def set_stop_loss_from_dropdown(self):
        if self.stop_loss_dropdown.currentText() != "---":
            dropdown_text = self.stop_loss_dropdown.currentText()
            percentage = re.search(r'(\d+)%', dropdown_text)
            percentage = percentage.group(1)

            checked_button = self.buy_sell_group.checkedButton()
            input_text = ''
            if checked_button is not None:
                if checked_button.text() == "BUY":
                    price_text = self.ask_price.text()

                    # checks if ask price is unavailable
                    if price_text.contains('Market Closed'):
                        price_text = self.last_traded_price.text()

                    _, _, price = price_text.partition("$")
                    input_text = round(float(price) - round((float(percentage) / 100) * float(price), 2), 2)

                if checked_button.text() == "SELL":
                    price_text = self.bid_price.text()
                    _, _, price = price_text.partition("$")
                    input_text = round(float(price) - round((float(percentage) / 100) * float(price), 2), 2)

        else:
            input_text = ""

        self.stop_loss_input.setText(str(input_text))