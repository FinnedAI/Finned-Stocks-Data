import yfinance as yf
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA
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


def arima(ticker, frame="week", col="Close"):
    frame_nums = {"day": 1, "week": 7, "month": 30, "year": 365}
    # get the number of days in the frame
    num_days = frame_nums.get(frame)
    sf = StatsForecast(
        models=[AutoARIMA(season_length=7)],
        freq="D",
    )
    df = history_to_sf(ticker, col)
    sf.fit(df)
    forecast_df = sf.predict(h=num_days, level=[90])
    forecast_df.drop(columns=["AutoARIMA-lo-90", "AutoARIMA-hi-90"],
                     inplace=True)
    # get last num_days/2 rows of hist
    last = df.tail(int(num_days / 2))
    # change index column to unique_id column
    last = last.set_index("unique_id")
    last = last.rename(columns={"y": "AutoARIMA"})
    # append "last" before the content of forecast_df
    forecast_df = pd.concat([last, forecast_df])

    return forecast_df