import grequests
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go


class Scraper:
    def __init__(self, currency_pair: str = "btcusd"):
        self.dates: list[int] = []
        self.currency_pair: str = currency_pair
        self.url: str = f"https://www.bitstamp.net/api/v2/ohlc/{currency_pair}/"
        self.df: pd.DataFrame = pd.DataFrame()

    def set_time_range(self, range_size: int, frequency: str = "1D"):
        end = datetime.now()
        start = datetime.now() - timedelta(range_size)

        dates = pd.date_range(start, end, freq=frequency)
        self.dates = [int(x.value / 10 ** 9) for x in list(dates)]

    def scrape(self, interval: int = 60):
        """ NOTE: Requires VPN to work """
        # print("Time intervals: ")
        params_list = []
        for first, last in zip(self.dates, self.dates[1:]):
            # print(
            #     datetime.fromtimestamp(first).strftime("%m/%d/%Y, %H:%M:%S"),
            #     " -> ",
            #     datetime.fromtimestamp(last).strftime("%m/%d/%Y, %H:%M:%S"),
            # )

            params = {
                "step": interval,  # seconds
                "limit": 1000,  # 1..1000
                "start": first,
                "end": last,
            }
            params_list.append(params)

        requests_list = (grequests.get(self.url, params=params) for params in params_list)
        responses = grequests.map(requests_list)

        master_data = [data.json()["data"]["ohlc"] for data in responses]
        print(master_data)
        self.df = pd.DataFrame(master_data)

    def save_to_csv(self, filename="data.csv"):
        if self.df is not None:
            self.df.to_csv(filename, index=False)
        else:
            print("No data available to save!")

    def clean_data(self):
        if self.df is None:
            print("Data not scraped yet!")
            return

        self.df = self.df.drop_duplicates()
        self.df["timestamp"] = self.df["timestamp"].astype(int)
        self.df = self.df.sort_values(by="timestamp")
        self.df = self.df[self.df["timestamp"] >= self.dates[0]]
        self.df = self.df[self.df["timestamp"] < self.dates[-1]]

    def visualize(self):
        if self.df is None:
            print("Data not available for visualization!")
            return

        self.df["datetime"] = self.df["timestamp"].apply(lambda x: pd.to_datetime(x, unit="s"))
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=self.df["datetime"],
                    open=self.df["open"],
                    high=self.df["high"],
                    low=self.df["low"],
                    close=self.df["close"],
                )
            ]
        )

        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.update_layout(template="plotly_dark")
        fig.update_layout(yaxis_title=f"{self.currency_pair.upper()} pair", xaxis_title="Date-time")
        fig.show()


scraper = Scraper(currency_pair="btcusdt")
scraper.set_time_range(range_size=10, frequency="6H")
scraper.scrape()
scraper.clean_data()
scraper.visualize()
scraper.save_to_csv(filename="data.csv")
