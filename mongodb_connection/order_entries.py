from datetime import datetime

from schwab_connections.schwab_acccount_data import get_account_num


# inserts order preview into mongo database
def insert_order_entry(client, order_preview):
    symbol = order_preview['orderStrategy']['orderLegs'][0]['finalSymbol']
    order_type = order_preview['orderStrategy']['orderType']
    action = order_preview['orderStrategy']['orderLegs'][0]['instruction']

    if action == "BUY" and order_type == "MARKET":
        individual_price = order_preview['orderStrategy']['orderLegs'][0]['askPrice']
    elif action == "SELL" and order_type == "MARKET":
        individual_price = order_preview['orderStrategy']['orderLegs'][0]['bidPrice']
    elif order_type == "LIMIT":
        individual_price = order_preview['orderStrategy']['price']

    quantity = order_preview['orderStrategy']['quantity']
    order_value = order_preview['orderStrategy']['orderValue']
    status = order_preview['orderStrategy']['status']

    account_num = get_account_num()

    order_history_collection = client.Schwab_DB.preview_order_entries
    order_doc = {
        "account_num": account_num,
        "symbol": symbol,
        "order_type": order_type,
        "action": action,
        "individual_price": individual_price,
        "quantity": quantity,
        "order_value": order_value,
        "status": status,
        "timestamp": datetime.now()
    }

    inserted_id = order_history_collection.insert_one(order_doc).inserted_id
    print(f'Order entry successfully submitted: {inserted_id}')

# retrieves all order entries previewed
def fetch_order_entries(client):
    current_account_num = get_account_num()

    order_history_collection = client.Schwab_DB.preview_order_entries
    previous_orders = order_history_collection.find({'account_num': current_account_num})
    print(f'Matching orders: {previous_orders}')

    return previous_orders

# deletes order from database and history table
def database_delete_order(client, id):

    order_history_collection = client.Schwab_DB.preview_order_entries
    deleted_order = order_history_collection.delete_one({'_id': id})
    print(f'Order deleted: {deleted_order}')