import logging
logger = logging.getLogger(__name__)
import os
import statistics
from api.currency_quote import CurrencyClient
import time
import datetime
from api.equity_quote import EquityClient
from api.index_quote import IndexClient

class TransactionBase:
    def __init__(self, test_mode=False):
        self.test_mode = test_mode
        self.history_length = int(os.getenv('HISTORY_LENGTH'))
        self.change_threshold = float(os.getenv('CHANGE_THRESHOLD'))
        self.history = []
        self.next_action = None
        self.currency_client = CurrencyClient()
        self.is_up_market = None
        self.is_down_market = None
        self.cached_checks = 0
        self.cached_checks_limit = 9
        self.equity_client = EquityClient(os.getenv('TARGET_SYMBOL', 'SCHB'))
        self.index_client = IndexClient()
        self._boot_strap()
        self.bought_price = None
        self.today830am = datetime.datetime.now().replace(hour=8, minute=30, second=0, microsecond=0)
        self.today230pm = datetime.datetime.now().replace(hour=14, minute=30, second=0, microsecond=0)
        self.today7pm = datetime.datetime.now().replace(hour=19, minute=00, second=0, microsecond=0)

        self.running_total = 0
        self.number_of_holds = 0
        self.holds_per_override_cent = float(os.getenv('HOLDS_PER_OVERRIDE_CENT', 100000000000))
        self.market_direction_threshold = float(os.getenv('MARKET_DIRECTION_THRESHOLD'))
        self.quick_selloff_multiplier = float(os.getenv('QUICK_SELLOFF_MULTIPLIER', 10))
        self.test_preserve_asset_value = False
        
    def _get_price_difference(self, price):
        average = statistics.mean(self.history)
        difference = price - average
        return ((difference/average) * 100)
        
    def _boot_strap(self):
        for i in range(self.history_length):
            if self.test_mode:
                self.history.append(0.0)
            else:
                self.history.append(self.currency_client.get_forex_quote())
                time.sleep(.1)
        self.next_action = 'buy'
    
    def _is_down_market(self):
        if self.test_mode:
            return False
        if self.is_down_market == None or self.cached_checks >= self.cached_checks_limit:
            self.is_down_market = self.equity_client.get_snapshot() <= self.market_direction_threshold
            self.cached_checks = 0
        else:
            self.cached_checks += 1
        return self.is_down_market
        
    def _is_up_market(self):
        if self.test_mode:
            return False
        if self.is_up_market == None or self.cached_checks >= self.cached_checks_limit:
            self.is_up_market = self.equity_client.get_snapshot() >= self.market_direction_threshold
            self.cached_checks = 0
        else:
            self.cached_checks += 1
        return self.is_up_market
    
    def _significant_negative_price_action(self, price):
        percent_difference = self._get_price_difference(price)
        will_selloff = abs(percent_difference) > (self.change_threshold * self.quick_selloff_multiplier)
        
        if will_selloff:
            print("quick selloff")
            logger.info("Selling off due to negative price action")

        return will_selloff