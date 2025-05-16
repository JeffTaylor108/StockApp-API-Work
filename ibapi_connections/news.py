import datetime
import re

# testing interactions with news data
def news_data_testing(app, contract):

    # requests news providers user is subscribed to
    app.reqNewsProviders()

    # requests contract specific news
    app.reqHistoricalNews(app.getNextReqId(), contract.conId, "BRFG", "2025-5-10", "", 10, [])

    # requests specific news article
    app.reqNewsArticle(app.getNextReqId(), "BRFG", 'BRFG$1add90db', [])


# gets recent article news headlines for contract
# (refactor to search for article headlines from all valid sources)
def get_news_headlines(app, contract):

    app.reqNewsProviders()
    today = datetime.date.today()
    app.reqHistoricalNews(app.getNextReqId(), contract.conId, "BRFG", today, "", 10, [])

    if app.find_articles_event.wait(timeout=5):
        for headline in app.headlines_found:
            cleaned_headline = re.sub(r"^\{.*?\}", "", headline).strip()
            print(cleaned_headline)


# gets recent news articles for contract
# (refactor to search for article headlines from all valid sources)
def get_news_articles(app, contract):

    app.reqNewsProviders()
    today = datetime.date.today()
    app.reqHistoricalNews(app.getNextReqId(), contract.conId, "BRFG", today, "", 10, [])

    app.reqNewsArticle(app.getNextReqId(), "BRFG", 'BRFG$1add90db', [])