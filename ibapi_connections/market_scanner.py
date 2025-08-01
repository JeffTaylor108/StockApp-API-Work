from mongodb_connection.IBKR_market_scanners import mongo_insert_market_scanner

# writes valid parameters for TWS scanner to xml file
def req_scanner_params(app):
    app.reqScannerParameters()


# sends market scanner subscription request
def req_scanner_subscription(app, scanner_details, filter_values, display_name):

    print(f'Sending request to subscribe to scanner: {scanner_details} with tags: {filter_values}')
    next_req_id = app.getNextReqId()

    if len(filter_values) < 1:
        app.reqScannerSubscription(next_req_id, scanner_details, [], None)
        mongo_insert_market_scanner(app.client, next_req_id, display_name, scanner_details, [])
    else:
        app.reqScannerSubscription(next_req_id, scanner_details, [], filter_values)

        # converts array of TagValue object to an array of tag dictionaries for mongo
        tags = []
        for tag in filter_values:
            tags.append({
                "tag": tag.tag,
                "value": tag.value
            })

        mongo_insert_market_scanner(app.client, next_req_id, display_name, scanner_details, tags)

# sends market scanner subscription without inserting to mongo
def req_saved_scanner_subscription(app, scanner_details, filter_values, existing_req_id):

    print(f'Sending request to subscribe to scanner {existing_req_id}: {scanner_details} with tags: {filter_values}')

    if len(filter_values) < 1:
        app.reqScannerSubscription(existing_req_id, scanner_details, [], None)
    else:
        app.reqScannerSubscription(existing_req_id, scanner_details, [], filter_values)

# cancels market scanner subscription
def cancel_subscription(app, req_id):
    app.cancelScannerSubscription(req_id)
    print(f"Closing scanner subscription for scanner with id {req_id}")