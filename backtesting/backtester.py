from abc import ABC, abstractmethod
from typing import Dict, Any

import numpy as np
import pandas as pd
import vectorbt as vbt

from scraping.scraper import Scraper


class BaseBacktester(ABC):
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
        if not isinstance(self.data, pd.DataFrame) and not isinstance(self.data, pd.Series):
            raise TypeError(f"Backtester input data is invalid. Must be DataFrame, not {type(self.data)}.")

    def load_data_from_csv(self, file_path: str):
        self.data = pd.read_csv(file_path)[["timestamp", "close"]]
        self.data["date"] = pd.to_datetime(self.data["timestamp"], unit="s")
        self.data = self.data.set_index("date")["close"]

    @abstractmethod
    def run_backtest(self):
        pass

    @abstractmethod
    def display_results(self):
        pass


class SingleStrategyBacktester(BaseBacktester):
    def display_results(self):
        if self.pf is not None:
            print(self.pf.stats())
            self.pf.plot().show()

    def run_backtest(self):
        self.validate_data()
        rsi = vbt.RSI.run(self.data, window=self.config['window'], short_name="rsi")

        entry_point = self.config['entry_point']
        exit_point = self.config['exit_point']

        entries = rsi.rsi_crossed_below(entry_point)
        exits = rsi.rsi_crossed_above(exit_point)

        self.pf = vbt.Portfolio.from_signals(
            self.data, entries, exits,
            sl_stop=self.config['stop_loss'],
            tp_stop=self.config['take_profit'],
            fees=self.config['fee']
        )

        self.display_results()
        return self.pf


class GridBacktester(BaseBacktester):
    def run_backtest(self):
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
            sl_stop=self.config['stop_loss'],
            tp_stop=self.config['take_profit'],
            fees=self.config['fee']
        )

        self.display_results()
        return self.pf

    def display_results(self):
        if self.pf is not None:
            print(self.pf.stats(agg_func=None))
            # Output performance matrix
            pf_perf = self.pf.deep_getattr(self.config['metric'])
            pf_perf_matrix = pf_perf.vbt.unstack_to_df(
                index_levels="rsi_crossed_above", column_levels="rsi_crossed_below"
            )
            pf_perf_matrix.vbt.heatmap(xaxis_title="entry", yaxis_title="exit").show()


def main():
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
        'take_profit': 10,
        'metric': 'total_return',
    }
    backtester_single = SingleStrategyBacktester(config=backtester_config, data=data)
    single_pf = backtester_single.run_backtest()

    # For a grid backtest:
    backtester_config = {
        'window': 100,
        'entry_point': (30, 50),
        'exit_point': (58, 72),
        'num': 30,
        'fee': 0.001,
        'stop_loss': 5,
        'take_profit': 10,
        'metric': 'total_return',
    }
    backtester_grid = GridBacktester(config=backtester_config, data=data)
    grid_pf = backtester_grid.run_backtest()


if __name__ == '__main__':
    main()
