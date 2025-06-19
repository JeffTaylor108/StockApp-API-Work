


# writes valid parameters for TWS scanner to xml file
def req_scanner_params(app):
    app.reqScannerParameters()


# sends market scanner subscription request
def req_scanner_subscription(app, scanner_details, filter_values):

    print(f'Sending request to subscribe to scanner: {scanner_details}')

    if len(filter_values) < 1:
        app.reqScannerSubscription(app.getNextReqId(), scanner_details, [], None)
    else:
        app.reqScannerSubscription(app.getNextReqId(), scanner_details, [], filter_values)

# cancels market scanner subscription
def cancel_subscription(app, reqId):
    app.cancelScannerSubscription(reqId)