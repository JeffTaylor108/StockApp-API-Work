

# testing interactions with news data
def news_data_testing(app, contract):

    # requests news providers user is subscribed to
    app.reqNewsProviders()

    # requests contract specific news
    app.reqHistoricalNews(app.getNextReqId(), contract.conId, "BRFG", "2025-5-10", "", 10, [])

    # requests specific news article
    app.reqNewsArticle(app.getNextReqId(), "BRFG", 'BRFG$1add90db', [])