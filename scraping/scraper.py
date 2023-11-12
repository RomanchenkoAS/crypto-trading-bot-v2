import os

import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import warnings

import settings

# Filter out FutureWarnings from _plotly_utils.basevalidators
warnings.filterwarnings('ignore', category=FutureWarning, module='_plotly_utils.basevalidators')


class Scraper:
    def __init__(self, currency_pair: str = "btcusdt"):
        self.dates: list[int] = []
        self.currency_pair: str = currency_pair
        self.url: str = f"https://www.bitstamp.net/api/v2/ohlc/{currency_pair}/"
        self.df: pd.DataFrame = pd.DataFrame()

    def set_time_range(self, range_size: int):
        end = datetime.now()
        start = datetime.now() - timedelta(range_size)
        frequency = "6H"  # May be turned into a parameter if needed

        dates = pd.date_range(start, end, freq=frequency)
        self.dates = [int(x.value / 10 ** 9) for x in list(dates)]

    def scrape(self, interval: int = 60, explicit: bool = False):
        """ NOTE: Requires VPN to work. Explicit = True to inspect time intervals. """
        from grequests import get as grequests_get, map as grequests_map  # Import here to avoid monkey-patching
        params_list = []
        for first, last in zip(self.dates, self.dates[1:]):
            params = {
                "step": interval,  # seconds
                "limit": 1000,  # 1..1000
                "start": first,
                "end": last,
            }
            params_list.append(params)

        if explicit:
            print("Time intervals (first/last): ")
            for p in [params_list[0], params_list[-1]]:
                print(
                    datetime.fromtimestamp(p["start"]).strftime("%m/%d/%Y, %H:%M:%S"),
                    " -> ",
                    datetime.fromtimestamp(p["end"]).strftime("%m/%d/%Y, %H:%M:%S"),
                )

        requests_list = (grequests_get(self.url, params=params) for params in params_list)
        responses = grequests_map(requests_list)

        # Nested list comprehension = flattening data
        master_data = [item for data in responses for item in data.json()["data"]["ohlc"]]
        self.df = pd.DataFrame(master_data)

    def save_to_csv(self, filename: str = "data.csv"):
        """ Save to file """
        if filename is None:
            print("Current data will not be saved.")
        if self.df is not None:
            self.clean_data()
            self.df.to_csv(os.path.join(settings.DATA_DIR, filename), index=False)
        else:
            print("No data available to save!")

    def get_dataframe(self):
        self.clean_data()
        return self.df

    def clean_data(self):
        # Strip excessive data not included in time period
        if self.df is None:
            print("Data not scraped yet!")
            return

        self.df = self.df.drop_duplicates()
        self.df["timestamp"] = self.df["timestamp"].astype(int)
        self.df = self.df.sort_values(by="timestamp")
        self.df = self.df[self.df["timestamp"] >= self.dates[0]]
        self.df = self.df[self.df["timestamp"] < self.dates[-1]]

    def visualize(self):
        self.clean_data()
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


SETUP = {
    "currency_pair": "btcusdt",
    "range_size": 30,  # Number of Days in scraping period
    "interval": 60,  # Length of one cline, sec
    "filename": "data_30.csv",  # Where to save the data | None to not save
    "show_timestamps": False,
    "show_plot": True
}

if __name__ == '__main__':
    scraper = Scraper(currency_pair=SETUP["currency_pair"])
    scraper.set_time_range(range_size=SETUP["range_size"])
    scraper.scrape(interval=SETUP["interval"], explicit=SETUP["show_timestamps"])
    if SETUP["show_plot"]:
        scraper.visualize()
    if SETUP["filename"]:
        scraper.save_to_csv(filename=SETUP["filename"])
