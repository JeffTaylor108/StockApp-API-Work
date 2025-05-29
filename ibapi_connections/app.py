from typing import Optional

from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import *
import time
from ibapi.order import *
import threading
from PyQt6.QtCore import pyqtSignal, QObject
import datetime
from dataclasses import dataclass, asdict


# EClient is used to send requests to TWS, EWrapper is used to receive responses from TWS

# class that instantiates EWrapper and EClient
# all methods must be redefined for inheritance in class
class StockApp(EWrapper, EClient, QObject):

    # creates a signal that triggers whenever method.emit() is called
    connected = pyqtSignal()
    stock_prices_updated = pyqtSignal()
    portfolio_prices_updated = pyqtSignal()
    active_orders_updated = pyqtSignal()
    completed_orders_updated = pyqtSignal()
    stock_symbol_changed = pyqtSignal()

    def __init__(self):
        EClient.__init__(self, self)
        QObject.__init__(self)
        self.nextOrderId = None
        self.nextReqId = 1

        # currently selected stock
        self.current_symbol = 'AAPL'

        # variables for stock data
        self.market_data = MarketData(
            req_id=None,
            bid=None,
            ask=None,
            last=None,
            open=None,
            close=None,
            high=None,
            low=None,
            volume=None
        )

        # mapping from req id to event
        self.id_to_event ={}

        # variables for news data
        self.find_articles_event = threading.Event()
        self.articles_found = []

        self.find_article_text_event = threading.Event()
        self.selected_article_text = ""

        # threading events for buying a stock
        self.find_matching_contract_event = threading.Event()
        self.matching_contract = None

        # variables for positions of account
        self.find_portfolio_event = threading.Event()
        self.req_id_to_portfolio_symbol = {}
        self.portfolio_dict = {} # dictionary that matches stock symbol to position
        self.portfolio_list =[]

        # variables for market data graphs
        self.find_market_data_bars_event = threading.Event()
        self.market_data_bars = []

        # variables for order activity
        self.find_completed_orders_event = threading.Event()
        self.find_active_orders_event = threading.Event()
        self.completed_orders = []
        self.active_orders = {}


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

    # defines response for reqPositions
    def position(self, account, contract, position, avgCost):
        # print(f"Positions: Account: {account} Contract: {contract} Position: {position} Avg cost: {avgCost}")

        portfolio_obj = Portfolio(
            contract = contract,
            position = float(position),
            avg_cost = avgCost,
            last = -1,
            close = -1
        )

        self.portfolio_dict[contract.symbol] = portfolio_obj
        self.portfolio_list.append(portfolio_obj)

    def positionEnd(self):
        self.find_portfolio_event.set()
        print("Ended positions request")

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

        if reqId in self.req_id_to_portfolio_symbol:

            # finds associated symbol in portfolio from req_id
            symbol = self.req_id_to_portfolio_symbol.get(reqId)

            if tickType == 68:
                self.portfolio_dict.get(symbol).last = price
                print(f"Last bid price for {symbol} changed to ", price)

            elif tickType == 75:
                self.portfolio_dict.get(symbol).close = price
                print(f"Close price for {symbol} changed to ", price)

            if self.portfolio_dict.get(symbol).last != -1 and self.portfolio_dict.get(symbol).close != -1:
                event = self.id_to_event.get(reqId)
                if event and not event.is_set():
                    event.set()
                self.portfolio_prices_updated.emit()

        else:
            if tickType == 66:
                self.market_data.bid = price
                print(f"Bid price: {price}")

            elif tickType == 67:
                self.market_data.ask = price
                print(f"Ask price: {price}")

            elif tickType == 68:
                self.market_data.last = price
                print(f"Last traded price: {price}")

            elif tickType == 72:
                self.market_data.high = price
                print(f"High price: {price}")

            elif tickType == 73:
                self.market_data.low = price
                print(f"Low traded price: {price}")

            elif tickType == 75:
                self.market_data.close = price
                print(f"Closing price: {price}")

            elif tickType == 76:
                self.market_data.open = price
                print(f"Opening price: {price}")

            # emits signal to trigger an event
            self.check_and_emit_complete_data()

            # commented out for refactoring
            # print(f"Tick Price: reqId: {reqId}, tickType: {tickType}, price: {price}, attrib: {attrib}")

    # same as tickPrice
    def tickSize(self, reqId, tickType, size):

        if tickType == 74:
            self.market_data.volume = size
            print(f"Trading volume for day: {size}")

        self.check_and_emit_complete_data()

        # commented out for refactoring
        # print(f"Tick Size: reqId: {reqId}, tickType: {tickType}, size: {size}")

    def cancelMktData(self, reqId):
        print(f"Market data for request {reqId} cancelled successfully")

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

        self.active_orders[orderId] = ActiveOrders (
            order_id = orderId,
            symbol = contract.symbol,
            status = orderState.status,
            action = order.action,
            type = order.orderType,
            quantity = order.totalQuantity,
            fill_price = order.lmtPrice
        )

        self.active_orders_updated.emit()

        print(f"Open orders: orderId: {orderId}, contract: {contract}, order: {order}, order state: {orderState}")

    def openOrderEnd(self):
        self.find_active_orders_event.set()
        print("All open orders received")

    # responds with details on order whenever the status of an order changes
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):

        # when an order is cancelled, moves it from active dictionary to completed list
        print("Status: ", {status})
        if status == "Cancelled":
            order = self.active_orders.get(orderId)
            self.active_orders.pop(orderId)
            self.completed_orders.append(order)
            self.active_orders_updated.emit()
            print(f"Order {orderId} cancelled")

        print(f"Order Status: orderId: {orderId}, status: {status}, filled: {filled}, remaining: {remaining}, avgFillPrice: {avgFillPrice}, and more not printed")

    # response with details on all completed orders
    def completedOrder(self, contract: Contract, order: Order, orderState: OrderState):

        self.completed_orders.append(CompletedOrders (
            order_id = order.orderId,
            symbol = contract.symbol,
            status = orderState.status,
            action = order.action,
            type = order.orderType,
            quantity = order.totalQuantity,
            fill_price = order.lmtPrice
        ))

        print(f"Completed Orders: contract: {contract}, order: {order}, order state: {orderState}")

    def completedOrdersEnd(self):
        self.find_completed_orders_event.set()
        print("All completed orders received")

    # responds with details on order when executed
    def execDetailsEnd(self, reqId, contract, execution):
        print(f"Exec details: reqId: {reqId}, contract: {contract}, execution: {execution}")


#--------------------------------Historical Data Graphs Endpoint--------------------------------------------------------------------

    # responds with historical bar data of contract
    def historicalData(self, reqId, bar: BarData):
        print(f"Historical bar data: Req Id: {reqId}, Bar Data: {bar}")
        self.market_data_bars.append(bar)

    def historicalDataEnd(self, reqId, start, end):
        self.find_market_data_bars_event.set()
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

# ------------------------------End of EWrapper/EClient definitions----------------------------------------------------

    # helper method for tickPrice and tickSize event threading
    def check_and_emit_complete_data(self):
        data_dict = asdict(self.market_data)

        # Define what counts as "unfilled" – here we assume None or 0 is unfilled
        all_filled = all(
            value is not None for key, value in data_dict.items() if key != 'req_id'
        )

        if all_filled:
            event = self.id_to_event.get(self.market_data.req_id)
            if event and not event.is_set():
                event.set()
            self.stock_prices_updated.emit()

    # helper method for handling universal symbol changes
    def check_current_symbol(self, new_symbol):
        if self.current_symbol != new_symbol:
            self.current_symbol = new_symbol
            self.stock_symbol_changed.emit()


# data objects
@dataclass
class NewsArticle:
    date: str
    headline: str
    article_id: str

@dataclass
class Portfolio:
    contract: Contract
    position: float
    avg_cost: float
    last: Optional[float]
    close: Optional[float]

@dataclass
class MarketData:
    req_id: int
    bid: Optional[float]
    ask: Optional[float]
    last: Optional[float]
    high: Optional[float]
    low: Optional[float]
    open: Optional[float]
    close: Optional[float]
    volume: Optional[float]

@dataclass
class ActiveOrders:
    order_id: int
    status: str
    symbol: str
    action: str
    type: str
    quantity: int
    fill_price: float

@dataclass
class CompletedOrders:
    order_id: int
    status: str
    symbol: str
    action: str
    type: str
    quantity: int
    fill_price: float