import pandas as pd
from bs4 import BeautifulSoup
import cloudscraper
import nltk
import yfinance as yf
from nltk.sentiment.vader import SentimentIntensityAnalyzer

scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "desktop": True}
)


def news(ticker):
    # get news on ticker
    _ticker = yf.Ticker(ticker)
    news = _ticker.news
    return news


def sentimentv2(ticker):
    _news = news(ticker)
    # Sentiment Analysis
    analyzer = SentimentIntensityAnalyzer()
    sentiments = [analyzer.polarity_scores(article["title"]) for article in _news]
    # get mean of sentiments
    sentiments_mean = pd.DataFrame(sentiments).mean()
    return round(sentiments_mean["compound"], 2)

if __name__ == "__main__":
    print(sentimentv2("AAPL"))
