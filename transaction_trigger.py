import logging
logger = logging.getLogger(__name__)
import os
import statistics
from api.currency_quote import CurrencyClient
import time
import datetime

class TransactionTrigger:
    def __init__(self):
        self.history_length = int(os.getenv('HISTORY_LENGTH'))
        self.change_threshold = float(os.getenv('CHANGE_THRESHOLD'))
        self.history = []
        self.next_action = None
        self.currency_client = CurrencyClient()
        self._boot_strap()
        self.bought_price = None
        self.today830am = datetime.datetime.now().replace(hour=8, minute=30, second=0, microsecond=0)
        self.today230pm = datetime.datetime.now().replace(hour=14, minute=30, second=0, microsecond=0)
    
    def get_action(self, price):
        self.history.append(price)
        if len(self.history) > self.history_length:
            self.history = self.history[1:]

        percent_difference = self._get_price_difference(price)

        if datetime.datetime.now() < self.today830am:
            return 'hold'

        if (self.next_action == 'buy') and \
                (percent_difference > self.change_threshold) and \
                (datetime.datetime.now() < self.today230pm) and \
                not self._is_down_market():
            self.next_action = 'sell'
            self.bought_price = price
            return 'buy'
        elif (self.next_action == 'sell') and (price >= self.bought_price) \
                and (percent_difference < self.change_threshold) \
                and abs(percent_difference) > self.change_threshold:
            self.next_action = 'buy'
            return 'sell'
        else:
            return 'hold'
        
    def _get_price_difference(self, price):
        average = statistics.mean(self.history)
        difference = price - average
        return ((difference/average) * 100)
        
    def _boot_strap(self):
        for i in range(self.history_length):
            self.history.append(self.currency_client.get_crypto_quote())
            time.sleep(1)

        self.next_action = 'buy'
    
    def _is_down_market(self):
        return self.currency_client.get_snapshot() <= -1
        