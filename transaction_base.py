import logging
logger = logging.getLogger(__name__)
import os
import statistics
from api.currency_quote import CurrencyClient
import time
import datetime
from api.equity_quote import EquityClient
import requests

class TransactionBase:
    def __init__(self, test_mode=False, history=[], logger = logger):
        self.test_mode = test_mode
        self.history_length = int(os.getenv('HISTORY_LENGTH'))
        self.change_threshold = float(os.getenv('CHANGE_THRESHOLD'))
        self.history = history
        self.next_action = None
        self.logger = logger
        self.currency_client = CurrencyClient(logger = self.logger)
        self.is_up_market = None
        self.is_down_market = None
        self.cached_checks = 0
        self.cached_checks_limit = 7500
        self.equity_client = EquityClient(os.getenv('TARGET_SYMBOL', 'SCHB'))
        if test_mode:
            self.equity_client.price = 1.0
        self._boot_strap()
        self.bought_price = None
        self.today841am = datetime.datetime.now().replace(hour=8, minute=41, second=0, microsecond=0)
        self.today230pm = datetime.datetime.now().replace(hour=14, minute=30, second=0, microsecond=0)
        self.today445pm = datetime.datetime.now().replace(hour=16, minute=45, second=0, microsecond=0)
        self.today7pm = datetime.datetime.now().replace(hour=19, minute=00, second=0, microsecond=0)

        self.number_of_holds = 0
        self.holds_per_override_cent = float(os.getenv('HOLDS_PER_OVERRIDE_CENT', 100000000000))
        self.market_direction_threshold = float(os.getenv('MARKET_DIRECTION_THRESHOLD'))
        self.quick_selloff_additional_threshold = float(os.getenv('QUICK_SELLOFF_ADDITIONAL_THRESHOLD', .01))
        self.test_preserve_asset_value = False

        current_asset_value = self.history[-1]
        bootstrap_budget_multiplier = float(os.getenv('BOOSTRAP_BUDGET_MULTIPLIER', .01))
        self.running_total = current_asset_value * bootstrap_budget_multiplier

        self.max_transactions = int(os.getenv('MAX_TRANSACTIONS', 100))
        self.transactions = 0

        self.status_multiplier = int(os.getenv('STATUS_MULTIPLIER', 1))
        self.override_countdown = datetime.timedelta(seconds = int(os.getenv('OVERRIDE_COUNTDOWN', 0)))
        self.bought_time = datetime.datetime.now()

        self.blackout_holds = int(os.getenv('BLACKOUT_HOLDS', 0))

    def _get_price_difference(self, price):
        average = statistics.mean(self.history)
        difference = price - average
        return ((difference/average) * 100)
        
    def _boot_strap(self):
        initial_smoothing_multiplier = 10
        for i in range(self.history_length * initial_smoothing_multiplier):
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
        will_selloff = abs(percent_difference) > (self.change_threshold + self.quick_selloff_additional_threshold)
        
        if will_selloff:
            self.is_down_market = True
            self.is_up_market = True
            print("quick selloff")
            self.logger.info("Selling off due to negative price action")

        return will_selloff
    
    def _time_elapsed(self):
        return datetime.datetime.now() - self.bought_time
    
    def _diagnosis(self, price):
        if self.number_of_holds % 100000 == 0:
            logger.info("------------------v")
            logger.info("Hold for {}".format(self.equity_client.target_symbol))
            logger.info("Price {}".format(price))
            logger.info("Next action {}".format(self.next_action))
            logger.info("Percent difference {}".format(self._get_price_difference(price)))
            logger.info("Running total {}".format(self.running_total))
            logger.info("Up market: {}".format(self._is_up_market()))
            logger.info("Down market: {}".format(self._is_down_market()))
            logger.info("Transactions: {}".format(self.transactions))
            logger.info("Number of holds {}".format(self.number_of_holds))
            logger.info("------------------^")