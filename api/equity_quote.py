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
    def __init__(self, target_symbol, logger = logger):
        self.price = 0
        self.api_key = os.getenv('EQUITY_API_KEY')
        self.target_symbol = target_symbol
        self.equity_ticker = os.getenv('EQUITY_TICKER', 'SCHB')
        self.logger = logger
        if self.api_key is None:
            raise ValueError("api key must be present")

        self.client = RESTClient(self.api_key)

        self.today831am = datetime.datetime.now().replace(hour=8, minute=31, second=0, microsecond=0)

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
        for i in range(20):
            try:
                now = datetime.datetime.now()
                time_delta_to_831am = now - self.today831am
                minutes_from_831am = round(time_delta_to_831am.seconds / 60)
                now = round(now.timestamp())
        
                from_831_response = requests.get("https://api.polygon.io/v1/indicators/ema/{}?timestamp.gte={}&timespan=minute&adjusted=true&window={}&series_type=close&order=desc&limit=1&apiKey={}".format(self.target_symbol, now, minutes_from_831am, self.api_key))
                while len(from_831_response.json()['results']['values']) == 0:
                    time.sleep(.2)
                    from_831_response = requests.get("https://api.polygon.io/v1/indicators/ema/{}?timestamp.gte={}&timespan=minute&adjusted=true&window={}&series_type=close&order=desc&limit=1&apiKey={}".format(self.target_symbol, now, minutes_from_831am, self.api_key))
                ema_since_831_price = float(self._parse_ema_price(from_831_response.json()))

                from_5_mins_ago_resp = requests.get("https://api.polygon.io/v1/indicators/ema/{}?timestamp.gte={}&timespan=minute&adjusted=true&window={}&series_type=close&order=desc&limit=1&apiKey={}".format(self.target_symbol, now, 5, self.api_key))
                while len(from_5_mins_ago_resp.json()['results']['values']) == 0:
                    time.sleep(.2)
                    from_5_mins_ago_resp = requests.get("https://api.polygon.io/v1/indicators/ema/{}?timestamp.gte={}&timespan=minute&adjusted=true&window={}&series_type=close&order=desc&limit=1&apiKey={}".format(self.target_symbol, now, 5, self.api_key))
                ema_since_5m_price = float(self._parse_ema_price(from_5_mins_ago_resp.json()))

                return self._calculate_percent(ema_since_831_price, ema_since_5m_price)
            except(Exception) as e:
                self.logger.error("Problem requesting currency information: {}".format(e))
                time.sleep(1)

    def _parse_trade_response(self, trade_response):
        return trade_response['results'][0]['price']
        
    def _parse_ema_price(self, ema_response):
        return ema_response['results']['values'][0]['value']
    
    def _calculate_percent(self, ema_since_831_price, ema_since_5m_price):
        return ema_since_5m_price - ema_since_831_price