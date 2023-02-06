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


@bot.command(name="info", help="Returns the info of a stock given ticker and timeframe")
async def info(ctx, ticker="AAPL"):
    await ctx.send("Compiling the data... Check your DMs...")

    df, sentiment = await unblock_function(ac.get_info, ticker)
    nonmetrics = ["phone", "website", "logo_url", "city", "state", "country"]
    for nonmetric in nonmetrics:
        del df[nonmetric]

    text = pd.DataFrame.from_dict(df, orient="index").to_markdown()

    file = discord.File(
        BytesIO(str(f"""{text}""").encode()), filename=f"{ticker}_info.txt"
    )
    await ctx.message.author.send(
        file=file,
        content=f"[FSD {datetime.now()}] Here's your data: \n *Sentiment for {ticker} is: {sentiment}*",
    )


@bot.command(
    name="calendar", help="Returns the upcoming events of a stock given ticker"
)
async def calendar(ctx, ticker="AAPL"):
    await ctx.send("Compiling the data... Check your DMs...")

    df = await unblock_function(ac.get_calendar, ticker)
    text = df.to_markdown()
    file = discord.File(
        BytesIO(str(f"""{text}""").encode()), filename=f"{ticker}_calendar.txt"
    )

    await ctx.message.author.send(
        file=file,
        content=f"[FSD {datetime.now()}] Here's your data: ",
    )


@bot.command(
    name="experts", help="Returns the expert recommendations of a stock given ticker"
)
async def experts(ctx, ticker="AAPL", timeframe="week"):
    await ctx.send("Compiling the data... Check your DMs...")

    df = await unblock_function(ac.get_experts, ticker, timeframe)
    text = df.to_markdown()
    file = discord.File(
        BytesIO(str(f"""{text}""").encode()), filename=f"{ticker}_experts.txt"
    )

    await ctx.message.author.send(
        file=file,
        content=f"[FSD {datetime.now()}] Here's your data: ",
    )


@bot.command(
    name="sustainability", help="Returns the sustainability of a stock given ticker"
)
async def sustainability(ctx, ticker="AAPL"):
    await ctx.send("Compiling the data... Check your DMs...")

    df = await unblock_function(ac.get_sustainability, ticker)
    text = df.to_markdown()
    file = discord.File(
        BytesIO(str(f"""{text}""").encode()), filename=f"{ticker}_sustainability.txt"
    )

    await ctx.message.author.send(
        file=file,
        content=f"[FSD {datetime.now()}] Here's your data: ",
    )


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


@bot.command(name="news", help="Returns the news of a stock given ticker")
async def news(ctx, ticker="AAPL"):
    await ctx.send("Compiling the data... Check your DMs...")

    df = await unblock_function(ac.get_news, ticker)
    text = df.to_markdown()

    file = discord.File(BytesIO(str(text).encode()), filename=f"{ticker}_news.txt")
    if len(str(text)) > 1950:
        await ctx.message.author.send(
            file=file, content=f"[FSD {datetime.now()}] Here's your data: "
        )
    else:
        await ctx.message.author.send(f"""```{str(text).strip()}```""")


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
async def arima(ctx, ticker="AAPL", col="Close", timeframe="week"):
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
async def ets(ctx, ticker="AAPL", col="Close", timeframe="week"):
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
async def ces(ctx, ticker="AAPL", col="Close", timeframe="week"):
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
async def theta(ctx, ticker="AAPL", col="Close", timeframe="week"):
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
    name="top",
    help="Show the top stocks within the given timeframe (day, week, month, year)",
)
async def top(ctx, col="Close", timeframe="week", num=10):
    await ctx.send("Crunching the numbers... Check your DMs in a minute...")

    avgs = {}
    for ticker in ac.file_as_list()[:num]:
        data = await unblock_function(mc.fast_monte_carlo, ticker, timeframe, col)
        avgs[ticker] = round((data["%change"] * data["increase"]) / 100, 2)

    avgs = {
        k: v for k, v in sorted(avgs.items(), key=lambda item: item[1], reverse=True)
    }
    df = pd.DataFrame.from_dict(avgs, orient="index", columns=["Relevancy Score"])
    # set index name
    df.index.name = "Ticker"
    text = df.to_markdown()

    # make pie chart
    fig, ax = plt.subplots()
    nonzero = df[df["Relevancy Score"] >= 0]
    labels = nonzero.index
    ax.pie(
        nonzero["Relevancy Score"],
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
    )
    ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(f"Top {num} stocks for {col} in {timeframe}")
    plt.tight_layout()

    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    files = [
        discord.File(buffer, filename=f"Top_{col}.png"),
        discord.File(BytesIO(str(text).encode()), filename=f"Top_{col}.txt"),
    ]

    if len(str(text)) > 1950:
        await ctx.message.author.send(
            files=files, content=f"[FSD {datetime.now()}] Here's your data: "
        )
    else:
        await ctx.message.author.send(
            file=files[0], content=f"""```{text.strip()}```"""
        )


@bot.command(
    name="income",
    help="Shows the income statement of a company",
)
async def income(ctx, ticker="AAPL"):
    await ctx.send("Crunching the numbers... Check your DMs in a minute...")

    df = await unblock_function(ac.get_income_stmt, ticker)
    text = df.to_markdown()

    if len(str(text)) > 1950:
        await ctx.message.author.send(
            file=discord.File(
                BytesIO(str(text).encode()), filename=f"{ticker}_Income.txt"
            ),
            content=f"[FSD {datetime.now()}] Here's your data: ",
        )
    else:
        await ctx.message.author.send(content=f"""```{text.strip()}```""")


@bot.command(
    name="cashflow",
    help="Shows the cashflow statement of a company",
)
async def cashflow(ctx, ticker="AAPL"):
    await ctx.send("Crunching the numbers... Check your DMs in a minute...")

    df = await unblock_function(ac.get_cashflow, ticker)
    text = df.to_markdown()

    if len(str(text)) > 1950:
        await ctx.message.author.send(
            file=discord.File(
                BytesIO(str(text).encode()), filename=f"{ticker}_Cashflow.txt"
            ),
            content=f"[FSD {datetime.now()}] Here's your data: ",
        )
    else:
        await ctx.message.author.send(content=f"""```{text.strip()}```""")


@bot.command(
    name="shares",
    help="Shows the number of shares outstanding of a company",
)
async def shares(ctx, ticker="AAPL"):
    await ctx.send("Crunching the numbers... Check your DMs in a minute...")

    df = await unblock_function(ac.get_shares, ticker)
    df.rename(columns={"BasicShares": "Shares Outstanding"}, inplace=True)
    text = df.to_markdown()

    # make plot of shares
    plot = df.plot()
    plot.set_title(f"Shares Outstanding for {ticker} by Quarter")
    fig = plot.get_figure()
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    files = [
        discord.File(buffer, filename=f"{ticker}_Shares.png"),
        discord.File(BytesIO(str(text).encode()), filename=f"{ticker}_Shares.txt"),
    ]

    if len(str(text)) > 1950:
        await ctx.message.author.send(
            files=files,
            content=f"[FSD {datetime.now()}] Here's your data: ",
        )
    else:
        await ctx.message.author.send(
            file=files[0], content=f"""```{text.strip()}```"""
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
