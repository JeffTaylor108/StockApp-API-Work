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

def cancel_order(app, order_id):
    app.cancelOrder(order_id, OrderCancel())

    print(f'Order {order_id} cancelled')