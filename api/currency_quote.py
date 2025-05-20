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
    def __init__(self):
        self.api_key = os.getenv('CURRENCY_API_KEY')
        self.currency_ticker = os.getenv('CURRENCY_TICKER')
        if self.api_key is None:
            raise ValueError("api key must be present")
        self.price = 0

        self.streaming_client = WebSocketClient(
        	api_key=self.api_key,
        	feed=Feed.RealTime,
        	market=Market.Forex
	    )
        self.streaming_client.subscribe("C.{}/USD".format(self.currency_ticker))

        self.threading_update = threading.Thread(target=self.updates)
        self.threading_update.start()


    def updates(self):
        self.streaming_client.run(self.update_price)

    def update_price(self, msgs: List[WebSocketMessage]):
        for m in msgs:
            self.price = m.bid_price

    def get_forex_quote(self):
        while self.price == 0:
            time.sleep(1)

        return self.price

    def parse_crypto_response(response):
        return response.json()['last']['price']
  
    def get_snapshot(self):
        response = None
        for i in range(20):
            try:
                response = requests.get("https://api.polygon.io/v2/snapshot/locale/global/markets/crypto/tickers/X:{}USD?apiKey={}".format(self.currency_ticker, self.api_key))
                return self.parse_snapshot(response.json())
            except(Exception) as e:
                logger.error("Problem requesting currency information: {}".format(e))
                time.sleep(1)
    
    def parse_snapshot(self, resp):
        return float(resp['ticker']['todaysChangePerc'])
    
