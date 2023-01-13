import yfinance as yf
import pandas as pd
import sys

sys.path.append("..")
from algorithms.sentiment import SentimentReader as sentiment


def get_articles(ticker):
    sr = sentiment(ticker)
    return sr.get_headlines()


def get_sentiment(ticker):
    sr = sentiment(ticker)
    return sr.get_mean_sentiment()


def get_info(ticker):
    _ticker = yf.Ticker(ticker)
    # convert to dataframe
    _ticker.info["sentiment"] = get_sentiment(ticker)
    info = pd.DataFrame.from_dict(_ticker.info, orient="index")

    return info


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
    df = pd.DataFrame(list(zip(unique_id, ds, y)),
                      columns=["unique_id", "ds", "y"])
    return df
