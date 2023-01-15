from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA, AutoETS, AutoCES, AutoTheta
import matplotlib.pyplot as plt
import pandas as pd
import sys

sys.path.append("..")
import discord_actions.actions as ac

sf = StatsForecast(
    models=[AutoARIMA(season_length=7)],
    freq="D",
)
sf2 = StatsForecast(
    models=[AutoETS(season_length=7)],
    freq="D",
)
sf3 = StatsForecast(
    models=[AutoCES(season_length=7)],
    freq="D",
)
sf4 = StatsForecast(
    models=[AutoTheta(season_length=7)],
    freq="D",
)


def arima(ticker, frame="week", col="Close"):
    frame_nums = {"day": 1, "week": 7, "month": 30, "year": 365}
    # get the number of days in the frame
    num_days = frame_nums.get(frame)
    df = ac.history_to_sf(ticker, col)
    pasttime_x = df["ds"].tail(num_days * 2)
    pasttime_y = df["y"].tail(num_days * 2)

    # initialize the plot
    fig = plt.figure()
    plt.plot(pasttime_x, pasttime_y)
    plt.title(f"ARIMA: {ticker}")
    plt.xlabel("Time (Days)")
    plt.ylabel(f"{col} Price($)")
    plt.grid()

    sf.fit(df)
    forecast_df = sf.predict(h=num_days, level=[90])
    # add a day to the beginning of the forecast with a date of 1 + the last date in the past
    # and a y value of the first y value in the forecast
    forecast_df = pd.concat(
        [
            pd.DataFrame(
                {
                    "ds": [forecast_df["ds"].iloc[0] - pd.Timedelta(1, unit="D")],
                    "AutoARIMA": [pasttime_y.iloc[-1]],
                }
            ),
            forecast_df,
        ],
        ignore_index=True,
    )

    forecast_df.drop(columns=["AutoARIMA-lo-90", "AutoARIMA-hi-90"], inplace=True)
    # add the forecast to the plot
    plt.plot(forecast_df["ds"], forecast_df["AutoARIMA"])

    return [fig, forecast_df.set_index("ds")]


def ets(ticker, frame="week", col="Close"):
    frame_nums = {"day": 1, "week": 7, "month": 30, "year": 365}
    # get the number of days in the frame
    num_days = frame_nums.get(frame)
    df = ac.history_to_sf(ticker, col)
    pasttime_x = df["ds"].tail(num_days * 2)
    pasttime_y = df["y"].tail(num_days * 2)

    # initialize the plot
    fig = plt.figure()
    plt.plot(pasttime_x, pasttime_y)
    plt.title(f"ETS: {ticker}")
    plt.xlabel("Time (Days)")
    plt.ylabel(f"{col} Price($)")
    plt.grid()

    sf2.fit(df)
    forecast_df = sf2.predict(h=num_days, level=[90])
    forecast_df = pd.concat(
        [
            pd.DataFrame(
                {
                    "ds": [forecast_df["ds"].iloc[0] - pd.Timedelta(1, unit="D")],
                    "AutoETS": [pasttime_y.iloc[-1]],
                }
            ),
            forecast_df,
        ],
        ignore_index=True,
    )
    forecast_df.drop(columns=["AutoETS-lo-90", "AutoETS-hi-90"], inplace=True)

    # add the forecast to the plot
    plt.plot(forecast_df["ds"], forecast_df["AutoETS"])

    return [fig, forecast_df.set_index("ds")]


def ces(ticker, frame="week", col="Close"):
    frame_nums = {"day": 1, "week": 7, "month": 30, "year": 365}
    # get the number of days in the frame
    num_days = frame_nums.get(frame)
    df = ac.history_to_sf(ticker, col)
    pasttime_x = df["ds"].tail(num_days * 2)
    pasttime_y = df["y"].tail(num_days * 2)

    # initialize the plot
    fig = plt.figure()
    plt.plot(pasttime_x, pasttime_y)
    plt.title(f"CES: {ticker}")
    plt.xlabel("Time (Days)")
    plt.ylabel(f"{col} Price($)")
    plt.grid()

    sf3.fit(df)
    forecast_df = sf3.predict(h=num_days, level=[90])
    forecast_df = pd.concat(
        [
            pd.DataFrame(
                {
                    "ds": [forecast_df["ds"].iloc[0] - pd.Timedelta(1, unit="D")],
                    "CES": [pasttime_y.iloc[-1]],
                }
            ),
            forecast_df,
        ],
        ignore_index=True,
    )

    # add the forecast to the plot
    plt.plot(forecast_df["ds"], forecast_df["CES"])

    return [fig, forecast_df.set_index("ds")]


def theta(ticker, frame="week", col="Close"):
    frame_nums = {"day": 1, "week": 7, "month": 30, "year": 365}
    # get the number of days in the frame
    num_days = frame_nums.get(frame)
    df = ac.history_to_sf(ticker, col)
    pasttime_x = df["ds"].tail(num_days * 2)
    pasttime_y = df["y"].tail(num_days * 2)

    # initialize the plot
    fig = plt.figure()
    plt.plot(pasttime_x, pasttime_y)
    plt.title(f"Theta: {ticker}")
    plt.xlabel("Time (Days)")
    plt.ylabel(f"{col} Price($)")
    plt.grid()

    sf4.fit(df)
    forecast_df = sf4.predict(h=num_days, level=[90])
    forecast_df = pd.concat(
        [
            pd.DataFrame(
                {
                    "ds": [forecast_df["ds"].iloc[0] - pd.Timedelta(1, unit="D")],
                    "AutoTheta": [pasttime_y.iloc[-1]],
                }
            ),
            forecast_df,
        ],
        ignore_index=True,
    )
    forecast_df.drop(columns=["AutoTheta-lo-90", "AutoTheta-hi-90"], inplace=True)

    # add the forecast to the plot
    plt.plot(forecast_df["ds"], forecast_df["AutoTheta"])

    return [fig, forecast_df.set_index("ds")]
