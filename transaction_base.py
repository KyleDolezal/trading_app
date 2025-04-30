import logging
logger = logging.getLogger(__name__)
import os
import statistics
from api.currency_quote import CurrencyClient
import time
import datetime

class TransactionBase:
    def __init__(self, test_mode=False):
        self.history_length = int(os.getenv('HISTORY_LENGTH'))
        self.change_threshold = float(os.getenv('CHANGE_THRESHOLD'))
        self.history = []
        self.next_action = None
        self.currency_client = CurrencyClient()
        self._boot_strap()
        self.bought_price = None
        self.today830am = datetime.datetime.now().replace(hour=8, minute=30, second=0, microsecond=0)
        self.today230pm = datetime.datetime.now().replace(hour=14, minute=30, second=0, microsecond=0)
        self.running_total = 0
        self.number_of_holds = 0
        self.holds_per_override_cent = int(os.getenv('HOLDS_PER_OVERRIDE_CENT', 100000000000))
        self.test_mode = test_mode
        self.market_direction_threshold = float(os.getenv('MARKET_DIRECTION_THRESHOLD'))
        self.quick_selloff_multiplier = float(os.getenv('QUICK_SELLOFF_MULTIPLIER', 10))
        
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
        if self.test_mode:
            return False
        return self.currency_client.get_snapshot() <= self.market_direction_threshold
        
    def _is_up_market(self):
        if self.test_mode:
            return False
        return self.currency_client.get_snapshot() >= self.market_direction_threshold
    
    def _significant_negative_price_action(self, price):
        percent_difference = self._get_price_difference(price)
        return abs(percent_difference) > (self.change_threshold * self.quick_selloff_multiplier)