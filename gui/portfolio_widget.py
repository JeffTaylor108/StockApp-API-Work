from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem

from gui import styling
from ibapi_connections.account_data import currently_held_positions, get_available_funds, get_pnl
from ibapi_connections.market_data import get_portfolio_price_stream


class PortfolioWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        # widgets added to layout
        widget_label = QLabel("Portfolio")

        # available funds
        available_funds_label = QLabel("Available funds: ")
        self.available_funds = QLabel(f"${self.app.available_funds}")
        self.app.available_funds_updated.connect(self.update_available_funds) # triggers when signal received from IB

        # realized and unrealized P&L
        pnl_label = QLabel("P&L")
        self.daily_pnl = QLabel("Daily: ")
        self.realized_pnl = QLabel("Realized: ")
        self.unrealized_pnl = QLabel("Unrealized: ")
        self.app.pnl_updated.connect(self.update_pnl)

        # table for portfolio_dict data
        self.portfolio_table = QTableWidget()
        self.portfolio_table.setColumnCount(6)
        self.portfolio_table.setHorizontalHeaderLabels(["Ticker Symbol", "Positions", "Mkt Value", "AVG Price", "Last", "Change"])
        self.app.portfolio_prices_updated.connect(self.update_position_prices) # triggers when signal received from IB

        # layout
        layout = QVBoxLayout()
        layout.addWidget(widget_label)
        layout.addWidget(available_funds_label)
        layout.addWidget(self.available_funds)
        layout.addWidget(pnl_label)
        layout.addWidget(self.daily_pnl)
        layout.addWidget(self.realized_pnl)
        layout.addWidget(self.unrealized_pnl)
        layout.addWidget(self.portfolio_table)

        self.setLayout(layout)

        # fonts/styling
        widget_label.setFont(styling.heading_font)
        available_funds_label.setFont(styling.heading_font)
        pnl_label.setFont(styling.heading_font)

        self.get_portfolio()
        get_available_funds(self.app)
        get_pnl(self.app)


    def get_portfolio(self):

        currently_held_positions(self.app)

        for position in self.app.portfolio_dict.values():

            get_portfolio_price_stream(self.app, position.contract)

            row_position = self.portfolio_table.rowCount()
            self.portfolio_table.insertRow(row_position)

            self.portfolio_table.setItem(row_position, 0, QTableWidgetItem(position.contract.symbol))
            self.portfolio_table.setItem(row_position, 1, QTableWidgetItem(f"{position.position}"))
            self.portfolio_table.setItem(row_position, 2, QTableWidgetItem(f"{position.last * position.position}"))
            self.portfolio_table.setItem(row_position, 3, QTableWidgetItem(f"{position.avg_cost:.2f}"))
            self.portfolio_table.setItem(row_position, 4, QTableWidgetItem(f"{position.last}"))
            self.portfolio_table.setItem(row_position, 5, QTableWidgetItem(f"{(position.last - position.close):.2f}"))


    # updates position price and change values
    def update_position_prices(self):
        row_count = self.portfolio_table.rowCount()

        for row in range(row_count):
            symbol = self.portfolio_table.item(row, 0).text()
            position = self.app.portfolio_dict.get(symbol)

            self.portfolio_table.setItem(row, 1, QTableWidgetItem(f"{position.position}"))
            self.portfolio_table.setItem(row, 2, QTableWidgetItem(f"{position.last * position.position}"))
            self.portfolio_table.setItem(row, 3, QTableWidgetItem(f"{position.avg_cost:.2f}"))
            self.portfolio_table.setItem(row, 4, QTableWidgetItem(f"{position.last}"))
            self.portfolio_table.setItem(row, 5, QTableWidgetItem(f"{(position.last - position.close):.2f}"))

    # updates available funds
    def update_available_funds(self):
        self.available_funds.setText(f"${self.app.available_funds}")

    # updates P&L
    def update_pnl(self):
        self.daily_pnl.setText(f"Daily: ${self.app.daily_pnl:,.2f}")
        self.realized_pnl.setText(f"Realized: $ {self.app.realized_pnl:,.2f}")
        self.unrealized_pnl.setText(f"Unrealized: ${self.app.unrealized_pnl:,.2f}")