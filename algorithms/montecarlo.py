import numpy as np
import pandas as pd
from random import random
import matplotlib.pyplot as plt
from scipy.stats import norm
import sys

sys.path.append("..")
import discord_actions.actions as ac


def monte_carlo(ticker, frame="week", col="Close"):
    frame_nums = {"day": 1, "week": 7, "month": 30, "year": 365}
    start_date = pd.to_datetime("today") - pd.Timedelta(frame_nums[frame], unit="D")
    end_date = pd.to_datetime("today")
    hist = ac.get_history(ticker, start=start_date, end=end_date)
    days = [i for i in range(1, len(hist[col]) + 1)]
    price_orig = hist[col].tolist()
    change = hist[col].pct_change().tolist()
    change = change[1:]

    # Stats for model
    avg = np.mean(change)
    stdev = np.std(change)
    sims = 200
    days_to_sim = frame_nums[frame]

    fig = plt.figure()
    plt.plot(days, price_orig)
    plt.title(f"Monte Carlo: {ticker}")
    plt.xlabel(f"Trading Days After {start_date}")
    plt.ylabel(f"{col} Price($)")
    plt.xlim([frame_nums[frame]/2, len(days) + days_to_sim])
    plt.grid()

    end = []
    above = []

    for i in range(sims):
        num_days = [days[-1]]
        price = [hist.iloc[-1, 0]]
        for j in range(days_to_sim):
            num_days.append(num_days[-1] + 1)
            percent_change = norm.ppf(random(), loc=avg, scale=stdev)
            price.append(price[-1] * (1 + percent_change))

        if price[-1] > price_orig[-1]:
            above.append(1)
        else:
            above.append(0)
        end.append(price[-1])
        plt.plot(num_days, price)
    avg_price = sum(end) / sims
    avg_perc_change = (avg_price - price_orig[-1]) / price_orig[-1]
    increase_chance = sum(above) / sims

    text = pd.DataFrame.from_dict(
        {
            "Closing": str(round(avg_price, 2)),
            "Percent Change": str(round(avg_perc_change * 100, 2)) + "%",
            "Chance of Increase": str(round(increase_chance * 100, 2)) + "%",
        },
        orient="index",
    )
    return [fig, text]

if __name__ == "__main__":
    fig, df = monte_carlo("AAPL", frame="month", col="Close")
    # open the figure and keep open
    plt.show(block=True)