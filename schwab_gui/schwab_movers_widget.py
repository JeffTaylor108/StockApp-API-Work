from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QTableWidget, QComboBox, QHBoxLayout, QPushButton, \
    QTableWidgetItem

from gui import styling
from schwab_connections.schwab_market_data import SchwabMarketData


class SchwabMoversWidget(QWidget):
    def __init__(self, mongo_client):
        super().__init__()
        self.mongo_client = mongo_client

        self.market_data_controller = SchwabMarketData()

        # widget label
        widget_label = QLabel("Top Movers")

        # sort by attribute / frequency selectors
        sort_label = QLabel("Sort Top Movers By: ")
        attribute_selector_label = QLabel("Attribute: ")
        self.attribute_selector = QComboBox()
        self.attribute_selector.addItems(["Volume", "Trades", "Percent Change Up", "Percent Change Down"])

        frequency_selector_label = QLabel("Frequency (biggest movers for that period): ")
        self.frequency_selector = QComboBox()
        self.frequency_selector.addItems(["Most Recent", "1 min", "5 min", "10 min", "30 min", "60 min"])

        # sort bar layout
        sort_bar_layout = QHBoxLayout()
        sort_bar_layout.addWidget(attribute_selector_label)
        sort_bar_layout.addWidget(self.attribute_selector)
        sort_bar_layout.addWidget(frequency_selector_label)
        sort_bar_layout.addWidget(self.frequency_selector)

        # find top movers button
        self.find_movers_button = QPushButton("Find Top Movers")
        self.find_movers_button.pressed.connect(self.get_top_movers)

        # top mover table
        self.top_mover_table = QTableWidget()
        self.top_mover_table.setRowCount(10)
        self.top_mover_table.setColumnCount(7)
        self.top_mover_table.setHorizontalHeaderLabels(["Company Name", "Symbol", "Last Price", "Net Change", "Net % Change", "Volume", "Market Share"])

        # layout
        layout = QVBoxLayout()
        layout.addWidget(widget_label)
        layout.addWidget(sort_label)
        layout.addLayout(sort_bar_layout)
        layout.addWidget(self.find_movers_button)
        layout.addWidget(self.top_mover_table)

        self.setLayout(layout)

        # fonts/styling
        widget_label.setFont(styling.heading_font)

    def get_top_movers(self):

        attribute = self.attribute_selector.currentText().upper()
        attribute = attribute.replace(" ", "_")

        frequency = self.frequency_selector.currentText()
        if frequency == "Most Recent":
            frequency = 0
        else:
            frequency = frequency[0]

        print(f'getting top movers for attribute {attribute} and frequency {frequency}')
        mover_data = self.market_data_controller.fetch_movers(attribute, frequency)
        self.populate_mover_table(mover_data)

    def populate_mover_table(self, mover_data):
        print('populating table')

        row = 0
        for instrument in mover_data['screeners']:
            self.top_mover_table.setItem(row, 0, QTableWidgetItem(instrument['description']))
            self.top_mover_table.setItem(row, 1, QTableWidgetItem(instrument['symbol']))
            self.top_mover_table.setItem(row, 2, QTableWidgetItem(str(instrument['lastPrice'])))
            self.top_mover_table.setItem(row, 3, QTableWidgetItem(str(instrument['netChange'])))
            self.top_mover_table.setItem(row, 4, QTableWidgetItem(str(instrument['netPercentChange'])))
            self.top_mover_table.setItem(row, 5, QTableWidgetItem(str(instrument['volume'])))
            self.top_mover_table.setItem(row, 6, QTableWidgetItem(str(instrument['marketShare'])))
            row += 1

    def clear_mover_table(self):
        self.top_mover_table.clear()
        print("mover table cleared")