

# testing interactions with account summary
def account_summary_testing(app):

    # 9001 is reqId for own account
    app.reqAccountSummary(app.getNextReqId(), "All", "NetLiquidation")

    # if multiple tags are provided, each value will be returned in a separate response
    app.reqAccountSummary(app.getNextReqId(), "All", "AccountType, AvailableFunds")

# requests available funds of account
def get_available_funds(app):
    app.request_funds_event.clear()

    app.reqAccountSummary(app.getNextReqId(), "All", "AvailableFunds")
    if app.request_funds_event.wait(timeout=5):
        print("Available funds: ", app.available_funds)
    else:
        print("Time out while finding available funds")

# requests P&L data
def get_pnl(app):
    app.request_pnl_event.clear()

    app.reqPnL(app.getNextReqId(), app.account, "")
    if app.request_pnl_event.wait(timeout=5):
        print ("PnL data received")
    else:
        print('Timed out requesting PnL data')

# requests positions of an account
def currently_held_positions(app):

    # requests positions for accessible account
    app.reqPositions()

# gets stock symbols of positions in portfolio_dict
def get_position_symbols(app):

    app.portfolio_list = []
    app.find_portfolio_event.clear()
    position_symbols = []

    app.reqPositions()

    if app.find_portfolio_event.wait(timeout=5):
        for position in app.portfolio_list:
            symbol = position.contract.symbol
            position_symbols.append(symbol)
    else:
        print("Timeout while finding positions")

    print('Position symbols:', position_symbols)

    return position_symbols