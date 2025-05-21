

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

# gets historical bar data of contract
def get_market_data_graph(app, contract):

    app.reqMarketDataType(3)
    app.reqHistoricalData(app.getNextReqId(), contract, "", "1 M", "1 day", "TRADES", 1, 1, True, [])

    if app.find_market_data_bars_event.wait(timeout=5):
        return app.market_data_bars
    else:
        print("Market Bar Data not received")
        return None
