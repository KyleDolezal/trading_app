import logging
logger = logging.getLogger(__name__)
import os
import statistics
from api.currency_quote import CurrencyClient
import time
from transaction_base import TransactionBase
import datetime

class TransactionTrigger(TransactionBase):
    def __init__(self, test_mode=False, history=[], logger = logger):
        super().__init__(test_mode, history, logger = logger)
    
    def get_action(self, price):
        self.logger.info("Test log")
        self.history.append(price)
        while len(self.history) > self.history_length:
            self.history = self.history[1:]

        percent_difference = self._get_price_difference(price)

        if (datetime.datetime.now() < self.today841am or datetime.datetime.now() > self.today7pm) and not self.test_mode:
            self.running_total = 0
            self.transactions = 0
            return 'hold'
        if datetime.datetime.now() > self.today445pm:
            self.holds_per_override_cent = self.holds_per_override_cent * .9999
        if (self.next_action == 'buy') and \
                (percent_difference > self.change_threshold) and \
                (datetime.datetime.now() < self.today230pm or self.test_mode) and \
                self.running_total >= 0 and \
                self.number_of_holds >= self.blackout_holds and \
                self.transactions <= self.max_transactions and \
                not self._is_down_market():
            self.next_action = 'sell'
            self.transactions += 1
            self.bought_price = price
            self.running_total -= price
            self.number_of_holds = 0
            self.bought_time = datetime.datetime.now()
            return 'buy'
        elif (self.next_action == 'sell') and \
                (percent_difference < self.change_threshold) and \
                abs(percent_difference) > self.change_threshold and \
                (self._preserve_asset_value(price) or self._override_sell_price(price)) :
            self.next_action = 'buy'
            self.cached_checks = self.cached_checks_limit
            self.running_total += price
            self.transactions += 1
            self.number_of_holds = 0
            return 'sell'
        else:
            self.number_of_holds += 1
            return 'hold'
    
    def _override_sell_price(self, price):
        if self.is_down_market:
            status_multiplier = 1 / self.status_multiplier
        else:
            status_multiplier = self.status_multiplier
        override_amount = float(.01 / self.holds_per_override_cent * status_multiplier) * self.number_of_holds
        spread = self.bought_price - price
        spread_override = ((spread - override_amount <= 0) and self._time_elapsed() >= self.override_countdown)
        will_override = self._significant_negative_price_action(price) or \
            spread_override
        if spread_override:
            self.logger.info('Overriding sell behavior for transaction trigger')
        return will_override
    
    def _preserve_asset_value(self, price):
        return (datetime.datetime.now() > self.today445pm) or (price >= self.bought_price) or self.test_preserve_asset_value