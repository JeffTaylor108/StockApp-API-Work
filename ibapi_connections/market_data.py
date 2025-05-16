

# testing interactions with market data
def market_data_testing(app, contract):
    app.reqMarketDataType(3)

    # procedurally retrieves data for every tickType in genericTickList
    app.reqMktData(app.getNextReqId(), contract, "", False, False, [])

# gets live price of contract
def get_live_price(app, contract):
    app.reqMarketDataType(3)
    app.desired_tick = 68

    app.reqMktData(app.getNextReqId(), contract, "", False, False, [])

# ends market data stream
def stop_mkt_data_stream(app, reqId):
    app.cancelMktData(reqId)
    print("Market data stream closed.")

# gets live volume of contract
def get_live_volume(app, contract):
    app.reqMarketDataType(3)
    app.desired_tick = 74

    app.reqMktData(app.getNextReqId(), contract, "", False, False, [])

