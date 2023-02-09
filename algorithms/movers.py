from ftplib import FTP
import pandas as pd
import requests
import discord
import config as CONFIG
import time
import asyncio

"""
Track live momement of tickers and send alerts when they move
past a certain threshold.
"""
past_movements = {}
tickers = False

def retrieve_tickers():
    # prevent calling of ftp server after the first time running the function
    global tickers
    if tickers: return tickers

    """
    Retrieve tickers from FTP server.
    ftp://ftp.nasdaqtrader.com/symboldirectory/
    """
    ftp = FTP("ftp.nasdaqtrader.com")
    ftp.login()
    ftp.cwd("symboldirectory")
    with open("nasdaqtraded.txt", "wb") as f:
        ftp.retrbinary("RETR nasdaqtraded.txt", f.write)
    ftp.quit()

    tickers = pd.read_csv("nasdaqtraded.txt", sep="|")["Symbol"][:-1]
    blacklist = ['.', '$']
    tickers = [str(ticker) for ticker in tickers if all(char not in str(ticker) for char in blacklist)]
    return tickers

# init_phase is a boolean that is true if this is the first time the function is being called
# so that we can initialize the past_movements dict
def get_tickers_json(init_phase):
    tickers = retrieve_tickers()
    # batch the tickers into groups of 1000
    ticker_batches = [tickers[i : i + 1900] for i in range(0, len(tickers), 1900)]
    # send the batches to the API
    for batch in ticker_batches:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?formatted=true&symbols={'%2c'.join(batch)}&corsDomain=finance.yahoo.com"
        
        response = requests.get(url)
        data = response.json()
        if init_phase:
            for ticker in data["quoteResponse"]["result"]:
                past_movements[ticker["symbol"]] = ticker["regularMarketChangePercent"]["raw"]
        else:
            for ticker in data["quoteResponse"]["result"]: notify_if_appropriate(ticker["symbol"], ticker["regularMarketChangePercent"]["raw"])

async def notify_if_appropriate(ticker, percent_change):
    CHANNEL_ID = CONFIG["CHANNEL_ID"]
    THRESHOLD = CONFIG["THRESHOLD"]
    if abs(percent_change - past_movements[ticker]) > THRESHOLD:
        # send alert to discord in the channel with the id CHANNEL_ID
        channel = bot.get_channel(CHANNEL_ID)
        message = f"{ticker} is on the move! It has moved {percent_change - past_movements[ticker]}% in the last minute. Buy it while it's hot!"
        await channel.send(message)


# start the movers thread
def start_movers():
    get_tickers_json(True)
    while True:
        get_tickers_json(False)
        time.sleep(60)

if __name__ == "__main__":
    t = retrieve_tickers()
    # batch the tickers into groups of 1900 (browser URI limit is 2000)
    ticker_batches = [t[i : i + 1900] for i in range(0, len(t), 1900)]
    print('%2c'.join(ticker_batches[0]))