import os
import logging
logger = logging.getLogger(__name__)
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, Feed, Market
from typing import List
import time
import threading
import statistics

class IndexClient:
    def __init__(self):
        self.price = 0
        self.api_key = os.getenv('EQUITY_API_KEY')
        self.equity_ticker = os.getenv('INDEX_TICKER')
        self.history_length = int(os.getenv('HISTORY_LENGTH'))

        self.micro_term_avg_price = 0

        self.short_term_history = []
        self.short_term_avg_price = 0

        self.short_term_history_len = int(self.history_length)

        if self.api_key is None:
            raise ValueError("api key must be present")

        self.streaming_client = WebSocketClient(
	        api_key=self.api_key,
            feed=Feed.RealTime,
            market=Market.Indices
	    )
        self.streaming_client.subscribe("A.I:{}".format(self.equity_ticker))

        self.threading_update = threading.Thread(target=self.updates)
        self.threading_update.start()

    def is_down_market(self):
        return self.micro_term_avg_price > self.short_term_avg_price

    def is_up_market(self):
        return self.micro_term_avg_price < self.short_term_avg_price

    def updates(self):
        self.streaming_client.run(self.update_price)

    def update_price(self, msgs: List[WebSocketMessage]):
        for m in msgs:
            self.price = m.close

            self.update_short_term_history(m.close)
            self.update_micro_history_avg()
    
    def update_micro_history_avg(self):
        micro_len = int(round(self.short_term_history_len / 2, 0))
        if len(self.short_term_history) > micro_len:
            micro_history = self.short_term_history[micro_len:]
            self.micro_term_avg_price = statistics.mean(micro_history)

    def update_short_term_history(self, price):
        self.short_term_history.append(price)
        if len(self.short_term_history) > self.short_term_history_len:
            self.short_term_history = self.short_term_history[1:]
        self.short_term_avg_price = statistics.mean(self.short_term_history)
    
    def bootstrapped(self):
        return len(self.short_term_history) >= (self.short_term_history_len - 1)

    def get_equity_quote(self):
        while self.price == 0:
            time.sleep(1)

        return self.price
    