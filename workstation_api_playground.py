from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import *
import time
from ibapi.order import *
import threading


# EClient is used to send requests to TWS, EWrapper is used to receive responses from TWS

# class that instantiates EWrapper and EClient
# all methods must be redefined for inheritance in class
class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextOrderId = None

    # generates reqIds for internal use
    nextReqId = 1

    def getNextReqId(self):
        reqId = self.nextReqId
        self.nextReqId += 1
        return reqId

    # generates next valid id for orders through app.reqIds and sets nextOrderId to it
    def nextValidId(self, orderId):
        self.nextOrderId = orderId

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
        con = (contractDescriptions[0].contract)
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

    # defines response for tick price values (to print specific data, us 'if tickType == ...' statements and refer to docs)
    # tickList docs: https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/#available-tick-types
    def tickPrice(self, reqId, tickType, price, attrib):
        print(f"Tick Price: reqId: {reqId}, tickType: {tickType}, price: {price}, attrib: {attrib}")

    # same as tickPrice
    def tickSize(self, reqId, tickType, size):
        print(f"Tick Size: reqId: {reqId}, tickType: {tickType}, size: {size}")

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
        print(f"Historical news: reqId: {reqId}, time: {time}, providerCode: {providerCode}, articleId: {articleId}, headline: {headline}")

    def historicalDataEnd(self, reqId, hasMore):
        print("All historical news displayed for: ", reqId, "More data to display:", hasMore)

    # defines response for reqNewsArticle (note: article text returns html as a single line)
    def newsArticle(self, reqId, articleType, articleText):
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


# AAPL Contract object for testing
contract =  Contract()
contract.conId = 265598
contract.symbol = "AAPL"
contract.secType = "STK"
contract.exchange = "NASDAQ"
contract.currency = "USD"

# testing interactions with account summary
def account_summary_testing():

    # 9001 is reqId for own account
    app.reqAccountSummary(app.getNextReqId(), "All", "NetLiquidation")

    # if multiple tags are provided, each value will be returned in a separate response
    app.reqAccountSummary(app.getNextReqId(), "All", "AccountType, AvailableFunds")

# testing interactions with contract data
def contract_data_testing():

    # requests Contract objects that match the symbol input in console
    symbol_input = input("Enter the symbol you would like to get info on: ")
    app.reqMatchingSymbols(app.getNextReqId(), symbol_input)

    # Contract objects must be instantiated in code to be used in API methods
    app.reqContractDetails(app.getNextReqId(), contract)

# testing interactions with market data
def market_data_testing():
    app.reqMarketDataType(3)

    # procedurally retrieves data for every tickType in genericTickList
    app.reqMktData(app.getNextReqId(), contract, "", False, False, [])

# testing interactions with news data
def news_data_testing():

    # requests news providers user is subscribed to
    app.reqNewsProviders()

    # requests contract specific news
    app.reqHistoricalNews(app.getNextReqId(), contract.conId, "BRFG", "2025-5-10", "", 10, [])

    # requests specific news article
    app.reqNewsArticle(app.getNextReqId(), "BRFG", 'BRFG$1add90db', [])

# testing interactions with buying/selling stocks
def buy_order_testing():

    while app.nextOrderId is None:
        time.sleep(0.1)  # wait for nextValidId to be called

    # constructs minimum necessary fields for Order object
    order = Order()
    order.orderId = app.nextOrderId # IMPORTANT: use nextOrderId for orders
    order.action = "BUY"
    order.orderType = "MKT" # specifies as market order
    order.totalQuantity = 1

    app.placeOrder(app.nextOrderId, contract, order)

def sell_order_testing():

    while app.nextOrderId is None:
        time.sleep(0.1)  # wait for nextValidId to be called

    # constructs minimum necessary fields for Order object
    order = Order()
    order.orderId = app.nextOrderId # IMPORTANT: use nextOrderId for orders
    order.action = "SELL"
    order.tif = "GTC"
    order.orderType = "LMT" # specifies as limit order (order will execute when limit is hit)
    order.lmtPrice = 144.80
    order.totalQuantity = 1

    app.placeOrder(app.nextOrderId, contract, order)

# connects to TWS API on port 7497 (paper trading)
app = TestApp()
app.connect("127.0.0.1", 7497, 0)
time.sleep(1)

# starts app
api_thread = threading.Thread(target=app.run)
api_thread.start()

# checks if app connected
print(app.isConnected())

#---------------------------Testing Functions-------------------------------------------------------------------------

# calls nextValidId
app.reqIds(-1)

# account_summary_testing()
# contract_data_testing()
# market_data_testing()
# news_data_testing()
buy_order_testing()
# sell_order_testing()

