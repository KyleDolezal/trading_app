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
import statistics

class EquityClient:
    def __init__(self, logger = logger, test_mode = False, unit_test = False):
        self.test_mode = test_mode
        self.price = 0
        self.ask_price = 0
        self.inverse_price = 0
        self.inverse_ask_price = 0
        self.reference_price = 0
        self.unit_test = unit_test
        self.api_key = os.getenv('EQUITY_API_KEY')
        self.currency_ticker = os.getenv('CURRENCY_TICKER')
        self.target_symbol = os.getenv('TARGET_SYMBOL')
        self.inverse_target_symbol = os.getenv('INVERSE_TARGET_SYMBOL')
        self.equity_ticker = os.getenv('EQUITY_TICKER', 'SCHB')
        self.logger = logger

        self.reference_ticker = os.getenv('REFERENCE_TICKER')

        self.micro_term_avg_price = 0

        self.short_term_history = []
        self.short_term_avg_price = 0

        self.short_term_history_len = int(os.getenv('REFERENCE_SIZE', 3))
        
        if self.api_key is None:
            raise ValueError("api key must be present")

        self.client = RESTClient(self.api_key)

        self.today831am = datetime.datetime.now().replace(hour=8, minute=31, second=0, microsecond=0)

        self.streaming_client = WebSocketClient(
	        api_key=self.api_key,
            feed=Feed.RealTime,
            market=Market.Stocks
	    )
        self.streaming_client.subscribe("Q.{},Q.{},Q.{}".format(self.target_symbol, self.inverse_target_symbol, self.reference_ticker))

        self.threading_update = threading.Thread(target=self.updates)
        self.threading_update.start()

    def updates(self):
        if self.test_mode:
            self.price = 1.0
            self.inverse_price = 1.0
        else:
            self.streaming_client.run(self.update_price)

    def bid_ask_mean(self, target_symbol):
        bid_quote = self.get_equity_quote(target_symbol)
        ask_quote = self.get_ask_quote(target_symbol)
        return round(float((bid_quote + ask_quote) / 2), 2)

    def update_price(self, msgs: List[WebSocketMessage]):
        if self.test_mode:
            return
        for m in msgs:
            price = m.bid_price
            if m.symbol == self.target_symbol:
                while self.price != price:
                    self.price = m.bid_price
                while self.ask_price != m.ask_price:
                    self.ask_price = m.ask_price
            if m.symbol == self.inverse_target_symbol:
                while self.inverse_price != price:
                    self.inverse_price = m.bid_price
                while self.inverse_ask_price != m.ask_price:
                    self.inverse_ask_price = m.ask_price
            if m.symbol == self.reference_ticker:
                while self.reference_price != price:
                    self.reference_price = m.bid_price
                    self.update_short_term_history(price)
                    self.update_micro_history_avg()

    def is_down_market(self):
        return self.micro_term_avg_price > self.short_term_avg_price 
    
    def is_up_market(self):
        return self.micro_term_avg_price < self.short_term_avg_price 
    
    def bootstrapped(self):
        return len(self.short_term_history) >= (self.short_term_history_len - 1)

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

    def get_equity_quote(self, symbol):
        if self.test_mode:
            return 1.0
        
        while self.price == 0:
            time.sleep(1)

        if symbol == self.target_symbol:
            return self.price
        elif symbol == self.inverse_target_symbol:
            return self.inverse_price
        else:
            return 0.0
        

    def get_ask_quote(self, symbol):
        if self.test_mode:
            return 2.0
        
        while self.ask_price == 0:
            time.sleep(1)

        if symbol == self.target_symbol:
            return self.ask_price
        elif symbol == self.inverse_target_symbol:
            return self.inverse_ask_price
        else:
            return 0.0
    
    def get_snapshot(self, symbol):
        if self.unit_test:
            return 0
        for i in range(20):
            try:
                if self.test_mode:
                    resp = requests.get("https://api.polygon.io/v2/snapshot/locale/global/markets/crypto/tickers/X:{}USD?apiKey={}".format(self.currency_ticker, self.api_key))
                    raw_percent = resp.json()['ticker']['todaysChangePerc']
                    if symbol == self.target_symbol:
                        return raw_percent
                    else:
                        return raw_percent * -1
                else:
                    now = datetime.datetime.now()
                    time_delta_to_831am = now - self.today831am
                    minutes_from_831am = round(time_delta_to_831am.seconds / 60)
                    now = round(now.timestamp())
            
                    from_831_response = requests.get("https://api.polygon.io/v1/indicators/ema/{}?timestamp.gte={}&timespan=minute&adjusted=true&window={}&series_type=close&order=desc&limit=1&apiKey={}".format(symbol, now, minutes_from_831am, self.api_key))
                    while len(from_831_response.json()['results']['values']) == 0:
                        time.sleep(.2)
                        from_831_response = requests.get("https://api.polygon.io/v1/indicators/ema/{}?timestamp.gte={}&timespan=minute&adjusted=true&window={}&series_type=close&order=desc&limit=1&apiKey={}".format(symbol, now, minutes_from_831am, self.api_key))
                    ema_since_831_price = float(self._parse_ema_price(from_831_response.json()))

                    from_5_mins_ago_resp = requests.get("https://api.polygon.io/v1/indicators/ema/{}?timestamp.gte={}&timespan=minute&adjusted=true&window={}&series_type=close&order=desc&limit=1&apiKey={}".format(symbol, now, 5, self.api_key))
                    while len(from_5_mins_ago_resp.json()['results']['values']) == 0:
                        time.sleep(.2)
                        from_5_mins_ago_resp = requests.get("https://api.polygon.io/v1/indicators/ema/{}?timestamp.gte={}&timespan=minute&adjusted=true&window={}&series_type=close&order=desc&limit=1&apiKey={}".format(symbol, now, 5, self.api_key))
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
        average = (ema_since_5m_price + ema_since_831_price) / 2
        difference = ema_since_5m_price - average
        snapshot = difference * 100
        return snapshot