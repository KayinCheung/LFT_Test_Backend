# LFT_Test_Backend

A websocket python server built using Flask and SocketIO.

## Features

- Loads from config: symbols, update frequency, duration of historical data to keep, and num of elements per update.

- Every `update frequency interval` (default 1 second), it picks 50 symbols at random, randomize their price between 0-100000, and emits a websocket stream of the updated symbols and price.

- Update frequency is configurable down to a minimum of 100ms.

- Saves past 5 mins of updates. The historical data is available via rest api call.


## Deploying server

1) `pip3 install -r requirements`
2) `Python3 app.py`

The server will be deployed locally at `http://127.0.0.1:5000`

