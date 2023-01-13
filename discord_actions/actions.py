import yfinance as yf
import pandas as pd
import sys
from pandas_datareader import data

sys.path.append("..")
import algorithms.sentiment as sn
yf.pdr_override()


def get_news(ticker):
    news_normal = []
    news = sn.news(ticker)
    for article in news:
        news_normal.append(
            [article["title"], article["link"], ", ".join(article["relatedTickers"])]
        )

    _news = pd.DataFrame(news_normal, columns=["title", "link", "relatedTickers"])
    return _news


def get_sentiment(ticker):
    sentiment = sn.sentimentv2(ticker)
    return sentiment


def get_info(ticker, frame):
    frame_nums = {"day": 1, "week": 7, "month": 30, "year": 365}
    num_days = frame_nums.get(frame)
    start = pd.Timestamp.today() - pd.Timedelta(days=num_days)
    end = pd.Timestamp.today()
    _ticker = data.DataReader(ticker, start=start, end=end)

    return [_ticker, get_sentiment(ticker)]


def get_calendar(ticker):
    _ticker = yf.Ticker(ticker)
    calendar = _ticker.calendar
    return calendar


def get_history(ticker, **kwargs):
    # extraxt start and end dates from kwargs
    start = kwargs.get("start", None)
    end = kwargs.get("end", None)
    _ticker = yf.Ticker(ticker)
    # get historical market data
    if start and end:
        hist = _ticker.history(start=start, end=end)
    else:
        hist = _ticker.history(period="max")
    return hist


def get_actions(ticker):
    _ticker = yf.Ticker(ticker)
    actions = _ticker.actions
    return actions


def get_dividends(ticker):
    _ticker = yf.Ticker(ticker)
    dividends = _ticker.dividends
    return dividends


def get_splits(ticker):
    _ticker = yf.Ticker(ticker)
    splits = _ticker.splits
    return splits


def history_to_sf(ticker, metric):
    hist = get_history(ticker).tail(int(365.25 * 10))
    # iterate over the dataframe
    unique_id = ["ID" for i in range(len(hist))]
    ds = [date for date in hist.index]
    y = [metric for metric in hist[metric]]
    df = pd.DataFrame(list(zip(unique_id, ds, y)), columns=["unique_id", "ds", "y"])
    return df
