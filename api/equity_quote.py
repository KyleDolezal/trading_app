import os
import logging
logger = logging.getLogger(__name__)
from polygon import RESTClient
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, Feed, Market
from typing import List
import time
import requests
import threading
import datetime

class EquityClient:
    def __init__(self, target_symbol):
        self.price = 0
        self.api_key = os.getenv('EQUITY_API_KEY')
        self.target_symbol = target_symbol
        self.equity_ticker = os.getenv('EQUITY_TICKER', 'SCHB')

        if self.api_key is None:
            raise ValueError("api key must be present")

        self.client = RESTClient(self.api_key)

        self.streaming_client = WebSocketClient(
	        api_key=self.api_key,
            feed=Feed.RealTime,
            market=Market.Stocks
	    )
        self.streaming_client.subscribe("Q.{}".format(self.target_symbol))

        self.threading_update = threading.Thread(target=self.updates)
        self.threading_update.start()

    def updates(self):
        self.streaming_client.run(self.update_price)

    def update_price(self, msgs: List[WebSocketMessage]):
        for m in msgs:
            self.price = m.bid_price

    def get_equity_quote(self):
        while self.price == 0:
            time.sleep(1)

        return self.price
    
    def get_snapshot(self):
        response = None
        for i in range(20):
            try:
                seconds_to_allow_for_recent_trade = 3
                now = int(datetime.datetime.now().timestamp() - seconds_to_allow_for_recent_trade)
                                            
                now_response = requests.get("https://api.polygon.io/v3/trades/{}?timestamp.gte={}&order=asc&limit=1&sort=timestamp&apiKey={}".format(self.target_symbol, now, self.api_key))
                now_price = 0
                if len(now_response.json().get('results', [])) == 0 or now_response.json()['results'][0]['price'] == 0:
                    now_price = self.price
                while now_price == 0:
                    time.sleep(.2)
                    now_response = requests.get("https://api.polygon.io/v3/trades/{}?timestamp.gte={}&order=asc&limit=1&sort=timestamp&apiKey={}".format(self.target_symbol, now, self.api_key))
                    now_price = now_response.json()['results'][0]['price']
                five_minutes_ago = now - 300
                past_response = requests.get("https://api.polygon.io/v3/trades/{}?timestamp.gte={}&order=asc&limit=1&sort=timestamp&apiKey={}".format(self.target_symbol, five_minutes_ago, self.api_key))
                while len(past_response.json().get('results', [])) == 0:
                    time.sleep(.2)
                    past_response = requests.get("https://api.polygon.io/v3/trades/{}?timestamp.gte={}&order=asc&limit=1&sort=timestamp&apiKey={}".format(self.target_symbol, five_minutes_ago, self.api_key))
                past_price = past_response.json()['results'][0]['price']
                return ((now_price - past_price) / now_price) * 100
            except(Exception) as e:
                logger.error("Problem requesting currency information: {}".format(e))
                time.sleep(1)