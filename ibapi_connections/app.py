from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import *
import time
from ibapi.order import *
import threading
from PyQt6.QtCore import pyqtSignal, QObject
import datetime
from dataclasses import dataclass


# EClient is used to send requests to TWS, EWrapper is used to receive responses from TWS

# class that instantiates EWrapper and EClient
# all methods must be redefined for inheritance in class
class StockApp(EWrapper, EClient, QObject):

    # creates a signal that triggers whenever method.emit() is called
    connected = pyqtSignal()
    stock_prices_updated = pyqtSignal()

    def __init__(self):
        EClient.__init__(self, self)
        QObject.__init__(self)
        self.nextOrderId = None
        self.nextReqId = 1

        # variables for stock data
        self.bid_price = None
        self.ask_price = None
        self.last_traded_price = None
        self.high_price = None
        self.low_price = None
        self.open_price = None
        self.close_price = None

        # variables for news data
        self.find_articles_event = threading.Event()
        self.articles_found = []

        self.find_article_text_event = threading.Event()
        self.selected_article_text = ""

        # threading events for buying a stock
        self.find_matching_contract_event = threading.Event()
        self.matching_contract = None

        # threading events for getting volume of stock
        self.trading_volume = None

        # variables for news data



    # generates reqIds for internal use
    def getNextReqId(self):
        reqId = self.nextReqId
        self.nextReqId += 1
        return reqId

    # generates next valid id for orders through app.reqIds and sets nextOrderId to it
    def nextValidId(self, orderId):
        self.nextOrderId = orderId
        self.connected.emit()
        self.reqIds(-1)

    # -------------------------------------Account Endpoint------------------------------------------------------------

    # defines response for reqAccountSummary
    def accountSummary(self, reqId, account, tag, value,
                       currency:str):
        print(f"Account Summary: reqId: {reqId}, account: {account}, tag: {tag}, value: {value}, currency: {currency}")

    def accountSummaryEnd(self, reqId):
        print(f"All Account Summary data received for reqId: {reqId}")

    # -----------------------------------Contract Data Endpoint---------------------------------------------------------------

    # defines response for reqMatchingSymbols
    def symbolSamples(self, reqId, contractDescriptions):

        # extracts Contract object from contractDescriptions
        con = contractDescriptions[0].contract

        if con:
            self.matching_contract = con
            self.find_matching_contract_event.set()
        else:
            print("No matching contracts found")
            self.find_matching_contract_event.set()

        stock_details_string = (f"conId: {con.conId}, secType: {con.secType} symbol: {con.symbol}, "
                                f"exchange: {con.exchange}, primary exchange: {con.primaryExchange}, "
                                f"currency: {con.currency}, description: {con.description}")

        print(f"Stock Symbol details: reqId: {reqId}, stock details: {stock_details_string}")


    # defines response for reqContractDetails
    def contractDetails(self, reqId, contractDetails):

        # see documentation for what properties contractDetails can display
        print(f"Contract Details: reqId: {reqId}, contract details: {contractDetails}")

        # contractDetails displays contract data through contractDetails.contract.symbol
        print(f"contract symbol: {contractDetails.contract.symbol}")

    def contractDetailsEnd(self, reqId):
        print("All Contract Details received for reqId:", reqId)

    # -----------------------------------Market Data Endpoint-------------------------------------------------------------------

    # defines response for reqMarketDataType
    def marketDataType(self, reqId, marketDataType):
        print(f"Market Data Type: {marketDataType}")

    # defines response for tick price values (to print specific data, use 'if tickType == ...' statements and refer to docs)
    # tickList docs: https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/#available-tick-types
    def tickPrice(self, reqId, tickType, price, attrib):

        if tickType == 66:
            self.bid_price = price
            print(f"Bid price: {price}")

        elif tickType == 67:
            self.ask_price = price
            print(f"Ask price: {price}")

        elif tickType == 68:
            self.last_traded_price = price
            print(f"Last traded price: {price}")

        elif tickType == 72:
            self.high_price = price
            print(f"High price: {price}")

        elif tickType == 73:
            self.low_price = price
            print(f"Low traded price: {price}")

        elif tickType == 75:
            self.close_price = price
            print(f"Closing price: {price}")

        elif tickType == 76:
            self.open_price = price
            print(f"Opening price: {price}")

        # emits signal to trigger an event
        self.stock_prices_updated.emit()

        # commented out for refactoring
        # print(f"Tick Price: reqId: {reqId}, tickType: {tickType}, price: {price}, attrib: {attrib}")

    # same as tickPrice
    def tickSize(self, reqId, tickType, size):

        if tickType == 74:
            self.trading_volume = size
            print(f"Trading volume for day: {size}")

        # commented out for refactoring
        # print(f"Tick Size: reqId: {reqId}, tickType: {tickType}, size: {size}")

    #--------------------------------News Endpoint--------------------------------------------------------------------

    # defines response for reqNewsProviders, which returns an array of news providers
    def newsProviders(self, newsProviders):
        print(f"News Providers available: {newsProviders}")

        # access the provider codes for each news provider
        provider_codes = []
        for providers in newsProviders:
            provider_codes.append(providers.code)
        print(provider_codes)

    # defines response for reqHistoricalNews
    def historicalNews(self, reqId, time, providerCode, articleId, headline):
        # print(f"Historical news: reqId: {reqId}, time: {time}, providerCode: {providerCode}, articleId: {articleId}, headline: {headline}")
        article_obj = NewsArticle(
            date = time,
            headline = headline,
            article_id = articleId
        )
        self.articles_found.append(article_obj)
        self.find_articles_event.set()

    def historicalDataEnd(self, reqId, hasMore):
        print("All historical news displayed for: ", reqId, "More data to display:", hasMore)

    # defines response for reqNewsArticle (note: article text returns html as a single line)
    def newsArticle(self, reqId, articleType, articleText):
        self.selected_article_text = articleText
        self.find_article_text_event.set()
        print(f"News Article: reqId: {reqId}, articleType: {articleType}, article text: {articleText}")

#--------------------------------Orders Endpoint--------------------------------------------------------------------

    # responds with details on order whenever an order is placed
    def openOrder(self, orderId, contract, order, orderState):
        print(f"Open orders: orderId: {orderId}, contract: {contract}, order: {order}, order state: {orderState}")

    # responds with details on order whenever the status of an order changes
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        print(f"Order Status: orderId: {orderId}, status: {status}, filled: {filled}, remaining: {remaining}, avgFillPrice: {avgFillPrice}, and more not printed")

    # responds with details on order when executed
    def execDetailsEnd(self, reqId, contract, execution):
        print(f"Exec details: reqId: {reqId}, contract: {contract}, execution: {execution}")

# ------------------------------End of EWrapper/EClient definitions----------------------------------------------------

# news article object
@dataclass
class NewsArticle:
    date: str
    headline: str
    article_id: str