import threading


# testing interactions with market data
def market_data_testing(app, contract):
    app.reqMarketDataType(3)

    # procedurally retrieves data for every tickType in genericTickList
    app.reqMktData(app.getNextReqId(), contract, "", False, False, [])

# gets live bid, ask, and last traded prices of contract
def get_live_prices_and_volume(app, contract):
    app.reqMarketDataType(3)

    req_id = app.getNextReqId()
    app.market_data.req_id = req_id

    event = threading.Event()
    app.id_to_event[req_id] = event

    app.reqMktData(req_id, contract, "", False, False, [])
    if event.wait(timeout=5):
        print(app.market_data)
        return None
    else:
        print("timed out finding stock data")
        return None

# ends market data stream
def stop_mkt_data_stream(app, reqId):
    app.cancelMktData(reqId)
    print("Market data stream closed.")

# gets historical bar data of contract
def get_market_data_graph(app, contract, period, interval):

    app.market_data_bars = []
    app.find_market_data_bars_event.clear()

    app.reqMarketDataType(3)
    print("Contract: ", contract)

    period_num, _, period_unit = period.partition(' ')
    period_unit = period_unit[0]

    # converts hour/minute values into seconds for TWS processing
    if period_unit == 'H':
        hour_to_seconds = int(period_num) * 3600
        period_value = f'{hour_to_seconds} S'
    elif period_unit == 'M':
        minute_to_seconds = int(period_num) * 60
        period_value = f'{minute_to_seconds} S'
    else:
        period_value = f'{period_num} {period_unit}'


    app.reqHistoricalData(app.getNextReqId(), contract, "", period_value, interval, "TRADES", 1, 1, True, [])

    if app.find_market_data_bars_event.wait(timeout=5):
        return app.market_data_bars
    else:
        print("Market Bar Data not received")
        return None

# opens market data streams for positions in portfolio_dict
def get_portfolio_price_stream(app, contract):
    app.reqMarketDataType(3)

    req_id = app.getNextReqId()
    app.req_id_to_portfolio_symbol[req_id] = contract.symbol

    event = threading.Event()
    app.id_to_event[req_id] = event

    app.reqMktData(req_id, contract, "", False, False, [])

    if event.wait(timeout=5):
        print(f'Portfolio price stream for {contract.symbol} initialized')
    else:
        print(f'Price stream for {contract.symbol} timed out')

# requests live mkt data for market scanner
def get_scanner_mkt_data(app, contract, scanner_req_id):

    req_id = app.getNextReqId()
    app.scanner_contract_req_ids[req_id] = scanner_req_id
    app.scanner_contract_ids_to_symbol[req_id] = contract.symbol
    app.reqMktData(req_id, contract, "", True, False, [])
