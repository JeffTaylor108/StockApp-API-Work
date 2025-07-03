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
        self.stock_dropdown.currentTextChanged.connect(self.create_candlestick_graph)
        self.app.stock_symbol_changed.connect(self.handle_symbol_change_signal)

        # graph period dropdown
        self.period_dropdown = QComboBox()
        self.period_dropdown.addItems(['1 Week', '3 Days', '1 Day', '12 Hours', '6 Hours', '2 Hours', '30 Min'])
        self.period_dropdown.setCurrentIndex(0)
        self.period_dropdown.currentIndexChanged.connect(self.create_candlestick_graph)

        # candlestick interval dropdown
        self.interval_dropdown = QComboBox()
        self.interval_dropdown.addItems(['30 secs', '1 min', '10 mins', '30 mins', '1 hour', '2 hours', '3 hours', '1 day'])
        self.interval_dropdown.setCurrentIndex(3)
        self.interval_dropdown.currentIndexChanged.connect(self.create_candlestick_graph)

        graph_options_layout.addWidget(self.stock_dropdown)
        graph_options_layout.addWidget(self.period_dropdown)
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

    # generated mostly by Claude
    def create_candlestick_graph(self):
        symbol = self.stock_dropdown.currentText()
        self.app.check_current_symbol(symbol)  # handles universal symbol change
        contract: Contract = req_contract_from_symbol(self.app, symbol)
        period = self.period_dropdown.currentText()
        interval = self.interval_dropdown.currentText()
        data = get_market_data_graph(self.app, contract, period, interval)

        # removes previous graph
        self.plot_item.clear()

        if not data:
            print("No data to plot")
            return

        # Process all candles and separate by type for batch processing
        self._create_optimized_candlesticks_tws(data)

        # Set up x-axis labels efficiently
        self._setup_axis_labels_tws(data)

        self.market_data_graph.enableAutoRange()
        print(f"Successfully plotted {len(data)} candles")

    def _create_optimized_candlesticks_tws(self, data):
        """Highly optimized candlestick chart using batched drawing operations for TWS data"""

        if not data:
            return

        candle_width = 0.6

        # Separate bullish and bearish candles for batch processing
        bullish_bodies = []
        bearish_bodies = []
        bullish_wicks = []
        bearish_wicks = []
        doji_lines = []

        # Colors
        bullish_color = 'g'
        bearish_color = 'r'
        bullish_pen = pg.mkPen(bullish_color, width=1)
        bearish_pen = pg.mkPen(bearish_color, width=1)

        # Process all candles and group by type
        for i, bar in enumerate(data):
            open_price = bar.open
            close_price = bar.close
            high_price = bar.high
            low_price = bar.low

            is_bullish = close_price >= open_price
            body_top = max(open_price, close_price)
            body_bottom = min(open_price, close_price)
            body_height = body_top - body_bottom

            # Group candle bodies
            if body_height > 0:
                if is_bullish:
                    bullish_bodies.append({
                        'x': i,
                        'height': body_height,
                        'y0': body_bottom
                    })
                else:
                    bearish_bodies.append({
                        'x': i,
                        'height': body_height,
                        'y0': body_bottom
                    })
            else:
                # Doji candle - draw as horizontal line
                doji_lines.extend([
                    [i - candle_width / 2, i + candle_width / 2],
                    [open_price, open_price]
                ])

            # Group wicks (full range from low to high)
            wick_data = ([i, i], [low_price, high_price])
            if is_bullish:
                bullish_wicks.append(wick_data)
            else:
                bearish_wicks.append(wick_data)

        # Draw bullish candles in batches
        if bullish_bodies:
            self._draw_candle_bodies_tws(bullish_bodies, bullish_color, candle_width)

        if bearish_bodies:
            self._draw_candle_bodies_tws(bearish_bodies, bearish_color, candle_width)

        # Draw wicks in batches
        self._draw_wick_lines_tws(bullish_wicks, bullish_pen)
        self._draw_wick_lines_tws(bearish_wicks, bearish_pen)

        # Draw doji lines
        if doji_lines:
            self._draw_doji_lines_tws(doji_lines, bullish_pen)

    def _draw_candle_bodies_tws(self, bodies, color, width):
        """Draw candle bodies efficiently using single BarGraphItem"""
        if not bodies:
            return

        x_vals = [body['x'] for body in bodies]
        heights = [body['height'] for body in bodies]
        y0_vals = [body['y0'] for body in bodies]

        # Create single BarGraphItem for all bodies of the same type
        bars = pg.BarGraphItem(
            x=x_vals,
            height=heights,
            width=width,
            y0=y0_vals,
            brush=color,
            pen=pg.mkPen(color, width=1)
        )
        self.plot_item.addItem(bars)

    def _draw_wick_lines_tws(self, wick_data, pen):
        """Draw wick lines efficiently using numpy arrays"""
        if not wick_data:
            return

        import numpy as np

        # Combine all wick lines into continuous arrays with NaN separators
        x_data = []
        y_data = []

        for x_coords, y_coords in wick_data:
            x_data.extend(x_coords)
            x_data.append(np.nan)  # Separator to break line segments
            y_data.extend(y_coords)
            y_data.append(np.nan)

        # Remove trailing NaN
        if x_data and np.isnan(x_data[-1]):
            x_data = x_data[:-1]
            y_data = y_data[:-1]

        if x_data and y_data:
            wick_plot = pg.PlotDataItem(
                x=np.array(x_data),
                y=np.array(y_data),
                pen=pen,
                connect='finite'  # Only connect non-NaN values
            )
            self.plot_item.addItem(wick_plot)

    def _draw_doji_lines_tws(self, doji_data, pen):
        """Draw doji lines efficiently"""
        if not doji_data or len(doji_data) < 2:
            return

        import numpy as np

        # Combine all doji lines
        x_data = []
        y_data = []

        for i in range(0, len(doji_data), 2):
            if i + 1 < len(doji_data):
                x_data.extend(doji_data[i])
                x_data.append(np.nan)
                y_data.extend(doji_data[i + 1])
                y_data.append(np.nan)

        # Remove trailing NaN
        if x_data and np.isnan(x_data[-1]):
            x_data = x_data[:-1]
            y_data = y_data[:-1]

        if x_data and y_data:
            doji_plot = pg.PlotDataItem(
                x=np.array(x_data),
                y=np.array(y_data),
                pen=pg.mkPen(pen.color(), width=2),
                connect='finite'
            )
            self.plot_item.addItem(doji_plot)

    def _setup_axis_labels_tws(self, data):
        """Efficiently set up x-axis labels with optimal spacing"""
        if not data:
            return

        # Calculate optimal step size for labels (show ~10-15 labels max)
        step = max(1, len(data) // 12)

        ticks = []
        for i in range(0, len(data), step):
            bar = data[i]
            date_str = bar.date.strip()

            # Remove timezone if present
            if " US/Eastern" in date_str:
                date_str = date_str.replace(" US/Eastern", "")

            try:
                # Try parsing with time first
                dt = datetime.strptime(date_str, "%Y%m%d %H:%M:%S")
                label = dt.strftime("%b %d %H:%M")
            except ValueError:
                try:
                    # Fallback to date only
                    dt = datetime.strptime(date_str, "%Y%m%d")
                    label = dt.strftime("%b %d")
                except ValueError:
                    # If all else fails, use the original string
                    label = date_str

            ticks.append((i, label))

        # Add the last data point if it's not already included
        if len(data) > 1 and (len(data) - 1) % step != 0:
            bar = data[-1]
            date_str = bar.date.strip()
            if " US/Eastern" in date_str:
                date_str = date_str.replace(" US/Eastern", "")

            try:
                dt = datetime.strptime(date_str, "%Y%m%d %H:%M:%S")
                label = dt.strftime("%b %d %H:%M")
            except ValueError:
                try:
                    dt = datetime.strptime(date_str, "%Y%m%d")
                    label = dt.strftime("%b %d")
                except ValueError:
                    label = date_str

            ticks.append((len(data) - 1, label))

        self.market_data_graph.getAxis('bottom').setTicks([ticks])

    def handle_symbol_change_signal(self):
        self.stock_dropdown.setCurrentText(self.app.current_symbol)