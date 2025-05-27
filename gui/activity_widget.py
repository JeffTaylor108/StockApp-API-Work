from functools import partial

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout

from gui import styling
from ibapi_connections.orders import get_active_orders, get_completed_orders, cancel_order


class ActivityWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        # widgets added to layout
        widget_label = QLabel("Order Activity")

        # buttons to select between active orders and completed orders
        active_orders_button = QPushButton('Active Orders')
        completed_orders_button = QPushButton('Completed Orders')
        active_orders_button.clicked.connect(self.get_active_orders)
        completed_orders_button.clicked.connect(self.get_completed_orders)

        # orders table (last column stores cancel button)
        self.table_label = QLabel("Active Orders")
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels(["Ticker Symbol", "Action", "Type", "Quantity", "Fill Price", "Status", ""])
        self.app.completed_orders_updated.connect(self.update_orders)
        self.app.active_orders_updated.connect(self.update_orders)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(widget_label)
        table_selector = QHBoxLayout()
        table_selector.addWidget(active_orders_button)
        table_selector.addWidget(completed_orders_button)
        layout.addLayout(table_selector)
        layout.addWidget(self.orders_table)

        self.setLayout(layout)

        # fonts/styling
        widget_label.setFont(styling.heading_font)

        self.get_active_orders()

    def get_active_orders(self):

        self.orders_table.setRowCount(0)
        self.table_label.setText("Active Orders")

        get_active_orders(self.app)
        for order in self.app.active_orders.values():

            row_position = self.orders_table.rowCount()
            self.orders_table.insertRow(row_position)

            cancel_button = QPushButton("Cancel")
            cancel_button.clicked.connect(partial(cancel_order, self.app, order.order_id))

            self.orders_table.setItem(row_position, 0, QTableWidgetItem(order.symbol))
            self.orders_table.setItem(row_position, 1, QTableWidgetItem(order.action))
            self.orders_table.setItem(row_position, 2, QTableWidgetItem(order.type))
            self.orders_table.setItem(row_position, 3, QTableWidgetItem(f"0/{str(order.quantity)}"))
            self.orders_table.setItem(row_position, 4, QTableWidgetItem(str(order.fill_price)))
            self.orders_table.setItem(row_position, 5, QTableWidgetItem(order.status))
            self.orders_table.setCellWidget(row_position, 6, cancel_button)

    def get_completed_orders(self):

        self.orders_table.setRowCount(0)
        self.table_label.setText("Completed Orders")

        get_completed_orders(self.app)
        for order in self.app.completed_orders:

            row_position = self.orders_table.rowCount()
            self.orders_table.insertRow(row_position)

            self.orders_table.setItem(row_position, 0, QTableWidgetItem(order.symbol))
            self.orders_table.setItem(row_position, 1, QTableWidgetItem(order.action))
            self.orders_table.setItem(row_position, 2, QTableWidgetItem(order.type))
            self.orders_table.setItem(row_position, 3, QTableWidgetItem(f"0/{str(order.quantity)}"))
            self.orders_table.setItem(row_position, 4, QTableWidgetItem(str(order.fill_price)))
            self.orders_table.setItem(row_position, 5, QTableWidgetItem(order.status))
            self.orders_table.setItem(row_position, 6, QTableWidgetItem(""))

    def update_orders(self):

        self.orders_table.setRowCount(0)
        if self.table_label.text() == "Completed Orders":

            for order in self.app.completed_orders:
                row_position = self.orders_table.rowCount()
                self.orders_table.insertRow(row_position)

                self.orders_table.setItem(row_position, 0, QTableWidgetItem(order.symbol))
                self.orders_table.setItem(row_position, 1, QTableWidgetItem(order.action))
                self.orders_table.setItem(row_position, 2, QTableWidgetItem(order.type))
                self.orders_table.setItem(row_position, 3, QTableWidgetItem(f"0/{str(order.quantity)}"))
                self.orders_table.setItem(row_position, 4, QTableWidgetItem(str(order.fill_price)))
                self.orders_table.setItem(row_position, 5, QTableWidgetItem(order.status))
                self.orders_table.setItem(row_position, 6, QTableWidgetItem(""))

        elif self.table_label.text() == "Active Orders":

            for order in self.app.active_orders.values():
                row_position = self.orders_table.rowCount()
                self.orders_table.insertRow(row_position)

                cancel_button = QPushButton("Cancel")
                cancel_button.clicked.connect(partial(cancel_order, self.app, order.order_id))

                self.orders_table.setItem(row_position, 0, QTableWidgetItem(order.symbol))
                self.orders_table.setItem(row_position, 1, QTableWidgetItem(order.action))
                self.orders_table.setItem(row_position, 2, QTableWidgetItem(order.type))
                self.orders_table.setItem(row_position, 3, QTableWidgetItem(f"0/{str(order.quantity)}"))
                self.orders_table.setItem(row_position, 4, QTableWidgetItem(str(order.fill_price)))
                self.orders_table.setItem(row_position, 5, QTableWidgetItem(order.status))
                self.orders_table.setCellWidget(row_position, 6, cancel_button)