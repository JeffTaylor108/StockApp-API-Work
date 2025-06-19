import re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QTabWidget, QTextEdit, QListWidget, QLineEdit, QHBoxLayout, \
    QPushButton, QListWidgetItem, QDialog
from ibapi.contract import Contract

from gui import styling
from ibapi_connections.account_data import currently_held_positions, get_position_symbols
from ibapi_connections.contract_data import req_contract_from_symbol
from ibapi_connections.news import get_news_headlines, get_news_article_from_id


class StockNewsWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        # widgets added to layout
        widget_label = QLabel("See Live Market News")

        # finds news by stock ticker
        search_bar_layout = QHBoxLayout()

        # symbol input
        symbol_search_label = QLabel("Search for News by Stock Symbol")
        self.symbol_search = QLineEdit()
        self.symbol_search.setPlaceholderText("Enter stock symbol")
        self.symbol_search.returnPressed.connect(self.get_stock_news)

        # search button
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.get_stock_news)

        # sets search layout
        search_bar_layout.addWidget(self.symbol_search)
        search_bar_layout.addWidget(search_button)

        # portfolio_dict news button
        portfolio_news_button = QPushButton("View Portfolio News")
        portfolio_news_button.clicked.connect(self.get_portfolio_news)

        # stock news display
        self.news_display_label = QLabel("News Based on Portfolio:")
        self.news_display = QListWidget()
        self.news_display.itemDoubleClicked.connect(self.on_headline_clicked)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(widget_label)
        layout.addWidget(symbol_search_label)
        layout.addLayout(search_bar_layout)
        layout.addWidget(portfolio_news_button)
        layout.addWidget(self.news_display_label)
        layout.addWidget(self.news_display)

        self.setLayout(layout)

        self.get_portfolio_news()

        # fonts/styling
        widget_label.setFont(styling.heading_font)

    def get_stock_news(self):
        symbol = self.symbol_search.text()
        contract:Contract = req_contract_from_symbol(self.app, symbol)
        headlines = get_news_headlines(self.app, contract)

        self.news_display.clear()
        self.news_display_label.setText("News Based on Symbol Search:")
        for article in headlines:

            cleaned_headline = re.sub(r"^\{.*?\}", "", article.headline).strip()
            cleaned_date = article.date[:10]

            # allows for me to store both text and article object inside each item
            item = QListWidgetItem(f"{cleaned_date}: {cleaned_headline}")
            item.setData(Qt.ItemDataRole.UserRole, article)
            self.news_display.addItem(item)

    def on_headline_clicked(self, headline):
        article_id = headline.data(Qt.ItemDataRole.UserRole).article_id
        print("article id: " + article_id)
        article_text = get_news_article_from_id(self.app, article_id)

        print("from headline click:" + article_text)

        dialog = ArticleDialog(article_text)
        dialog.setMinimumSize(800, 600)
        dialog.exec()

    def get_portfolio_news(self):
        account_portfolio = get_position_symbols(self.app)
        self.news_display.clear()

        for symbol in account_portfolio:
            contract: Contract = req_contract_from_symbol(self.app, symbol)
            headlines = get_news_headlines(self.app, contract)

            for article in headlines:
                cleaned_headline = re.sub(r"^\{.*?\}", "", article.headline).strip()
                cleaned_date = article.date[:10]

                # allows for me to store both text and article object inside each item
                item = QListWidgetItem(f"{cleaned_date}: {cleaned_headline}")
                item.setData(Qt.ItemDataRole.UserRole, article)
                self.news_display.addItem(item)



class ArticleDialog(QDialog):
    def __init__(self, article_text):
        super().__init__()

        self.setWindowTitle("News Article Selected")

        article_view = QTextEdit()
        article_view.setReadOnly(True)
        print("from dialog box" + article_text)
        article_view.setHtml(article_text)

        layout = QVBoxLayout()
        layout.addWidget(article_view)

        self.setLayout(layout)