import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go


class Scraper:
    def __init__(self, currency_pair="btcusd"):
        self.currency_pair = currency_pair
        self.url = f"https://www.bitstamp.net/api/v2/ohlc/{currency_pair}/"
        self.df = None

