import os
import logging
logger = logging.getLogger(__name__)
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, Feed, Market
from typing import List
import time
import threading

class IndexClient:
    def __init__(self):
        self.price = 0
        self.api_key = os.getenv('EQUITY_API_KEY')
        self.equity_ticker = os.getenv('INDEX_TICKER')

        if self.api_key is None:
            raise ValueError("api key must be present")

        self.streaming_client = WebSocketClient(
	        api_key=self.api_key,
            market=Market.Indices
	    )
        self.streaming_client.subscribe("V.I:{}".format(self.equity_ticker))

        self.threading_update = threading.Thread(target=self.updates)
        self.threading_update.start()

    def updates(self):
        self.streaming_client.run(self.update_price)

    def update_price(self, msgs: List[WebSocketMessage]):
        for m in msgs:
            self.price = m.value

    def get_equity_quote(self):
        while self.price == 0:
            time.sleep(1)

        return self.price
    