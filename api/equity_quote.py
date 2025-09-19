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
        self.volatility_price = 0
        self.unit_test = unit_test
        self.api_key = os.getenv('EQUITY_API_KEY')
        self.currency_ticker = os.getenv('CURRENCY_TICKER')
        self.target_symbol = os.getenv('TARGET_SYMBOL')
        self.inverse_target_symbol = os.getenv('INVERSE_TARGET_SYMBOL')
        self.equity_ticker = os.getenv('EQUITY_TICKER', 'SCHB')
        self.logger = logger

        self.broadbased_snapshot = 0

        self.broadbased_ticker = os.getenv('BROADBASED_TICKER', 'SCHB')

        self.volatility_ticker = os.getenv('VOLATILITY_TICKER', 'SCHB')

        self.reference_ticker = os.getenv('REFERENCE_TICKER')
        self.fixed_income_ticker = os.getenv('FIXED_INCOME_TICKER')

        self.micro_term_avg_price = 0

        self.fixed_snapshot = 0

        self.short_term_history = []
        self.short_term_avg_price = 0

        self.broadbased_history = []
        self.broadbased_average = 0

        self.broadbased_price = 0

        self.lastbought = datetime.datetime.now().replace(hour=7, minute=31, second=0, microsecond=0)

        self.short_term_vol_history = []
        self.short_term_vol_avg_price = 0
        self.micro_term_vol_avg_price = 0

        self.short_term_history_len = int(os.getenv('REFERENCE_SIZE', 3))
        self.history_len = int(os.getenv('HISTORY_LENGTH', 33))

        if test_mode:
            return
        
        if self.api_key is None:
            raise ValueError("api key must be present")

        self.client = RESTClient(self.api_key)

        self.today831am = datetime.datetime.now().replace(hour=8, minute=31, second=0, microsecond=0)

        self.streaming_client = WebSocketClient(
	        api_key=self.api_key,
            feed=Feed.RealTime,
            market=Market.Stocks
	    )
        self.streaming_client.subscribe("Q.{},Q.{},Q.{},Q.{},Q.{}".format(self.target_symbol, self.inverse_target_symbol, self.reference_ticker, self.volatility_ticker, self.broadbased_ticker))

        self.threading_update = threading.Thread(target=self.updates)
        self.threading_update.start()

        self.threading_fixed_update = threading.Thread(target=self.update_fixed_snapshot)
        self.threading_broadbased_update = threading.Thread(target=self.update_broadbased_snapshot)
        self.threading_history_values_update = threading.Thread(target=self.update_price_history_values)
        self.threading_diag = threading.Thread(target=self.show_diagnostic)

        if not self.test_mode:
            self.threading_fixed_update.start()
            self.threading_broadbased_update.start()
            self.threading_history_values_update.start()
            self.threading_diag.start()
   
    def bought_recently(self):
        now = datetime.datetime.now()
        return (abs((self.lastbought - now).total_seconds()) < 15)
    
    def show_diagnostic(self):
        while True:
            if self.bought_recently():
                logger.info("target price: {}".info(self.price))
                logger.info("inverse price: {}".info(self.inverse_price))
            time.sleep(1)

    def vol_history_diff(self):
        return abs(self.short_term_vol_avg_price - self.micro_term_vol_avg_price)

    def update_broadbased_history(self, price):
        self.broadbased_history.append(price)
        if len(self.broadbased_history) > self.history_len:
            self.broadbased_history = self.broadbased_history[1:]
        self.broadbased_average = statistics.mean(self.broadbased_history)

    def broadbased_up(self):
        if len(self.broadbased_history) < 2:
            return False
        return self.broadbased_history[-1] >= statistics.mean(self.broadbased_history)
    
    def broadbased_down(self):
        if len(self.broadbased_history) < 2:
            return False
        return self.broadbased_history[-1] <= statistics.mean(self.broadbased_history)

    def update_fixed_snapshot(self):
        while True:
            val = self.get_fixed_snapshot()
            if val != None:
                self.fixed_snapshot = val['value']

    def update_broadbased_snapshot(self):
        while True:
            val = self.get_broadbased_snapshot()
            if val != None:
                self.broadbased_snapshot = val['value']

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
    
    def update_price_history_values(self):
        while True:
            self.update_short_term_history(self.reference_price)
            self.update_micro_history_avg()
            self.update_short_term_vol_history(self.volatility_price)
            self.update_micro_vol_history_avg()
            self.update_broadbased_history(self.broadbased_price)

    def update_price(self, msgs: List[WebSocketMessage]):
        if self.test_mode:
            return
        for m in msgs:
            if m.symbol == self.target_symbol:
                self.price = m.bid_price
                self.ask_price = m.ask_price
                continue
            elif m.symbol == self.inverse_target_symbol:
                self.inverse_price = m.bid_price
                self.inverse_ask_price = m.ask_price
                continue
            elif m.symbol == self.reference_ticker:
                self.reference_price = m.bid_price
                continue
            elif m.symbol == self.volatility_ticker:
                self.volatility_price = m.bid_price
                continue
            elif m.symbol == self.broadbased_ticker:
                self.broadbased_price = m.bid_price
                continue

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

    def update_micro_vol_history_avg(self):
        micro_len = int(round(self.short_term_history_len / 2, 0))
        if len(self.short_term_vol_history) > micro_len:
            micro_history = self.short_term_vol_history[micro_len:]
            self.micro_term_vol_avg_price = statistics.mean(micro_history)

    def update_short_term_vol_history(self, price):
        self.short_term_vol_history.append(price)
        if len(self.short_term_vol_history) > self.short_term_history_len:
            self.short_term_vol_history = self.short_term_vol_history[1:]
        self.short_term_vol_avg_price = statistics.mean(self.short_term_vol_history)

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

    def get_fixed_snapshot(self):
        response = None
        try:
            response = requests.get("https://api.polygon.io/v1/indicators/rsi/{}?timespan=minute&adjusted=true&window=2&series_type=close&order=desc&limit=10&apiKey={}".format(self.fixed_income_ticker, self.api_key))                       
        except(Exception) as e:
            self.logger.error("Problem requesting rsi information: {}".format(e))
            return None
        return self.parse_rsi_snapshot(response.json())

    def get_broadbased_snapshot(self):
        response = None
        try:
            response = requests.get("https://api.polygon.io/v1/indicators/rsi/{}?timespan=minute&adjusted=true&window=5&series_type=close&order=desc&limit=10&apiKey={}".format(self.broadbased_ticker, self.api_key))                       
        except(Exception) as e:
            self.logger.error("Problem requesting rsi information: {}".format(e))
            return None
        return self.parse_rsi_snapshot(response.json())
    
    def parse_rsi_snapshot(self, resp):
        try:
            if not 'values' in resp['results'].keys():
                return None
            return {'value': (float(resp['results']['values'][0]['value']) - 50.0), 'timestamp': resp['results']['values'][0]['timestamp']}
        except(Exception) as e:
            self.logger.error("Problem requesting rsi information: {}".format(e))
            return None 
    
    