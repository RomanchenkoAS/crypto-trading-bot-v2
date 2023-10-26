import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

# TODO Lets introduce class scraper
# And structure that a little better

currency_pair = "btcusd"
url = f"https://www.bitstamp.net/api/v2/ohlc/{currency_pair}/"

# Before
start = datetime.now() - timedelta(1)
# Now
end = datetime.now()

dates = pd.date_range(start, end, freq="6H")
dates = [int(x.value / 10**9) for x in list(dates)]

# print([datetime.fromtimestamp(x).strftime("%m/%d/%Y, %H:%M:%S")
#       for x in dates])

master_data = []

print("Time intervals: ")
for first, last in zip(dates, dates[1:]):
    print(
        datetime.fromtimestamp(first).strftime("%m/%d/%Y, %H:%M:%S"),
        " -> ",
        datetime.fromtimestamp(last).strftime("%m/%d/%Y, %H:%M:%S"),
    )

    params = {
        "step": 60,  # seconds
        "limit": 1000,  # 1..1000
        "start": first,
        "end": last,
    }

    data = requests.get(url, params=params)

    data = data.json()["data"]["ohlc"]

    master_data += data

# Clear up the dataframe
df = pd.DataFrame(master_data)
df = df.drop_duplicates()

df["timestamp"] = df["timestamp"].astype(int)
df = df.sort_values(by="timestamp")

# Filter resulting dates to cut off extra ones
df = df[df["timestamp"] >= dates[0]]
df = df[df["timestamp"] < dates[-1]]

print("\nResulting DataFrame: ")
print(df)

# Write results to csv
df.to_csv("data.csv", index=False)

# Display plot if needed
# Create a datetime column
df["datetime"] = df["timestamp"].apply(lambda x: pd.to_datetime(x, unit="s"))

# Configure plot
fig = go.Figure(
    data=[
        go.Candlestick(
            x=df["datetime"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
        )
    ]
)

fig.update_layout(xaxis_rangeslider_visible=False)  # Remove slider
fig.update_layout(template="plotly_dark")  # Add some style
fig.update_layout(yaxis_title="BTCUSDT pair", xaxis_title="Date-time")  # Name axes

# Display plot
fig.show()