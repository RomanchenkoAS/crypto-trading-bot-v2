from decouple import config
from binance.client import Client
import pandas as pd
import pandas_ta as ta
import time
import json
import os
from datetime import datetime

# testnet = True means all the trading is virtual
client = Client(config("API_KEY"), config("SECRET_KEY"), testnet=True)
asset = "BTCUSDT"
entry = 32.76
exit = 62.83
window = 100

# Balance check
# balance = client.get_asset_balance(asset="BTC")
# print(balance)


def fetch_klines(asset):
    klines = client.get_historical_klines(
        asset, Client.KLINE_INTERVAL_1MINUTE, "2 hour ago UTC"
    )

    klines = [[x[0], float(x[4])] for x in klines]

    klines = pd.DataFrame(klines, columns=["time", "price"])
    klines["time"] = pd.to_datetime(klines["time"], unit="ms")

    return klines


def get_rsi(asset):
    klines = fetch_klines(asset)
    # Use tech analysis pandas module
    klines["rsi"] = ta.rsi(close=klines["price"], length=window)

    print(klines["rsi"].iloc[-1])

    return klines["rsi"].iloc[-1]


def create_account():
    account = {
        "is_buying": True,
        "assets": {},
    }

    with open("bot_account.json", "w") as f:
        f.write(json.dumps(account))


def log(msg):
    message = f"{msg}"
    print("[LOG] ", message)

    # Create a directory for logs if not exist
    if not os.path.isdir("logs"):
        os.mkdir("logs")

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    time = now.strftime("%H-%M-%S")

    with open(f"logs/{today}.txt", "a+") as log_file:
        log_file.write(f"{time} : {msg}\n")


def trade_log(symbol, side, price, amount):
    log(f"{side} {symbol} {amount} for {price} per")

    if not os.path.isdir("trades"):
        os.mkdir("trades")

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    time = now.strftime("%H-%M-%S")

    # If file not present - initialize it with a header
    if not os.path.isfile(f"trades/{today}.csv"):
        with open(f"trades/{today}.csv", "w") as trade_file:
            trade_file.write("symbol,side,amount,price\n")

    # Actual write
    with open(f"trades/{today}.csv", "a+") as trade_file:
        trade_file.write(f"{symbol},{side},{amount},{price}\n")


def do_trade(account, client, asset, side, quantity):
    print("[LOG] Making a trade...")

    if side == "buy":
        # market buy
        order = client.order_market_buy(
            symbol=asset,
            quantity=quantity,
        )

        account["is_buying"] = False

    if side == "sell":
        # market sell
        order = client.order_market_sell(
            symbol=asset,
            quantity=quantity,
        )

        account["is_buying"] = True

    order_id = order["orderId"]

    # Until the order is fulfilled refresh it every second
    while order["status"] != "FILLED":
        order = client.get_order(
            symbol=asset,
            orderId=order_id,
        )
        time.sleep(1)

    print("Made order: ")
    print(order)

    # This list comprehension takes each separate part of buy, multiplies price by quantity
    # and then sums it up to get the total price
    price_paid = sum(
        [float(fill["price"]) * float(fill["qty"]) for fill in order["fills"]]
    )

    # Log trade
    trade_log(asset, side, price_paid, quantity)

    with open("bot_account.json", "w") as f:
        f.write(json.dumps(account))

    print("[LOG] ... trade is over and logged")


if __name__ == "__main__":
    rsi = get_rsi(asset)
    old_rsi = rsi  # to check crossover event

    # Main working loop
    while True:
        current_time = time.localtime()
        seconds = current_time.tm_sec

        # If seconds are not 00 wait 1 sec and go to the next iteration
        if seconds != 0:
            time.sleep(1)
            continue

        try:
            if not os.path.exists("bot_account.json"):
                create_account()

            with open("bot_account.json") as f:
                account = json.load(f)

            old_rsi = rsi
            rsi = get_rsi(asset)

            if account["is_buying"]:
                # If crossover up-to-down ▼
                if rsi < entry and old_rsi > entry:
                    # trade buy
                    do_trade(account, client, asset, "buy", 0.01)

            else:
                # If crossover bottom-up ▲
                if rsi > exit and old_rsi < exit:
                    # trade sell
                    do_trade(account, client, asset, "sell", 0.01)

            print(
                "[INFO] current rsi =",
                round(rsi, 3),
                " |",
                time.strftime("%y.%m.%d %H:%M:%S", current_time),
            )

            time.sleep(2)

        except Exception as _ex:
            log("[ERR] " + str(_ex))
            time.sleep(30)