from functools import partial

from PyQt6.QtWidgets import QWidget, QLabel, QTableWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidgetItem

from gui import styling
from mongodb_connection.order_entries import fetch_order_entries, database_delete_order


class PreviewOrderHistoryWidget(QWidget):
    def __init__(self, mongo_client):
        super().__init__()
        self.mongo_client = mongo_client

        # widgets to be added to layout
        widget_label = QLabel("Preview Order History")

        # orders table (last column stores delete button)
        self.table_label = QLabel("Orders")
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(8)
        self.orders_table.setHorizontalHeaderLabels(
            ["Ticker Symbol", "Type", "Action", "Individual Price", "Quantity",
             "Total Order Value", "Status", ""])

        # layout
        layout = QVBoxLayout()
        layout.addWidget(widget_label)
        layout.addWidget(self.orders_table)

        self.setLayout(layout)

        self.populate_order_history_table()

        # fonts/styling
        widget_label.setFont(styling.heading_font)

    # fetches order documents and updates order history table
    def populate_order_history_table(self):
        self.orders_table.setRowCount(0)

        try:
            order_documents = fetch_order_entries(self.mongo_client)
        except Exception as e:
            print(f'Error fetching order_documents from db: {e}')

        for order in order_documents:
            print(order)
            row_position = self.orders_table.rowCount()
            self.orders_table.insertRow(row_position)

            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(partial(self.delete_order, order['_id']))

            self.orders_table.setItem(row_position, 0, QTableWidgetItem(order['symbol']))
            self.orders_table.setItem(row_position, 1, QTableWidgetItem(order['order_type']))
            self.orders_table.setItem(row_position, 2, QTableWidgetItem(order['action']))
            self.orders_table.setItem(row_position, 3, QTableWidgetItem(str(order['individual_price'])))
            self.orders_table.setItem(row_position, 4, QTableWidgetItem(str(order['quantity'])))
            self.orders_table.setItem(row_position, 5, QTableWidgetItem(str(order['order_value'])))
            self.orders_table.setItem(row_position, 6, QTableWidgetItem(order['status']))
            self.orders_table.setCellWidget(row_position, 7, delete_button)

    # deletes order document from database and table
    def delete_order(self, order_id):

        database_delete_order(self.mongo_client, order_id) # deletes from database
        self.populate_order_history_table() # repopulates table with orders
