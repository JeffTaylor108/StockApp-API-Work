import time
from ibapi.order import *
from ibapi.contract import *

from contract_data import req_contract_from_symbol
from market_data import get_live_price, stop_mkt_data_stream


# testing interactions with buying/selling stocks
def buy_order_testing(app, contract):

    while app.nextOrderId is None:
        time.sleep(0.1)  # wait for nextValidId to be called

    # constructs minimum necessary fields for Order object
    order = Order()
    order.orderId = app.nextOrderId # IMPORTANT: use nextOrderId for orders
    order.action = "BUY"
    order.orderType = "MKT" # specifies as market order
    order.totalQuantity = 1

    app.placeOrder(app.nextOrderId, contract, order)

def sell_order_testing(app, contract):

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

# method for buying a stock
# flow: input stock symbol, see current price, confirm/deny purchase
def buy_stock(app):

    contract = req_contract_from_symbol(app)
    print(contract)

    get_live_price(app, contract)
    time.sleep(1)
    stop_mkt_data_stream(app, app.nextReqId - 1)

    response = input(f"The latest bid price was: {app.latest_bid_price}, would you like to buy? ").lower()
    if response == "yes":

        quantity:int = input("How many would you like to order? ")

        while app.nextOrderId is None:
            time.sleep(0.1)

        order = Order()
        order.orderId = app.nextOrderId
        order.action = "BUY"
        order.orderType = "MKT"
        order.totalQuantity = quantity

        app.placeOrder(app.nextOrderId, contract, order)

    else:
        print("Order cancelled")

def sell_stock(app):

    contract = req_contract_from_symbol(app)
    print(contract)

    get_live_price(app, contract)
    time.sleep(1)
    stop_mkt_data_stream(app, app.nextReqId - 1)

    response = input(f"The latest bid price was: {app.latest_bid_price}, would you like to sell? ").lower()
    if response == "yes":

        quantity:int = input("How many would you like to sell? ")

        while app.nextOrderId is None:
            time.sleep(0.1)

        order = Order()
        order.orderId = app.nextOrderId
        order.action = "SELL"
        order.orderType = "MKT"
        order.totalQuantity = quantity

        app.placeOrder(app.nextOrderId, contract, order)

    else:
        print("Order cancelled")