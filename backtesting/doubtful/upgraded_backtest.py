# This is backtest with STOPLOSSES/TAKEPROFITS
import os

import numpy as np
import pandas as pd
import vectorbt as vbt

from settings import DATA_DIR

# Preferences
num = 10
metric = "total_return"
data_file = os.path.join(DATA_DIR, "data_30.csv")

# Read data from csv
btc_price = pd.read_csv(data_file)[["timestamp", "close"]]
btc_price["date"] = pd.to_datetime(btc_price["timestamp"], unit="s")
btc_price = btc_price.set_index("date")["close"]

# VectorBT part
rsi = vbt.RSI.run(btc_price, window=200, short_name="rsi")

# Entry and exit points for the grid
entry_points = np.linspace(20, 40, num=num)
exit_points = np.linspace(60, 80, num=num)

grid = np.array(np.meshgrid(entry_points, exit_points)).T.reshape(-1, 2)
entries_rsi = rsi.rsi_crossed_below(list(grid[:, [0]]))
exits_rsi = rsi.rsi_crossed_above(list(grid[:, [1]]))

pf = vbt.Portfolio.from_signals(
    btc_price, entries_rsi, exits_rsi,
    # sl_stop=5 / 100, # stop loss
    # tp_stop=5 / 100, # take profit
    fees=0.001
)

# Output performance matrix
# pf_perf = pf.deep_getattr(metric)
# pf_perf_matrix = pf_perf.vbt.unstack_to_df(
#     index_levels="rsi_crossed_above", column_levels="rsi_crossed_below"
# )
# pf_perf_matrix.vbt.heatmap(xaxis_title="entry", yaxis_title="exit").show()

pf_perf = pf.deep_getattr(metric)
pf_perf_matrix = pf_perf.vbt.unstack_to_df(
    index_levels="rsi_crossed_above", column_levels="rsi_crossed_below"
)

# import code
# code.interact(local=locals())
# Get the total number of trades from the trades record
total_trades = np.array([pf.from_signals(btc_price, entries_rsi[:, i], exits_rsi[:, j], fees=0.001).trades.count()
                         for i in range(num) for j in range(num)]).reshape(num, num)

# Now `total_trades` is a 2D NumPy array with the same shape as `pf_perf_matrix`
# Proceed with creating annotations as before
annotations = np.empty_like(pf_perf_matrix, dtype=object)
for i in range(pf_perf_matrix.shape[0]):  # rows
    for j in range(pf_perf_matrix.shape[1]):  # columns
        annotations[i, j] = (
            f"Entry: {entry_points[j]}<br>"
            f"Exit: {exit_points[i]}<br>"
            f"Total Return: {pf_perf_matrix.iloc[i, j]:.2f}%<br>"
            f"Total Trades: {total_trades[i, j]}"
        )

# Generate the heatmap with annotations
pf_perf_matrix.vbt.heatmap(
    xaxis_title="Entry RSI",
    yaxis_title="Exit RSI",
    annotation_text=annotations,
    annotation_kwargs=dict(size=8, font_color="black")
).show()