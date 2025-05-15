
# testing interactions with contract data
def contract_data_testing(app, contract):

    # requests Contract objects that match the symbol input in console
    symbol_input = input("Enter the symbol you would like to get info on: ")
    app.reqMatchingSymbols(app.getNextReqId(), symbol_input)

    # Contract objects must be instantiated in code to be used in API methods
    app.reqContractDetails(app.getNextReqId(), contract)


def req_contract_from_symbol(app):
    symbol_input = input("Enter the symbol for the stock you would like to use: ").upper()

    app.find_matching_contract_event.clear()
    app.matching_contract = None

    app.reqMatchingSymbols(app.getNextReqId(), symbol_input)

    if app.find_matching_contract_event.wait(timeout=5):
        app.matching_contract.exchange = 'NASDAQ' # sets exchange to NASDAQ, otherwise exchange is empty string
        return app.matching_contract
    else:
        print("Contract data not received")
        return None

