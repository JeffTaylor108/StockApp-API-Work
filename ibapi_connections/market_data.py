

# testing interactions with market data
def market_data_testing(app, contract):
    app.reqMarketDataType(3)

    # procedurally retrieves data for every tickType in genericTickList
    app.reqMktData(app.getNextReqId(), contract, "", False, False, [])

# gets live bid, ask, and last traded prices of contract
def get_live_prices(app, contract):
    app.reqMarketDataType(3)

    req_id = app.getNextReqId()
    app.id_to_symbol[req_id] = contract.symbol

    app.find_stock_data_event.clear()

    if contract.symbol not in app.stock_data:
        app.stock_data[contract.symbol] = {
            "req_id": req_id,
            "bid": None,
            "ask": None,
            "last": None,
            "high": None,
            "low": None,
            "open": None,
            "close": None,
            "volume": None
        }
    else:
        app.stock_data[contract.symbol]['req_id'] = req_id

    app.reqMktData(req_id, contract, "", False, False, [])
    if app.find_stock_data_event.wait(timeout=5):
        return app.stock_data[contract.symbol]
    else:
        print("timed out finding stock data")
        return None

# ends market data stream
def stop_mkt_data_stream(app, reqId):
    app.cancelMktData(reqId)
    print("Market data stream closed.")

# gets live volume of contract
def get_live_volume(app, contract):
    app.reqMarketDataType(3)
    app.reqMktData(app.getNextReqId(), contract, "", False, False, [])

# gets historical bar data of contract
def get_market_data_graph(app, contract, interval):

    app.market_data_bars = []
    app.find_market_data_bars_event.clear()

    app.reqMarketDataType(3)
    app.reqHistoricalData(app.getNextReqId(), contract, "", "1 W", interval, "TRADES", 1, 1, True, [])

    if app.find_market_data_bars_event.wait(timeout=5):
        return app.market_data_bars
    else:
        print("Market Bar Data not received")
        return None
