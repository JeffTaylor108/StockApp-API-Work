from datetime import datetime

import numpy as np
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox
import pyqtgraph as pg
from pyqtgraph import PlotItem, PlotWidget, BarGraphItem, mkPen
from PyQt6.QtCore import Qt

from gui import styling
from mongodb_connection.order_entries import fetch_order_entries
from schwab_connections.schwab_market_data import SchwabMarketData


class SchwabPriceHistoryGraphWidget(QWidget):

    def __init__(self, mongo_client):
        super().__init__()
        self.mongo_client = mongo_client

        self.market_data_controller = SchwabMarketData()

        # widget label
        widget_label = QLabel("Price History Graph")

        # symbol input
        self.symbol_input = QLineEdit('AAPL')
        self.find_symbol_button = QPushButton("Create Graph")
        self.find_symbol_button.clicked.connect(self.get_price_history)

        # period of data input
        self.period_dropdown = QComboBox()
        self.period_dropdown.addItems(["10 days", "5 days", "3 days", "1 day"])

        # frequency of candles input
        self.candle_frequency_dropdown = QComboBox()
        self.candle_frequency_dropdown.addItems(["30 minutes", "15 minutes", "5 minutes", "1 minute"])

        # container for query params
        search_query_params = QHBoxLayout()
        search_query_params.addWidget(self.symbol_input)
        search_query_params.addWidget(self.period_dropdown)
        search_query_params.addWidget(self.candle_frequency_dropdown)

        # graph widget
        self.price_history_graph = PlotWidget()
        self.price_history_graph.showGrid(x=True, y=True)
        self.price_history_graph.setBackground("w")
        self.price_history_graph.setLabel('left', 'Price ($)')
        self.price_history_graph.setLabel('bottom', 'Time')

        # layout
        layout = QVBoxLayout()
        layout.addWidget(widget_label)
        layout.addLayout(search_query_params)
        layout.addWidget(self.find_symbol_button)
        layout.addWidget(self.price_history_graph)

        self.setLayout(layout)

        # styling
        widget_label.setFont(styling.heading_font)

    # gets price history data for symbol input
    def get_price_history(self):

        symbol = self.symbol_input.text()
        period = self.period_dropdown.currentText()
        frequency = self.candle_frequency_dropdown.currentText()

        try:
            candles = self.market_data_controller.fetch_price_history(symbol, period, frequency)
            print(candles)
            self.construct_graph(candles)

        except Exception as e:
            print(f"Error fetching price history: {e}")

    # creates graph (used Claude to help generate + optimize)
    def construct_graph(self, candles):
        try:
            self.price_history_graph.clear()

            if not candles:
                print("No candles to plot")
                return

            # Process and validate candle data
            processed_candles = []
            x_labels = []

            for i, candle in enumerate(candles):
                required_keys = ["open", "close", "high", "low", "datetime"]
                if not all(key in candle for key in required_keys):
                    continue

                try:
                    open_price = float(candle["open"])
                    close_price = float(candle["close"])
                    high_price = float(candle["high"])
                    low_price = float(candle["low"])

                    timestamp = candle["datetime"]
                    if timestamp > 1e12:
                        dt = datetime.fromtimestamp(timestamp / 1000)
                    else:
                        dt = datetime.fromtimestamp(timestamp)

                    processed_candles.append({
                        'x': i,
                        'open': open_price,
                        'close': close_price,
                        'high': high_price,
                        'low': low_price,
                        'datetime': dt
                    })

                    x_labels.append((i, dt.strftime("%H:%M")))

                except (ValueError, TypeError, OSError) as e:
                    print(f"Error processing candle {i}: {e}")
                    continue

            if not processed_candles:
                print("No valid candle data to plot")
                return

            # Create optimized candlestick chart
            self.create_optimized_candlesticks_v2(processed_candles)

            # Set up x-axis labels
            if x_labels:
                step = max(1, len(x_labels) // 10)
                filtered_labels = [x_labels[i] for i in range(0, len(x_labels), step)]

                axis = self.price_history_graph.getAxis('bottom')
                axis.setTicks([filtered_labels])

                self.price_history_graph.setRange(
                    xRange=[-1, len(processed_candles)],
                    padding=0.1
                )

            self.price_history_graph.setMouseEnabled(x=True, y=True)
            self.add_position_indicators()
            print(f"Successfully plotted {len(processed_candles)} candles")

        except Exception as e:
            print(f"Error in construct_graph: {e}")
            import traceback
            traceback.print_exc()

    def create_optimized_candlesticks_v2(self, candles):
        """Highly optimized candlestick chart using batched drawing operations"""

        if not candles:
            return

        candle_width = 0.6

        # Separate bullish and bearish candles for batch processing
        bullish_bodies = []
        bearish_bodies = []
        bullish_wicks_upper = []
        bullish_wicks_lower = []
        bearish_wicks_upper = []
        bearish_wicks_lower = []
        doji_lines = []

        # Colors
        bullish_body_color = (34, 139, 34, 200)
        bullish_outline_color = (0, 100, 0, 255)
        bearish_body_color = (220, 20, 60, 200)
        bearish_outline_color = (139, 0, 0, 255)

        # Process all candles and group by type
        for candle in candles:
            x = candle['x']
            open_price = candle['open']
            close_price = candle['close']
            high_price = candle['high']
            low_price = candle['low']

            is_bullish = close_price >= open_price
            body_top = max(open_price, close_price)
            body_bottom = min(open_price, close_price)
            body_height = body_top - body_bottom

            # Group candle bodies
            if body_height > 0:
                if is_bullish:
                    bullish_bodies.append({
                        'x': x, 'height': body_height, 'y0': body_bottom
                    })
                else:
                    bearish_bodies.append({
                        'x': x, 'height': body_height, 'y0': body_bottom
                    })
            else:
                # Doji candle
                doji_lines.extend([
                    [x - candle_width / 2, x + candle_width / 2],
                    [open_price, open_price]
                ])

            # Group wicks
            if high_price > body_top:
                wick_data = ([x, x], [body_top, high_price])
                if is_bullish:
                    bullish_wicks_upper.append(wick_data)
                else:
                    bearish_wicks_upper.append(wick_data)

            if low_price < body_bottom:
                wick_data = ([x, x], [low_price, body_bottom])
                if is_bullish:
                    bullish_wicks_lower.append(wick_data)
                else:
                    bearish_wicks_lower.append(wick_data)

        # Draw bullish candles in batches
        if bullish_bodies:
            self._draw_candle_bodies(bullish_bodies, bullish_body_color, bullish_outline_color, candle_width)

        if bearish_bodies:
            self._draw_candle_bodies(bearish_bodies, bearish_body_color, bearish_outline_color, candle_width)

        # Draw wicks in batches
        self._draw_wick_lines(bullish_wicks_upper + bullish_wicks_lower, bullish_outline_color)
        self._draw_wick_lines(bearish_wicks_upper + bearish_wicks_lower, bearish_outline_color)

        # Draw doji lines
        if doji_lines:
            self._draw_doji_lines(doji_lines, bullish_outline_color)

    def _draw_candle_bodies(self, bodies, fill_color, outline_color, width):
        """Draw candle bodies efficiently using BarGraphItem"""
        if not bodies:
            return

        x_vals = [body['x'] for body in bodies]
        heights = [body['height'] for body in bodies]
        y0_vals = [body['y0'] for body in bodies]

        # Create single BarGraphItem for all bodies of the same type
        bars = BarGraphItem(
            x=x_vals,
            height=heights,
            width=width,
            y0=y0_vals,
            brush=fill_color,
            pen=pg.mkPen(outline_color, width=1)
        )
        self.price_history_graph.addItem(bars)

    def _draw_wick_lines(self, wick_data, color):
        """Draw wick lines efficiently using numpy arrays"""
        if not wick_data:
            return

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
                pen=pg.mkPen(color, width=1),
                connect='finite'  # Only connect non-NaN values
            )
            self.price_history_graph.addItem(wick_plot)

    def _draw_doji_lines(self, doji_data, color):
        """Draw doji lines efficiently"""
        if not doji_data or len(doji_data) < 2:
            return

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
                pen=pg.mkPen(color, width=2),
                connect='finite'
            )
            self.price_history_graph.addItem(doji_plot)

    # adds indicator to graph where user has bought/sold a position
    def add_position_indicators(self):

        # fetches order history
        prev_orders = fetch_order_entries(self.mongo_client)
        if not prev_orders:
            print("No orders to display indicators for")
            return

        for order in prev_orders:
            price = order['individual_price']

            # draws green line across y-axis at price where buy order occurred
            if order['action'] == 'BUY':
                line = pg.InfiniteLine(
                    pos=price,
                    angle=0,
                    pen=pg.mkPen(color=(0, 255, 0), width=2, style=Qt.PenStyle.DashLine),
                    label='BUY: ${:.2f}'.format(price),
                    labelOpts={'position': 0.90, 'color': (0, 200, 0)}
                )
                self.price_history_graph.addItem(line)
            # draws red line across y-axis at price where sell order occurred
            elif order['action'] == 'SELL':
                line = pg.InfiniteLine(
                    pos=price,
                    angle=0,
                    pen=pg.mkPen(color=(255, 0, 0), width=2, style=Qt.PenStyle.DashLine),
                    label='SELL: ${:.2f}'.format(price),
                    labelOpts={'position': 0.90, 'color': (200, 0, 0)}
                )
                self.price_history_graph.addItem(line)
