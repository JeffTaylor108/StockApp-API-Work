import datetime
import re

from ibapi.contract import Contract


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

    headlines = []

    app.articles_found.clear()
    app.find_articles_event.clear()

    app.reqNewsProviders()
    today = datetime.date.today()
    app.reqHistoricalNews(app.getNextReqId(), contract.conId, "BRFG", today, "", 10, [])

    if app.find_articles_event.wait(timeout=5):

        for article in app.articles_found:
            headlines.append(article)

    return headlines


# gets recent news articles for contract
# (refactor to search for article headlines from all valid sources)
def get_news_article_from_id(app, article_id):

    app.reqNewsArticle(app.getNextReqId(), "BRFG", article_id, [])

    if app.find_article_text_event.wait(timeout=5):
        article_text = app.selected_article_text

    return article_text
