import json

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit

from schwab_connections.market_data import get_quotes
from schwab_connections.schwab_auth import get_auth_url, authorize


class MainSchwabWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Charles Schwab API Trading GUI")

        # widgets to be added to layout

        # auth link to click
        auth_label = QLabel("Authorize account before proceeding by clicking this link: ")
        auth_url = get_auth_url()
        print(auth_url)
        auth_link = QLabel(f'<a href="{auth_url}">Click here to authorize</a>')
        auth_link.setOpenExternalLinks(True)
        auth_link.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)

        # input for broken url
        returned_link_label = QLabel("Enter the url of where Schwab redirects you after authorizing (it will show a broken page)")
        self.returned_link_input = QLineEdit()
        submit_link = QPushButton("Complete Authorization")
        submit_link.clicked.connect(self.submit_authorize)

        # stock symbol for quote retrieval
        quote_label = QLabel("Input stock symbol to see its quote data")
        self.symbol_input = QLineEdit()
        submit_symbol_button = QPushButton("Retrieve Quotes")
        submit_symbol_button.clicked.connect(self.confirm_get_quotes)

        # quote data display
        self.quote_data_display = QTextEdit()
        self.quote_data_display.setReadOnly(True)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(auth_label)
        layout.addWidget(auth_link)
        layout.addWidget(returned_link_label)
        layout.addWidget(self.returned_link_input)
        layout.addWidget(submit_link)
        layout.addWidget(quote_label)
        layout.addWidget(self.symbol_input)
        layout.addWidget(submit_symbol_button)
        layout.addWidget(self.quote_data_display)

        container = QWidget()
        container.setLayout(layout)

        # sets window to display container
        self.setCentralWidget(container)


    def submit_authorize(self):
        link = self.returned_link_input.text()
        authorize(link)

    def confirm_get_quotes(self):
        symbol = self.symbol_input.text()
        quote_data = get_quotes(symbol)

        quote_data_str = json.dumps(quote_data, indent=4)
        self.quote_data_display.setText(quote_data_str)