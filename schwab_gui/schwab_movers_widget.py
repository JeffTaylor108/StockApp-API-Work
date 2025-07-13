from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

from gui import styling
from schwab_connections.schwab_market_data import SchwabMarketData


class SchwabMoversWidget(QWidget):
    def __init__(self, mongo_client):
        super().__init__()
        self.mongo_client = mongo_client

        self.market_data_controller = SchwabMarketData()

        # widget label
        widget_label = QLabel("Top Movers")

        # layout
        layout = QVBoxLayout()
        layout.addWidget(widget_label)

        self.setLayout(layout)

        self.get_top_movers()

        # fonts/styling
        widget_label.setFont(styling.heading_font)

    def get_top_movers(self):
        self.market_data_controller.fetch_movers("VOLUME", 0)