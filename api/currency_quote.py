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

class CurrencyClient:
    def __init__(self, logger=logger):
        self.api_key = os.getenv('CURRENCY_API_KEY', 'api_key')
        self.currency_ticker = os.getenv('CURRENCY_TICKER')
        if self.api_key is None:
            raise ValueError("api key must be present")
        self.price = 0

        self.snapshot = 0.0

        self.logger = logger

        self.streaming_client = WebSocketClient(
        	api_key=self.api_key,
        	market=Market.Crypto
	    )
        self.streaming_client.subscribe("XT.{}-USD".format(self.currency_ticker))

        self.threading_update = threading.Thread(target=self.updates)
        self.threading_update.start()

        thread_snap = threading.Thread(target=self.update_snapshot)
        thread_snap.start()

    def updates(self):
        self.streaming_client.run(self.update_price)

    def update_snapshot(self):
        while True:
            self.snapshot = self.get_snapshot()
            time.sleep(1)

    def update_price(self, msgs: List[WebSocketMessage]):
        for m in msgs:
            price = m.price
            while price != self.price:
                self.price = price

    def get_forex_quote(self):
        while self.price == 0:
            time.sleep(1)

        return self.price

    def parse_crypto_response(response):
        return response.json()['last']['price']
  
    def get_snapshot(self):
        response = None
        try:
            response = requests.get("https://api.polygon.io/v1/indicators/rsi/X:{}USD?timespan=minute&window=20&series_type=close&order=desc&limit=1&apiKey={}".format(self.currency_ticker, self.api_key))                       
        except(Exception) as e:
            self.logger.error("Problem requesting rsi information: {}".format(e))
        return self.parse_snapshot(response.json())

    def parse_snapshot(self, resp):
        return (float(resp['results']['values'][0]['value']) - 50.0)
    
