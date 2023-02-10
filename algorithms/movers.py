from ftplib import FTP
import pandas as pd
import urllib3
import discord
import sys
import json
http = urllib3.PoolManager()

# config is at the root of the project
# since this file is normally imported from the root of the project
# we need to add the parent directory to the path when running this file directly
if __name__ == "__main__":
    sys.path.append("..")
import config as CONFIG

import sys
import asyncio

"""
Track live momement of tickers and send alerts when they move
past a certain threshold.
"""
tickers = False

async def retrieve_tickers():
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

async def get_tickers_json(bot):
    tickers = await retrieve_tickers()
    # batch the tickers into groups of 1000
    ticker_batches = [tickers[i : i + 1900] for i in range(0, len(tickers), 1900)]
    # send the batches to the API
    for batch in ticker_batches:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?formatted=true&symbols={'%2c'.join(batch)}&corsDomain=finance.yahoo.com"
        
        response = http.request('GET', url)
        data = json.loads(response.data)
        for ticker in data["quoteResponse"]["result"]: await notify_if_appropriate(ticker["symbol"], ticker["regularMarketChangePercent"]["raw"], bot)

async def notify_if_appropriate(ticker, percent_change, bot):
    CHANNEL_ID = CONFIG.CHANNEL_ID
    THRESHOLD = CONFIG.THRESHOLD
    if percent_change > THRESHOLD:
        # send alert to discord in the channel with the id CHANNEL_ID
        channel = bot.get_channel(CHANNEL_ID)
        message = f"{ticker} is on the move! It has moved {percent_change}% today. Buy it while it's hot!"
        await channel.send(message)


# start the movers thread
async def start_movers(bot):
    print("Starting movers subprocess...")
    while True:
        await get_tickers_json(bot)
        # sleep without blocking the main thread for 10 minutes
        await asyncio.sleep(600)

if __name__ == "__main__":
    t = retrieve_tickers()
    # batch the tickers into groups of 1900 (browser URI limit is 2000)
    ticker_batches = [t[i : i + 1900] for i in range(0, len(t), 1900)]
    print('%2c'.join(ticker_batches[0]))