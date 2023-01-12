import pandas as pd
from bs4 import BeautifulSoup
import cloudscraper
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "desktop": True}
)


class SentimentReader:
    def __init__(self, ticker, n=25):
        self.n = n
        self.ticker = ticker
        self.url = "https://finviz.com/quote.ashx?t="
        self.news_table = None
        self.parsed_news = None
        self.news = None

    def scrape_news(self):
        url = self.url + self.ticker
        resp = scraper.get(url)
        html = BeautifulSoup(resp.text, features="lxml")
        self.news_table = html.select_one("#news-table")

    def get_headlines(self):
        self.scrape_news()

        try:
            df_tr = self.news_table.findAll("tr")

            for i, table_row in enumerate(df_tr):
                #a_text = table_row.a.text
                td_text = table_row.td.text
                td_text = td_text.strip()
                if i == self.n - 1:
                    break
        except KeyError:
            pass

    def news_tables(self):
        self.get_headlines()

        # Iterate through the news
        self.parsed_news = []

        for x in self.news_table.findAll("tr"):
            try:
                text = x.a.get_text()
                date_scrape = x.td.text.split()

                if len(date_scrape) == 1:
                    time = date_scrape[0]

                else:
                    date = date_scrape[0]
                    time = date_scrape[1]

                self.parsed_news.append([self.ticker, date, time, text])
            except AttributeError:
                pass

    def analyze_sentiment(self):
        self.news_tables()

        # Sentiment Analysis
        analyzer = SentimentIntensityAnalyzer()

        columns = ["Ticker", "Date", "Time", "Headline"]
        self.news = pd.DataFrame(self.parsed_news, columns=columns)
        scores = self.news["Headline"].apply(analyzer.polarity_scores).tolist()

        df_scores = pd.DataFrame(scores)
        self.news = self.news.join(df_scores, rsuffix="_right")

    def get_dataframe(self):
        self.analyze_sentiment()
        self.analyze_sentiment()

        self.news["Date"] = pd.to_datetime(self.news.Date).dt.date
        unique_ticker = self.news["Ticker"].unique().tolist()
        dataframe = {name: self.news.loc[self.news["Ticker"] == name] for name in unique_ticker}
        dataframe = pd.concat(dataframe, axis=0)

        return dataframe

    def get_mean_sentiment(self):
        dataframe = self.get_dataframe()
        mean = round(dataframe["compound"].mean(), 2)
        return mean


if __name__ == "__main__":
    sentiment = SentimentReader("AAPL")
    print(sentiment.get_dataframe())
    print(sentiment.get_mean_sentiment())
