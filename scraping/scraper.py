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

