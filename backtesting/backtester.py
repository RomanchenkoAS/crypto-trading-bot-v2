import os

import numpy as np
import pandas as pd
import vectorbt as vbt

from settings import DATA_DIR


class Backtester:
    def __init__(self, data_source, cells: int = 30, metric: str = "total_return"):
        self.data_source: [str, pd.DataFrame] = data_source
        self.data: [str, pd.DataFrame] = None
        self.cells: int = cells
        self.metric: str = metric
        self.pf_perf_matrix: [pd.DataFrame] = None

    def load_data(self) -> None:
        if isinstance(self.data_source, pd.DataFrame):
            self.data = self.data_source
        elif isinstance(self.data_source, str):
            btc_price = pd.read_csv(self.data_source)[["timestamp", "close"]]
            btc_price["date"] = pd.to_datetime(btc_price["timestamp"], unit="s")
            self.data = btc_price.set_index("date")["close"]
        else:
            raise ValueError("Data source must be a DataFrame or a CSV file path")

    def show_heatmap(self):
        if self.pf_perf_matrix is not None:
            self.pf_perf_matrix.vbt.heatmap(xaxis_title="entry", yaxis_title="exit").show()
        else:
            print("No performance matrix available. Run backtest first.")

    def run_backtest(self, rsi_data: dict):
        rsi = vbt.RSI.run(self.data, window=rsi_data["window"], short_name="rsi")
        sma = vbt.MA.run(self.data, window=50, short_name="ma")
        entry1, entry2 = rsi_data["entry_points"]
        entry_points = np.linspace(entry1, entry2, num=self.cells)
        exit1, exit2 = rsi_data["exit_points"]
        exit_points = np.linspace(exit1, exit2, num=self.cells)
        grid = np.array(np.meshgrid(entry_points, exit_points)).T.reshape(-1, 2)
        entries = rsi.rsi_crossed_below(list(grid[:, [0]]))
        exits = rsi.rsi_crossed_above(list(grid[:, [1]]))
        pf = vbt.Portfolio.from_signals(self.data, entries, exits)

        pf_perf = pf.deep_getattr(self.metric)
        self.pf_perf_matrix = pf_perf.vbt.unstack_to_df(
            index_levels="rsi_crossed_above", column_levels="rsi_crossed_below"
        )


rsi_data = {
    "indicator": "rsi",
    "window": 100,
    "entry_points": (30, 50),
    "exit_points": (58, 72)
}

# Usage Example
data_file = os.path.join(DATA_DIR, "data.csv")  # or pass a DataFrame directly
backtester = Backtester(data_source=data_file)
backtester.load_data()
backtester.run_backtest(rsi_data)
backtester.show_heatmap()
