

# testing interactions with account summary
def account_summary_testing(app):

    # 9001 is reqId for own account
    app.reqAccountSummary(app.getNextReqId(), "All", "NetLiquidation")

    # if multiple tags are provided, each value will be returned in a separate response
    app.reqAccountSummary(app.getNextReqId(), "All", "AccountType, AvailableFunds")