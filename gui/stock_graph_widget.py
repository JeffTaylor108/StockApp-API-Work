from datetime import datetime
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QComboBox, QHBoxLayout
from ibapi.contract import Contract

from gui import styling
from ibapi_connections.contract_data import req_contract_from_symbol
from ibapi_connections.market_data import get_market_data_graph


class StockGraphWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        # widgets added to layout
        widget_label = QLabel("View Graphs of Market Data")

        # graph options layout
        graph_options_layout = QHBoxLayout()

        # stock dropdown for graph
        self.stock_dropdown = QComboBox()
        self.stock_dropdown.addItems(['AAPL', 'TSLA', 'AMZN', 'NVDA', 'GOOGL'])
        self.stock_dropdown.setEditable(True)
        self.stock_dropdown.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)
        self.stock_dropdown.activated.connect(self.create_candlestick_graph)

        # candlestick interval dropdown
        self.interval_dropdown = QComboBox()
        self.interval_dropdown.addItems(['10 mins', '30 mins', '1 hour', '2 hours', '3 hours', '1 day'])
        self.interval_dropdown.setCurrentIndex(1)
        self.interval_dropdown.currentIndexChanged.connect(self.create_candlestick_graph)

        graph_options_layout.addWidget(self.stock_dropdown)
        graph_options_layout.addWidget(self.interval_dropdown)

        # graph widget
        self.plot_item = pg.PlotItem()
        self.market_data_graph = pg.PlotWidget(plotItem=self.plot_item)
        self.market_data_graph.showGrid(x=True, y=True)
        self.market_data_graph.setTitle("Price History")
        self.market_data_graph.setLabel("left", "Price")
        self.market_data_graph.setLabel("bottom", "Date")

        # market data hover display
        self.market_data_hover_display = QLabel("")

        # layout
        layout = QVBoxLayout()
        layout.addWidget(widget_label)
        layout.addLayout(graph_options_layout)
        layout.addWidget(self.market_data_graph)

        self.setLayout(layout)

        self.create_candlestick_graph()

        # fonts/styling
        widget_label.setFont(styling.heading_font)


    # generated mostly by ChatGPT
    def create_candlestick_graph(self):
        symbol = self.stock_dropdown.currentText()
        contract: Contract = req_contract_from_symbol(self.app, symbol)
        interval = self.interval_dropdown.currentText()
        data = get_market_data_graph(self.app, contract, interval)

        # removes previous graph
        self.plot_item.clear()

        x_axis = []
        axis_dates = []

        for i, bar in enumerate(data):
            candle_width = 0.6
            top = max(bar.open, bar.close)
            bottom = min(bar.open, bar.close)

            # Body (rectangle)
            color = 'g' if bar.close >= bar.open else 'r'
            bar_item = pg.BarGraphItem(x=[i], height=[top - bottom], width=candle_width, y=bottom, brush=color)
            self.plot_item.addItem(bar_item)

            # Wick (line from low to high)
            wick = pg.PlotDataItem(x=[i, i], y=[bar.low, bar.high], pen=pg.mkPen(color, width=1))
            self.plot_item.addItem(wick)

            # Track x-labels
            x_axis.append(i)
            axis_dates.append(bar.date)

        # Apply x-axis date labels
        string_axis = pg.AxisItem(orientation='bottom')
        ticks = []
        for i, bar in enumerate(data):

            if i % 8 == 0:
                date_str = bar.date.strip()
                # Remove timezone if present
                if " US/Eastern" in date_str:
                    date_str = date_str.replace(" US/Eastern", "")

                try:
                    dt = datetime.strptime(date_str, "%Y%m%d %H:%M:%S")
                    label = dt.strftime("%b %d %H:%M")
                except ValueError:
                    dt = datetime.strptime(date_str, "%Y%m%d")
                    label = dt.strftime("%b %d")

                ticks.append((i, label))

        string_axis.setTicks([ticks])
        self.market_data_graph.getAxis('bottom').setTicks([ticks])
        self.market_data_graph.enableAutoRange()