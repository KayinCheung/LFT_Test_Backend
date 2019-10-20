from flask import Flask, request
from flask.json import jsonify
import random
from flask_socketio import SocketIO
import threading
import time
from datetime import timedelta
from flask_socketio import send, emit
from flask_cors import CORS
from string import ascii_lowercase
from itertools import chain, product
import pandas as pd
import config

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
seconds_to_keep = config.config["seconds_to_keep"] #Keep 5 mins historical data

class server_state():
    def __init__(self):
        self.symbols = config.config["symbols"]
        self.update_frequency = config.config["update_frequency_milliseconds"]
        self.elements_per_update = config.config["elements_per_update"]

        self.prev_update = []
        self.historicalData = pd.DataFrame(columns=['symbol', 'price', 'time'])

        self.randomizePrice()

    #At set intervals, randomly pick 50 tickers, randomize price and emit websocket
    def randomizePrice(self):
        t = threading.Timer(self.update_frequency / 1000.0, self.randomizePrice)
        t.start()
        ts = time.time()
        print(ts)

        self.prev_update = []

        a = self.symbols
        random.shuffle(a)
        to_randomize = a[:self.elements_per_update]
        for ticker in to_randomize:
            self.prev_update.append([ticker, random.randint(1, 100000)])


        df = pd.DataFrame(self.prev_update, columns=['symbol', 'price'])
        df['time'] = ts
        self.historicalData = self.historicalData.append(df)
        #print (self.historicalData)

        #print(to_randomize)
        socketio.emit('update', {'data': self.prev_update})

        self.truncateHistoricalData()

    # Keep past 5 mins data, discard the rest
    def truncateHistoricalData(self):
        ts = time.time()
        self.historicalData = self.historicalData[self.historicalData["time"] > (ts - seconds_to_keep)]
        #print(self.historicalData)
        
a = server_state()

@app.route("/gethistorical")
def getHistorical():
    output = a.historicalData.to_json(orient='records')
    return jsonify({"historicalData": output})

@app.route("/updatefreq", methods=['POST'])
def updateFreq():
    freq = int(request.get_json()['update_frequency'])
    if freq < 100:
        freq = 100
    a.update_frequency = freq
    return jsonify({"freq": a.update_frequency})

@app.route("/updatefreq", methods=['GET'])
def getUpdateFreq():
    return jsonify(a.update_frequency)

@app.route("/getupdates")
def readLastUpdate():
    return jsonify({"data": a.prev_update})

@app.route("/getconfig")
def readConfig():
    return jsonify({
        "updateFreq": a.update_frequency,
        "ElementPerUpdate": a.elements_per_update,
    })

@app.route("/getsymbols")
def readSymbols():
    return jsonify({
        "Symbols": a.symbols,
    })

if __name__ == '__main__':
    socketio.run(app)


