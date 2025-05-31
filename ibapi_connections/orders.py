import time

from PyQt6.QtCore import QTimer
from ibapi.order import *
from ibapi.order_cancel import OrderCancel

from ibapi_connections.contract_data import req_contract_from_symbol
from ibapi_connections.market_data import get_live_prices_and_volume, stop_mkt_data_stream


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


def submit_order(app, contract, action, order_type, quantity, limit_price=None):

    order = Order()
    order.orderId = app.nextOrderId
    order.action = action
    order.orderType = order_type
    order.totalQuantity = quantity

    if limit_price is not None:
        order.lmtPrice = limit_price

    print("Order: ", order.__dict__)
    try:
        app.placeOrder(app.nextOrderId, contract, order)
        print("Order placed.")
    except Exception as e:
        print("Error placing order:", e)

def get_active_orders(app):

    app.find_active_orders_event.clear()
    app.active_orders.clear()

    app.reqOpenOrders()
    if app.find_active_orders_event.wait(timeout=5):
        print("All active orders found")
    else:
        print("Timeout while finding active orders")

def get_completed_orders(app):

    app.find_completed_orders_event.clear()
    app.completed_orders = []

    app.reqCompletedOrders(True)
    if app.find_completed_orders_event.wait(timeout=5):
        print("All completed orders found")
    else:
        print('Timeout while finding completed orders')

def submit_bracket_order(app, contract, action, order_type, quantity, take_profit, stop_loss, limit_price=None ):

    # sets up parent order
    parent_order = Order()
    parent_order.orderId = app.nextOrderId
    parent_order.action = action
    parent_order.orderType = order_type
    parent_order.totalQuantity = quantity
    if limit_price is not None:
        parent_order.lmtPrice = limit_price
    parent_order.transmit = False

    # sets up take profit order
    take_profit_order = Order()
    take_profit_order.orderId = parent_order.orderId + 1
    if action == "BUY":
        take_profit_order.action = "SELL"
    else:
        take_profit_order.action = "BUY"
    take_profit_order.orderType = "LMT"
    take_profit_order.totalQuantity = quantity
    take_profit_order.lmtPrice = take_profit
    take_profit_order.parentId = parent_order.orderId
    take_profit_order.transmit = False

    # sets up stop loss order
    stop_loss_order = Order()
    stop_loss_order.orderId = parent_order.orderId + 2
    if action == "BUY":
        stop_loss_order.action = "SELL"
    else:
        stop_loss_order.action = "BUY"
    stop_loss_order.orderType = "STP"
    stop_loss_order.totalQuantity = quantity
    stop_loss_order.auxPrice = stop_loss
    stop_loss_order.parentId = parent_order.orderId
    stop_loss_order.transmit = True

    # sends orders to TWS
    try:
        app.placeOrder(parent_order.orderId, contract, parent_order)
        app.placeOrder(take_profit_order.orderId, contract, take_profit_order)
        app.placeOrder(stop_loss_order.orderId, contract, stop_loss_order)
        app.nextOrderId += 3
        print("Bracket Order placed.")
    except Exception as e:
        print("Error placing order:", e)



def cancel_order(app, order_id):
    app.cancelOrder(order_id, OrderCancel())