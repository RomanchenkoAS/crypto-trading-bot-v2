from typing import Dict, Any

import numpy as np
import pandas as pd
import vectorbt as vbt


class Backtester:
    def __init__(self, config: Dict[str, Any], data: pd.DataFrame = None):
        self.config = config
        self.data = data
        self.validate_config()

    def validate_config(self):
        required_keys = ['window', 'entry_point', 'exit_point', 'num', 'fee', 'stop_loss', 'take_profit', 'metric']
        if not all(key in self.config for key in required_keys):
            raise ValueError(f"Config dictionary is missing one of the required keys: {required_keys}")

    def load_data_from_csv(self, file_path: str):
        self.data = pd.read_csv(file_path)[["timestamp", "close"]]
        self.data["date"] = pd.to_datetime(self.data["timestamp"], unit="s")
        self.data = self.data.set_index("date")["close"]

    def run_backtest(self):
        rsi = vbt.RSI.run(self.data, window=self.config['window'], short_name="rsi")
        entry_points = np.linspace(self.config['entry_point'][0], self.config['entry_point'][1], num=self.config['num'])
        exit_points = np.linspace(self.config['exit_point'][0], self.config['exit_point'][1], num=self.config['num'])

        grid = np.array(np.meshgrid(entry_points, exit_points)).T.reshape(-1, 2)
        entries_rsi = rsi.rsi_crossed_below(list(grid[:, [0]]))
        exits_rsi = rsi.rsi_crossed_above(list(grid[:, [1]]))

        pf = vbt.Portfolio.from_signals(
            self.data, entries_rsi, exits_rsi,
            stop_loss=self.config['stop_loss'],
            take_profit=self.config['take_profit'],
            fee=self.config['fee']
        )
        return pf

    def display_results(self, pf):
        # Display stats and heatmap
        print(pf.stats())
        if self.config['num'] > 1:
            print(pf.stats(agg_func=None))
            # Output performance matrix
            pf_perf = pf.deep_getattr(self.config['metric'])
            pf_perf_matrix = pf_perf.vbt.unstack_to_df(
                index_levels="rsi_crossed_above", column_levels="rsi_crossed_below"
            )
            pf_perf_matrix.vbt.heatmap(xaxis_title="entry", yaxis_title="exit").show()
