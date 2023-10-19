# This is backtest with STOPLOSSES/TAKEPROFITS


import numpy as np
import pandas as pd
import vectorbt as vbt

# Preferences
num = 30
metric = "total_return"
data_file = "data_1m.csv"

# Read data from csv
btc_price = pd.read_csv(data_file)[["timestamp", "close"]]
btc_price["date"] = pd.to_datetime(btc_price["timestamp"], unit="s")
btc_price = btc_price.set_index("date")["close"]

# VectorBT part
rsi = vbt.RSI.run(btc_price, window=100, short_name="rsi")
sma = vbt.SMA.run(btc_price, window=50, short_name="sma")  # Adding SMA as an example

# Entry and exit points for the grid
entry_points = np.linspace(30, 50, num=num)
exit_points = np.linspace(58, 72, num=num)

grid = np.array(np.meshgrid(entry_points, exit_points)).T.reshape(-1, 2)
entries_rsi = rsi.rsi_crossed_below(list(grid[:, [0]]))
exits_rsi = rsi.rsi_crossed_above(list(grid[:, [1]]))

# Combine entries and exits, this is just an example, you may want to define your own logic
entries = entries_rsi
exits = exits_rsi

# Creating Portfolio with Stop Loss and Take Profit
stop_loss = 5  # in percentage
take_profit = 10  # in percentage

pf = vbt.Portfolio.from_signals(
    btc_price, entries, exits, stop_loss=stop_loss, take_profit=take_profit
)

# Output performance matrix
pf_perf = pf.deep_getattr(metric)
pf_perf_matrix = pf_perf.vbt.unstack_to_df(
    index_levels="rsi_crossed_above", column_levels="rsi_crossed_below"
)
print(pf_perf_matrix)
pf_perf_matrix.vbt.heatmap(xaxis_title="entry", yaxis_title="exit").show()
