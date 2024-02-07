# Description
This is an upgraded version of my older crypto trading bot: https://github.com/RomanchenkoAS/binance-trading-bot. Full desctiption may be found there.

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
