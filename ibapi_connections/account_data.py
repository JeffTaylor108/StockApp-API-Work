

# testing interactions with account summary
def account_summary_testing(app):

    # 9001 is reqId for own account
    app.reqAccountSummary(app.getNextReqId(), "All", "NetLiquidation")

    # if multiple tags are provided, each value will be returned in a separate response
    app.reqAccountSummary(app.getNextReqId(), "All", "AccountType, AvailableFunds")

# requests positions of an account
def currently_held_positions(app):

    # requests positions for accessible account
    app.reqPositions()

# gets stock symbols of positions in portfolio
def get_position_symbols(app):

    app.portfolio = []
    app.find_portfolio_event.clear()
    position_symbols = []

    app.reqPositions()

    if app.find_portfolio_event.wait(timeout=5):
        for position in app.portfolio:
            symbol = position.contract.symbol
            position_symbols.append(symbol)
    else:
        print("Timeout while finding positions")

    print(position_symbols)

    return position_symbols