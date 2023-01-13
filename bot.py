import discord
from io import BytesIO
from discord.ext import commands
from dotenv import load_dotenv
import os
from datetime import datetime
import discord_actions.actions as ac
import algorithms.montecarlo as mc
import algorithms.singleline as sl
import pandas as pd
import functools
import asyncio
import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt
from PIL import Image

# invite url: https://discord.com/oauth2/authorize?client_id=1062847336503586866&permissions=116736&scope=bot
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents)


# run pandas as nonblocking
async def unblock_function(fn, *args, **kwargs):
    func = functools.partial(fn, *args, **kwargs)
    return await asyncio.get_event_loop().run_in_executor(None, func)


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


@bot.command(name="info", help="Returns the info of a stock given ticker")
async def info(ctx, ticker="AAPL"):
    await ctx.send("Compiling the data... Check your DMs...")

    df = await unblock_function(ac.get_info, ticker)
    text = df.to_markdown()
    files = [
        discord.File(
            BytesIO(str(f"""{text}""").encode()), filename=f"{ticker}_info.txt"
        ),
    ]
    if len(str(text)) > 1950:
        await ctx.message.author.send(
            files=files, content=f"[FSD {datetime.now()}] Here's your data: "
        )
    else:
        await ctx.message.author.send(f"""```{text.strip()}```""")


@bot.command(name="history", help="Returns the history of a stock given ticker")
async def history(ctx, ticker="AAPL", period="max"):
    await ctx.send("Compiling the data... Check your DMs...")

    frame_nums = {"day": 1, "week": 7, "month": 30, "year": 365}
    if period == "max":
        df = await unblock_function(ac.get_history, ticker)
    else:
        start = pd.to_datetime("today") - pd.to_timedelta(frame_nums[period], unit="d")
        end = pd.to_datetime("today")
        df = await unblock_function(ac.get_history, ticker, start=start, end=end)
    text = df.to_markdown()

    # remove the volume column
    df.drop(columns=["Volume", "Dividends", "Stock Splits"], inplace=True)
    # get text as pandas plot in Bytes
    plot = df.plot(title=f"{ticker} History")
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    files = [
        discord.File(buffer, filename="plot.png"),
        discord.File(BytesIO(str(text).encode()), filename=f"{ticker}_history.txt"),
    ]
    if len(str(text)) > 1950:
        await ctx.message.author.send(
            files=files, content=f"[FSD {datetime.now()}] Here's your data: "
        )
    else:
        await ctx.message.author.send(
            file=files[0],
            content=f"""```{text.strip()}```""",
        )


@bot.command(name="actions", help="Returns the actions of a stock given ticker")
async def actions(ctx, ticker="AAPL"):
    await ctx.send("Compiling the data... Check your DMs...")

    df = await unblock_function(ac.get_actions, ticker)
    text = df.to_markdown()

    # get text as pandas plot in Bytes
    plot = df.plot()
    title = f"{ticker} Actions"
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    files = [
        discord.File(buffer, filename="plot.png"),
        discord.File(BytesIO(str(text).encode()), filename=f"{ticker}_actions.txt"),
    ]
    if len(str(text)) > 1950:
        await ctx.message.author.send(
            files=files, content=f"[FSD {datetime.now()}] Here's your data: "
        )
    else:
        await ctx.message.author.send(
            files=files[0],
            content=f"""```{text.strip()}```""",
        )


@bot.command(name="dividends", help="Returns the dividends of a stock given ticker")
async def dividends(ctx, ticker="AAPL"):
    await ctx.send("Compiling the data... Check your DMs...")

    df = await unblock_function(ac.get_dividends, ticker)
    text = df.to_markdown()

    # get text as pandas plot in Bytes
    plot = df.plot(title=f"{ticker} Dividends")
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    files = [
        discord.File(buffer, filename="plot.png"),
        discord.File(BytesIO(str(text).encode()), filename=f"{ticker}_dividends.txt"),
    ]
    if len(str(text)) > 1950:
        await ctx.message.author.send(
            files=files, content=f"[FSD {datetime.now()}] Here's your data: "
        )
    else:
        await ctx.message.author.send(
            files=files[0],
            content=f"""```{text.strip()}```""",
        )


@bot.command(name="splits", help="Returns the splits of a stock given ticker")
async def splits(ctx, ticker="AAPL"):
    await ctx.send("Compiling the data... Check your DMs...")

    df = await unblock_function(ac.get_splits, ticker)
    text = df.to_markdown()

    # get text as pandas plot in Bytes
    plot = df.plot(title=f"{ticker} Splits")
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    files = [
        discord.File(buffer, filename="plot.png"),
        discord.File(BytesIO(str(text).encode()), filename=f"{ticker}_splits.txt"),
    ]
    if len(str(text)) > 1950:
        await ctx.message.author.send(
            files=files, content=f"[FSD {datetime.now()}] Here's your data: "
        )
    else:
        await ctx.message.author.send(
            content=f"""```{text.strip()}```""", file=files[0]
        )


@bot.command(
    name="arima",
    help="Predicts the movement of a stock over a given timeframe (day, week, month, year) using ARIMA algorithm",
)
async def arima(ctx, ticker="AAPL", col="High", timeframe="week"):
    await ctx.send("Crunching the numbers... Check your DMs in a minute...")

    fig, df = await unblock_function(sl.arima, ticker, timeframe)
    text = df.to_markdown()

    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    files = [
        discord.File(buffer, filename=f"{ticker}_ARIMA_{col}.png"),
        discord.File(BytesIO(str(text).encode()), filename=f"{ticker}_ARIMA_{col}.txt"),
    ]

    if len(str(text)) > 1950:
        await ctx.message.author.send(
            files=files, content=f"[FSD {datetime.now()}] Here's your data: "
        )
    else:
        await ctx.message.author.send(
            content=f"""```{text.strip()}```""", file=files[0]
        )


@bot.command(
    name="ets",
    help="Predicts the movement of a stock over a given timeframe (day, week, month, year) using ETS algorithm",
)
async def ets(ctx, ticker="AAPL", col="High", timeframe="week"):
    await ctx.send("Crunching the numbers... Check your DMs in a minute...")

    fig, df = await unblock_function(sl.ets, ticker, timeframe)
    text = df.to_markdown()

    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    files = [
        discord.File(buffer, filename=f"{ticker}_ETS_{col}.png"),
        discord.File(BytesIO(str(text).encode()), filename=f"{ticker}_ETS_{col}.txt"),
    ]

    if len(str(text)) > 1950:
        await ctx.message.author.send(
            files=files, content=f"[FSD {datetime.now()}] Here's your data: "
        )
    else:
        await ctx.message.author.send(
            content=f"""```{text.strip()}```""", file=files[0]
        )


@bot.command(
    name="ces",
    help="Predicts the movement of a stock over a given timeframe (day, week, month, year) using CES algorithm",
)
async def ces(ctx, ticker="AAPL", col="High", timeframe="week"):
    await ctx.send("Crunching the numbers... Check your DMs in a minute...")

    fig, df = await unblock_function(sl.ces, ticker, timeframe)
    text = df.to_markdown()

    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    files = [
        discord.File(buffer, filename=f"{ticker}_CES_{col}.png"),
        discord.File(BytesIO(str(text).encode()), filename=f"{ticker}_CES_{col}.txt"),
    ]

    if len(str(text)) > 1950:
        await ctx.message.author.send(
            files=files, content=f"[FSD {datetime.now()}] Here's your data: "
        )
    else:
        await ctx.message.author.send(
            content=f"""```{text.strip()}```""", file=files[0]
        )


@bot.command(
    name="theta",
    help="Predicts the movement of a stock over a given timeframe (day, week, month, year) using THETA algorithm",
)
async def theta(ctx, ticker="AAPL", col="High", timeframe="week"):
    await ctx.send("Crunching the numbers... Check your DMs in a minute...")

    fig, df = await unblock_function(sl.theta, ticker, timeframe)
    text = df.to_markdown()

    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    files = [
        discord.File(buffer, filename=f"{ticker}_THETA_{col}.png"),
        discord.File(BytesIO(str(text).encode()), filename=f"{ticker}_THETA_{col}.txt"),
    ]

    if len(str(text)) > 1950:
        await ctx.message.author.send(
            files=files, content=f"[FSD {datetime.now()}] Here's your data: "
        )
    else:
        await ctx.message.author.send(
            content=f"""```{text.strip()}```""", file=files[0]
        )


@bot.command(
    name="monte_carlo",
    help="Predicts the possible movement of a stock over a given timeframe (day, week, month, year) using Monte Carlo algorithm",
)
async def monte_carlo(ctx, ticker="AAPL", col="Close", timeframe="week"):
    await ctx.send("Crunching the numbers... Check your DMs in a minute...")
    fig, df = await unblock_function(mc.monte_carlo, ticker, timeframe, col)
    text = df.to_markdown()

    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    files = [
        discord.File(buffer, filename=f"{ticker}_Monte_Carlo_{col}.png"),
        discord.File(
            BytesIO(str(text).encode()), filename=f"{ticker}_Monte_Carlo_{col}.txt"
        ),
    ]

    if len(str(text)) > 1950:
        await ctx.message.author.send(
            files=files, content=f"[FSD {datetime.now()}] Here's your data: "
        )
    else:
        await ctx.message.author.send(
            content=f"""```{text.strip()}```""", file=files[0]
        )


bot.run(TOKEN)
