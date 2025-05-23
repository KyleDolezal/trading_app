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
        self.streaming_client.subscribe("T.{}".format(self.target_symbol))

        self.threading_update = threading.Thread(target=self.updates)
        self.threading_update.start()

    def updates(self):
        self.streaming_client.run(self.update_price)

    def update_price(self, msgs: List[WebSocketMessage]):
        for m in msgs:
            self.price = m.price

    def get_equity_quote(self):
        while self.price == 0:
            time.sleep(1)

        return self.price
    
    def get_snapshot(self):
        response = None
        for i in range(20):
            try:
                response = requests.get("https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{}?apiKey={}".format(self.target_symbol, self.api_key))
                return self.parse_snapshot(response.json())
            except(Exception) as e:
                logger.error("Problem requesting currency information: {}".format(e))
                time.sleep(1)
    
    def parse_snapshot(self, resp):
        return float(resp['ticker']['todaysChangePerc'])
    