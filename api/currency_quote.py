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

class CurrencyClient:
    def __init__(self, logger=logger):
        self.api_key = os.getenv('CURRENCY_API_KEY', 'api_key')
        self.currency_ticker = os.getenv('CURRENCY_TICKER')
        if self.api_key is None:
            raise ValueError("api key must be present")
        self.price = 0

        self.micro_term_avg_price = 0

        self.short_term_history = []
        self.short_term_avg_price = 0

        self.short_term_history_len = int(os.getenv('SHORT_TERM_HISTORY_LEN', 500))

        self.snapshot = 0.0
        self.timestamp = datetime.datetime.now()

        self.macd_diff = 0.0

        self.ema_diff = 0.0

        self.longterm = 0.0

        self.logger = logger

        self.low = 0.0
        self.high = 0.0

        self.size = []
        self.previous_avg = 0
        self.size_diff = 0

        self.short_size = []
        self.short_previous_avg = 0
        self.short_size_diff = 0

        self.bid_spread = 0

        self.streaming_client = WebSocketClient(
        	api_key=self.api_key,
        	market=Market.Crypto
	    )
        self.streaming_client.subscribe("XQ.{}-USD".format(self.currency_ticker))

        self.threading_update = threading.Thread(target=self.updates)
        self.threading_update.start()

        thread_snap = threading.Thread(target=self.update_snapshot)
        thread_snap.start()

        thread_macd = threading.Thread(target=self.update_macd)
        thread_macd.start()

        thread_ema_diff = threading.Thread(target=self.update_ema_diff)
        thread_ema_diff.start()
    
        thread_longterm = threading.Thread(target=self.update_longterm)
        thread_longterm.start()

        thread_bounds = threading.Thread(target=self.update_bounds)
        thread_bounds.start()

    def updates(self):
        self.streaming_client.run(self.update_price)

    def bootstrapped(self):
        return len(self.short_term_history) >= (self.short_term_history_len - 1)

    def update_size(self, val):
        self.size.append(val)

        if len(self.size) == 25:
            avg = statistics.mean(self.size)
            self.size_diff = avg - self.previous_avg
            self.previous_avg = avg
            self.short_size = []
    
        self.short_size.append(val)

        if len(self.short_size) == 25:
            avg = statistics.mean(self.short_size)
            self.short_size_diff = avg - self.previous_avg
            self.previous_avg = avg
            self.size = []

    def update_ema_diff(self):
        while True:
            try:
                resp = self.get_ema_diff()
                self.ema_diff = resp
            except:
                pass
            time.sleep(1)

    def update_snapshot(self):
        while True:
            try:
                resp = self.get_snapshot()
                self.snapshot = resp['value']
                self.timestamp = (int(resp['timestamp']) / 1000)
            except:
                pass
            time.sleep(1)

    def update_longterm(self):
        while True:
            try:
                resp = self.get_longterm()
                self.longterm = resp['value']
            except:
                pass
            time.sleep(1)
    
    def update_macd(self):
        while True:
            try:
                self.macd_diff = self.get_macd()
            except:
                pass
            time.sleep(1)

    def update_bounds(self):
        while True:
            try:
                resp = self.get_bounds()
                self.low = resp['low']
                self.high = resp['high']
            except:
                pass
            time.sleep(1)

    def update_price(self, msgs: List[WebSocketMessage]):
        for m in msgs:
            price = m.bid_price
            self.update_size(m.ask_size)
            self.update_bid_spread(m.bid_price, m.ask_price)
            self.update_short_term_history(m.bid_price)
            self.update_micro_history_avg()

            while price != self.price:
                self.price = price

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

    def update_bid_spread(self, bid, ask):
        self.bid_spread = ask - bid

    def get_forex_quote(self):
        while self.price == 0:
            time.sleep(1)

        return self.price

    def parse_crypto_response(response):
        return response.json()['last']['price']
  
    def get_snapshot(self):
        response = None
        try:
            response = requests.get("https://api.polygon.io/v1/indicators/rsi/X:{}USD?timespan=minute&window=3&series_type=close&order=desc&limit=1&apiKey={}".format(self.currency_ticker, self.api_key))                       
        except(Exception) as e:
            self.logger.error("Problem requesting rsi information: {}".format(e))
        return self.parse_snapshot(response.json())
    
    def get_longterm(self):
        response = None
        try:
            response = requests.get("https://api.polygon.io/v1/indicators/rsi/X:{}USD?timespan=minute&window=10&series_type=close&order=desc&limit=1&apiKey={}".format(self.currency_ticker, self.api_key))            
        except(Exception) as e:
            self.logger.error("Problem requesting longterm rsi information: {}".format(e))
        return self.parse_snapshot(response.json())

    def parse_snapshot(self, resp):
        return {'value': (float(resp['results']['values'][0]['value']) - 50.0), 'timestamp': resp['results']['values'][0]['timestamp']}
    

    def get_macd(self):
        response = None
        try:
            response = requests.get("https://api.polygon.io/v1/indicators/macd/X:{}USD?timespan=minute&short_window=6&long_window=9&signal_window=4&series_type=close&order=desc&limit=1&apiKey={}".format(self.currency_ticker, self.api_key))        
        except(Exception) as e:
            self.logger.error("Problem requesting macd information: {}".format(e))
        return self.parse_macd(response.json())
    
    def get_bounds(self):
        response = None
        try:
            response = requests.get("https://api.polygon.io/v2/snapshot/locale/global/markets/crypto/tickers/X:{}USD?apiKey={}".format(self.currency_ticker, self.api_key))        
        except(Exception) as e:
            self.logger.error("Problem requesting bounds information: {}".format(e))
        return self.parse_bounds(response.json())

    def get_ema_diff(self):
        response = None
        try:
            ema_response = requests.get("https://api.polygon.io/v1/indicators/ema/X:{}USD?timespan=minute&window=7&series_type=close&order=desc&limit=1&apiKey={}".format(self.currency_ticker, self.api_key)) 
            sma_response = requests.get("https://api.polygon.io/v1/indicators/sma/X:{}USD?timespan=minute&window=7&series_type=close&order=desc&limit=1&apiKey={}".format(self.currency_ticker, self.api_key)) 
            ema_val = self.parse_snapshot(ema_response.json())['value']
            sma_val = self.parse_snapshot(sma_response.json())['value']
            return float(ema_val) - float(sma_val)
        except(Exception) as e:
            self.logger.error("Problem requesting macd information: {}".format(e))
        return self.parse_macd(response.json())
    
    def parse_macd(self, resp):
        return (float(resp['results']['values'][0]['value']) - float(resp['results']['values'][0]['signal']))
            
    def parse_bounds(self, resp):
        high = float(resp['ticker']['day']['h'])
        low = float(resp['ticker']['day']['l'])
        return {'low': low, 'high': high}