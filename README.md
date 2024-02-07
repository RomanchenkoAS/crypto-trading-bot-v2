# Description
This is an upgraded version of my older crypto trading bot: https://github.com/RomanchenkoAS/binance-trading-bot.

#### Requirements:
- managed by poetry: run ``` poetry install ```

#### Binance client docs: 
- https://python-binance.readthedocs.io/en/latest/

#### Installing redis:
```bash
sudo apt update && sudo apt install redis-server 
```

#### Testnet
API : testnet.binance.vision
- Get API-key and secret key from: https://testnet.binance.vision/key/generate
- Testnet uses a separate key

#### Real network
- create api-key/secret-key in binance account settings
- Add IP to allowed list
- get ip with

```bash 
 curl icanhazip.com 
```
- add it to binance api list (in browser)

#### TODOS 
- [ ] add types and ranges check for backtester input data
- [ ] save data in persistent db, instead of redis
- [ ] test both backtesters with existing input
- [ ] make a grid search for a good window/input-output
- [ ] we will need to gridsearch window as well as entries/exits
- [ ] backtester single will allow to write some results to json or csv

# v.1 bot description
This is an indicator-based binance trading bot & script to scrape / backtest historical data.

## Objectives 🎯

- Scrape historical candlestick data from Binance exchange
- Backtest a specific strategy against historical data and show a heatmap for a range of strategy coefficients
- Create a bot that trades on Binance testnet using a chosen strategy and records its actions to a CSV and log file
- Analyze trades and show a dataframe and returns of the trading strategy

## Technologies used 🛠

 - Python 
 - Plotly
 - Pandas
 - Numpy
 - VectorBT
 - Binance Client
 - [Bitstamp](https://www.bitstamp.net/api/) - for scraping 

## Description 🤔

#### Scraping 📃

To scrape data I am using **Bitstamp API** (web link). It is fairly simple: choose dates and generate according timestamps, make a request, recieve Open-High-Low-Close data (candlesticks), strip surplus from recieved data and write to csv using **pandas**.
- API: https://www.bitstamp.net/api/
- URL: https://www.bitstamp.net/api/v2/ohlc/{currency_pair}/

Some info about process is shown to the user to make sure all the numbers are correct:

<p align="center">
<img src="https://user-images.githubusercontent.com/119735427/235074146-41d7eddb-07b8-4ff3-9027-3199f773320b.png" alt="alt-text">
</p>

As a little extra: scraping.py builds a candlestick plot from recieved data with **plotly**:
<p align="center">
<img src="https://user-images.githubusercontent.com/119735427/235073869-ed1cbb39-5fc5-4921-9b18-7071671f18e1.png" alt="alt-text">
</p>


#### Backtest 📜

- backtest.py : test chosen strategy against a grid of coefficients
- backtest_single.py : test a single pair of coefficients and get in-depth data
- backtest_optimize.py : with a single pair of coefficients optimize "window" size at which RSI is calculated 

Now we can apply any chosen strategy to this historical data. To do this, I am using **VectorBT library**. It is really convenient to use, because it requires no class - based strategy, just a simple declaration of chosen indicator and border points.
In this case I am using relative-strength indicator (aka RSI) to find my entry & exit points. General idea is: we must buy the commodity whenever it is oversold, and sell it once it becomes overbought. RSI moves in range from 1 to 100, and it is generally advised to buy at RSI=30 and then sell at RSI=70.
Let us apply RSI strategy with these levels to 1 month worth of candlesticks data :

<p align="center">
<img src="https://user-images.githubusercontent.com/119735427/235079062-e8056a1f-03d1-4d96-988b-e9af23a3f261.png" alt="alt-text">
</p>

As we can see 30-70 RSI strategy returned 5.3% profit whereas benchmark returned only 3.7%. That is alright, but not good enough, it is time to play with borders a little. VectorBT allows to run multiple tests at once with a range of coefficients, so we set range for entry=(1..50) and exit=(50..99), and create a linear space grid (using numpy) to check all of those combinations and recieve total return of each pair. 

<p align="center">
<img src="https://user-images.githubusercontent.com/119735427/235080396-0f32d85d-68c5-4102-8777-d2626d82d192.png" alt="alt-text">
</p>

This heatmap shows a large portions of entry&exit pairs with return = 0, that means no trades were made with these coefficients.
Yellow squares point out the most successful pairs, so we narrow down the range and increase fragmentation to find the most efficient combination.
With range entry=(30..50) & exit=(58..72):

<p align="center">
<img src="https://user-images.githubusercontent.com/119735427/235081891-5291af99-f4bb-43a3-be6f-bed0cbfc0ebf.png" alt="alt-text">
</p>

Now, almost 15% for a month is an outstanding profit, let's check these entry&exit points statistic:

<p align="center">
<img src="https://user-images.githubusercontent.com/119735427/235082661-e99625f9-042e-4a71-9f4d-0801a5b72718.png" alt="alt-text">
</p>

Alongside dry text statistic we can build a plot for this strategy:

<p align="center">
<img src="https://user-images.githubusercontent.com/119735427/235082911-49429047-6ae6-4944-99f8-e4336f957851.png" alt="alt-text">
</p>

This looks real nice, next step is **forward-testing** this strategy.

#### Forward-testing (a.k.a. trading bot) 🪙

Bot (bot.py) has a simple moveset: 
- each second it makes a request to the binance api via **binance.Client** to get candlestick data
- with candlesticks data current RSI value is calculated
- IF it is under entry level AND the previous one was above entry level then the crossover happened
- whenever the crossover happens a fixed amount of commodity is bought, every check and trade is recorded in log file and .csv file with trades
- after buy, the bot does the same, but for exit level - looking an appropriate moment to sell

This procedure has a few minor points.
Bot generates a json file (if it is not present) which stores data about side it's currently on (BUY/SELL) and commodities it stores (e.g. BTCUSDT). For each trading day, it generates a separate log file and csv file with trades, so it can be both easily inspected by human (by looking at logs) and analysed procedurally (with reading .csv files).
Since backtest was ran at candlesticks with intervals of minute, forward testing should as well only trade once a minute to comply with chosen strategy, so if a minute has not yet passed since the last check we just time.sleep(1) for one second. This also works well to reduce CPU & network load.

Working bot shows this kind of output to the console :

<p align="center">
<img src="https://user-images.githubusercontent.com/119735427/235092149-1a2b0a36-e2ed-4d57-a79c-5d048d5b11a1.png" alt="alt-text">
</p>

There is really no need for a user to look at it constantly, since all the trades are already being logged to the log file:

<p align="center">
<img src="https://user-images.githubusercontent.com/119735427/235093010-c2a96294-08fc-47f1-bf01-89b9e091e04e.png" alt="alt-text">
</p>

Now to make an appropriate amount of forward testing a bot must work constantly for not less than a week. Keeping a personal machine running for this kind of time is a challenge by itself, so I hosted it on **google cloud** VM. The least possible CPU amount costs about $0.02 per day to run and is more than enough for such a script to run.

To launch the bot and keep it running when the terminal is closed (and close it as well if it is running at the moment), I use a bash script:

```
#!/bin/bash

# Check if the bot.py process is currently running
if pgrep -f "python3 bot.py" >/dev/null; then
    # If running, kill the process
    echo "Bot is currently running. Stopping..."
    pkill -f "python3 bot.py"
    echo "Bot stopped."
else
    # If not running, start the process
    echo "Bot is not running. Starting..."
    nohup python3 bot.py > nohup.out 2>&1 &
    echo "Bot started."
fi
```

And another one to check if the bot is currently running without killing it / opening a new instance:

```
#!/bin/bash

# Check if the bot.py process is currently running
if pgrep -f "python3 bot.py" >/dev/null; then
    # If running, kill the process
    echo "Bot is currently running."
else
    # If not running,
    echo "Bot is not running."
fi
```

Another way to run the script is via screen-detacher command, e.g. tmux

``` 
tmux new-session # create new screen
python3 bot.py # run the script, then detach with ctrl+b -> d
tmux attach-session # reattach the screen
```

After the bot makes quite some trades, they need to be analyzed to ensure viability of chosen strategy.

#### Analysis 📈

To perform trades analysis there is a very simple script to display all the trades in form of **pandas** dataframe trade_analysis.py:
A successful day of trading would look like this:

<p align="center">
<img src="https://user-images.githubusercontent.com/119735427/235101566-0167ee85-baef-4601-a50e-ed1596eca626.png" alt="alt-text">
</p>

## Result

After running the trading bot in forward-testing mode for 75 days, the following results were obtained:

<p align="center">
<img src="https://github.com/RomanchenkoAS/binance-trading-bot/assets/119735427/a357a264-b8fb-4bb4-9e99-aa2574b63aad" alt="alt-text">
</p>

During this 75-day period, the bot generated a total profit of 160 USDT. Considering an initial capital of approximately 290 USDT, this translates to an impressive +62% return on investment (ROI) over the testing period. The daily return on investment is approximately +0.83%, indicating consistent and favorable performance.

The forward-testing conducted in the Binance testnet has shown that the implemented trading strategy is highly efficient, outperforming benchmark returns. With a keen focus on optimizing entry and exit points using relative-strength indicators (RSI), the bot successfully captured favorable market conditions and executed profitable trades.

The ability to achieve such significant returns during the forward-testing phase is a promising indicator of the script's potential to perform well in live trading scenarios. However, it is essential to continue monitoring the bot's performance, adapting it to market changes, and conducting rigorous backtesting to validate its effectiveness over various market conditions.

As the bot's performance has demonstrated efficiency and stability over the testing period, the next steps involve further enhancements and goals for future development.
