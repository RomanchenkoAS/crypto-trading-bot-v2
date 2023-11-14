from typing import Dict, Any

import numpy as np
import pandas as pd
import vectorbt as vbt

from scraping.scraper import Scraper


# TODO Make basic backtester and subclasses that allow grid and single search
# TODO we will need to gridsearch window as well as entries/exits
# TODO backtester single will allow to write some results to json or csv

# TODO lets make basebacktester
# It will hold init, validates, and load data (csv and scraping)

class Backtester:
    def __init__(self, config: Dict[str, Any], data: pd.DataFrame = None):
        self.config: Dict = config
        self.data: pd.DataFrame = data
        self.pf: vbt.Portfolio | None = None
        self.validate_config()

    def validate_config(self):
        required_keys = ['window', 'entry_point', 'exit_point', 'num', 'fee', 'stop_loss', 'take_profit', 'metric']
        if not all(key in self.config for key in required_keys):
            raise ValueError(f"Config dictionary is missing one of the required keys: {required_keys}")

    def validate_data(self):
        if self.data is None:
            raise ValueError(f"Backtester is missing data source.")
        if not isinstance(self.data, pd.DataFrame):
            raise TypeError(f"Backtester input data is invalid.")

    def load_data_from_csv(self, file_path: str):
        self.data = pd.read_csv(file_path)[["timestamp", "close"]]
        self.data["date"] = pd.to_datetime(self.data["timestamp"], unit="s")
        self.data = self.data.set_index("date")["close"]

    def run_single_backtest(self):
        self.validate_data()
        rsi = vbt.RSI.run(self.data, window=self.config['window'], short_name="rsi")

        entry_point = self.config['entry_point']
        exit_point = self.config['exit_point']

        entries = rsi.rsi_crossed_below(entry_point)
        exits = rsi.rsi_crossed_above(exit_point)

        self.pf = vbt.Portfolio.from_signals(
            self.data, entries, exits,
            stop_loss=self.config['stop_loss'],
            take_profit=self.config['take_profit'],
            fee=self.config['fee']
        )

        self.display_single_strategy_results()
        return self.pf

    def run_grid_backtest(self):
        """ Backtest a grid of strategies """
        self.validate_data()
        rsi = vbt.RSI.run(self.data, window=self.config['window'], short_name="rsi")

        entry_points = np.linspace(self.config['entry_point'][0], self.config['entry_point'][1], num=self.config['num'])
        exit_points = np.linspace(self.config['exit_point'][0], self.config['exit_point'][1], num=self.config['num'])

        grid = np.array(np.meshgrid(entry_points, exit_points)).T.reshape(-1, 2)
        entries = rsi.rsi_crossed_below(grid[:, 0])
        exits = rsi.rsi_crossed_above(grid[:, 1])

        self.pf = vbt.Portfolio.from_signals(
            self.data, entries, exits,
            stop_loss=self.config['stop_loss'],
            take_profit=self.config['take_profit'],
            fee=self.config['fee']
        )

        self.display_grid_strategy_results()
        return self.pf

    def display_single_strategy_results(self):
        if self.pf is not None:
            print(self.pf.stats())
            self.pf.plot().show()

    def display_grid_strategy_results(self):
        if self.pf is not None:
            print(self.pf.stats(agg_func=None))
            # Output performance matrix
            pf_perf = self.pf.deep_getattr(self.config['metric'])
            pf_perf_matrix = pf_perf.vbt.unstack_to_df(
                index_levels="rsi_crossed_above", column_levels="rsi_crossed_below"
            )
            pf_perf_matrix.vbt.heatmap(xaxis_title="entry", yaxis_title="exit").show()


# Assuming your Scraper class is already defined as per your existing script
scraper = Scraper(currency_pair="btcusdt")
scraper.set_time_range(range_size=30)
scraper.scrape(interval=60)
data = scraper.get_dataframe()

# For a single strategy backtest:
backtester_config = {
    'window': 100,
    'entry_point': 32.76,  # Single entry point for single backtest
    'exit_point': 62.83,  # Single exit point for single backtest
    'num': 30,  # Number of cells in heatmap
    'fee': 0.001,
    'stop_loss': 5,
    'take_profit': 10
}
backtester_single = Backtester(config=backtester_config, data=data)
single_pf = backtester_single.run_single_backtest()

# For a grid backtest:
backtester_config = {
    'window': 100,
    'entry_point': (30, 50),
    'exit_point': (58, 72),
    'num': 30,
    'fee': 0.001,
    'stop_loss': 5,
    'take_profit': 10
}
backtester_grid = Backtester(config=backtester_config, data=data)
grid_pf = backtester_grid.run_grid_backtest()
