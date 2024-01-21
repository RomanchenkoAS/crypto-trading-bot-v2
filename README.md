#### Requirements: python-decouple python-binance pandas pandas-ta

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