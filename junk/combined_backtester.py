import numpy as np
import pandas as pd
import vectorbt as vbt


def combine_indicators(close, window=100, entry=30, exit=70, slow=50, fast=10):
    trend = np.full(close.shape, np.nan)
    rsi = vbt.RSI.run(close, window=window, short_name="rsi")
    slow_ma = vbt.MA.run(close, slow)
    fast_ma = vbt.MA.run(close, fast)
    ma_signal = fast_ma.ma_above(slow_ma).to_numpy()
    rsi_above = rsi.rsi_above(exit).to_numpy()
    rsi_below = rsi.rsi_below(entry).to_numpy()
    for x in range(len(close)):
        if rsi_above[x] is True and ma_signal[x] is True:
            trend[x] = 1
        elif rsi_below[x] is True or ma_signal[x] is False:
            trend[x] = -1
        else:
            trend[x] = 0
    print(trend)
    return trend


# Preferences
num = 10
metric = "total_return"
data_file = "../data/data_30.csv"

# Read data from csv
btc_price = pd.read_csv(data_file)[["timestamp", "close"]]
btc_price["date"] = pd.to_datetime(btc_price["timestamp"], unit="s")
btc_price = btc_price.set_index("date")["close"]

Indicator = vbt.IndicatorFactory(
    class_name="Combination",
    short_name="comb",
    input_names=["close"],
    param_names=["window", "entry", "exit", "slow", "fast"],
    output_names=["ind"]
).from_apply_func(
    combine_indicators,
    window=100,
    entry=30,
    exit=70,
    slow=50,
    fast=10
)

res = Indicator.run(
    btc_price,
    window=100,
    entry=30,
    exit=70,
    slow=50,
    fast=10,
    param_product=True,
)

entries = res.ind == 1.0
exits = res.ind == -1.0
pf = vbt.Portfolio.from_signals(btc_price, entries, exits, fees=0.01)
print(pf.stats())