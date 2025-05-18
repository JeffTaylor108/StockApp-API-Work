

# testing interactions with market data
def market_data_testing(app, contract):
    app.reqMarketDataType(3)

    # procedurally retrieves data for every tickType in genericTickList
    app.reqMktData(app.getNextReqId(), contract, "", False, False, [])

# gets live bid, ask, and last traded prices of contract
def get_live_prices(app, contract):
    app.reqMarketDataType(3)
    app.reqMktData(app.getNextReqId(), contract, "", False, False, [])

# ends market data stream
def stop_mkt_data_stream(app, reqId):
    app.cancelMktData(reqId)
    print("Market data stream closed.")

# gets live volume of contract
def get_live_volume(app, contract):
    app.reqMarketDataType(3)
    app.reqMktData(app.getNextReqId(), contract, "", False, False, [])

