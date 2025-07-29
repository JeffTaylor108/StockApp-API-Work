

def req_contract_from_symbol(app, symbol):

    app.find_matching_contract_event.clear()
    app.matching_contract = None

    app.reqMatchingSymbols(app.getNextReqId(), symbol)

    if app.find_matching_contract_event.wait(timeout=5):
        return app.matching_contract
    else:
        print("Contract data not received")
        return None

