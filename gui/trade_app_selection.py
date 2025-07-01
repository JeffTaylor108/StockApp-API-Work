from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QApplication

from gui import styling
from ibapi_connections.app import StockApp


class TradeAppSelectionWidget(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window

        # widgets added to layout
        widget_label = QLabel("Select Trading App")

        # TWS App Selector
        self.tws_button = QPushButton("Interactive Brokers")
        self.tws_button.pressed.connect(self.ibkr_selected)

        # Schwab App Selector
        self.schwab_button = QPushButton("Charles Schwab")
        self.schwab_button.pressed.connect(self.schwab_selected)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(widget_label)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.tws_button)
        buttons_layout.addWidget(self.schwab_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # styling
        widget_label.setFont(styling.heading_font)

    # closes Schwab window and opens IBKR window
    def ibkr_selected(self):
        from gui.main_window import MainWindow # moved inside to prevent circular import

        self.show_window_loading_overlay("Interactive Brokers Trading")
        QApplication.processEvents()

        # connects to TWS API on port 7497 (paper trading)
        self.app = StockApp()
        self.app.connect("127.0.0.1", 7497, 0)

        # starts app
        self.thread = QThread()
        self.app.moveToThread(self.thread)
        self.thread.started.connect(self.app.run)
        self.thread.start()

        # checks if app connected
        print(f"App is connected: {self.app.isConnected()}")

        self.main_window = MainWindow(self.app)
        self.main_window.show()
        self.hide_window_loading_overlay()

        if self.parent_window:
            self.parent_window.close()

    # closes IBKR window and opens Schwab window
    def schwab_selected(self):
        from schwab_gui.schwab_window import MainSchwabWindow # moved inside to prevent circular import

        self.show_window_loading_overlay("Schwab Trading")
        QApplication.processEvents()

        self.main_window = MainSchwabWindow()
        self.main_window.show()
        self.hide_window_loading_overlay()

        if self.parent_window:
            self.parent_window.close()

    # shows loading overlay when switching between TWS and Schwab APIs
    def show_window_loading_overlay(self, window_name):
        overlay = QLabel(f"Loading {window_name} Window...", self.parent_window)
        overlay.setStyleSheet("""
            background-color: rgba(0, 0, 0, 150);
            color: white;
            font-size: 24px;
            padding: 20px;
            border-radius: 10px;
        """)
        overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay.setGeometry(self.parent_window.rect())
        overlay.show()
        self.loading_overlay = overlay

    # hides loading overlay
    def hide_window_loading_overlay(self):
        if hasattr(self, "loading_overlay") and self.loading_overlay:
            self.loading_overlay.hide()
            self.loading_overlay.deleteLater()
            self.loading_overlay = None