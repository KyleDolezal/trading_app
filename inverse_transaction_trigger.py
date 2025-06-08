import logging
logger = logging.getLogger(__name__)
import os
import statistics
from api.currency_quote import CurrencyClient
import time
from transaction_base import TransactionBase
import datetime

class InverseTransactionTrigger(TransactionBase):
    def __init__(self, test_mode=False, history=[]):
        super().__init__(test_mode, history)
    
    def get_action(self, price):
        self.history.append(price)
        if len(self.history) > self.history_length:
            self.history = self.history[1:]

        percent_difference = self._get_price_difference(price)
        
        if (datetime.datetime.now() < self.today830am or datetime.datetime.now() > self.today7pm) and not self.test_mode:
            self.running_total = 0
            self.transactions = 0
            return 'hold'
        
        if datetime.datetime.now() > self.today445pm:
            self.holds_per_override_cent = self.holds_per_override_cent * .9999

        if (self.next_action == 'sell') and \
                (percent_difference > self.change_threshold) and \
                (self._preserve_asset_value(price) or self._override_sell_price(price)):
            self.next_action = 'buy'
            self.transactions += 1
            self.number_of_holds = 0
            return 'sell'
        elif (self.next_action == 'buy') \
                and (percent_difference < self.change_threshold) \
                and abs(percent_difference) > self.change_threshold and \
                (datetime.datetime.now() < self.today230pm or self.test_mode) and \
                not self._is_up_market() and \
                self.transactions <= self.max_transactions and \
                self.running_total >= 0:
            self.next_action = 'sell'
            self.running_total -= price
            self.transactions += 1
            self.bought_price = price
            self.number_of_holds = 0
            self.bought_time = datetime.datetime.now()
            return 'buy'
        else:
            self.number_of_holds += 1
            return 'hold'

    def _override_sell_price(self, price):
        if self.is_up_market:
            status_multiplier = 1 / self.status_multiplier
        else:
            status_multiplier = self.status_multiplier
        override_amount = (.01 / self.holds_per_override_cent * status_multiplier) * self.number_of_holds
        spread = price - self.bought_price

        spread_override = ((spread - override_amount <= 0) and self._time_elapsed() >= self.override_countdown)
        will_override = self._significant_negative_price_action(price) or \
            spread_override

        if spread_override:
            logger.info('Overriding sell behavior for inverse transaction trigger')
        return will_override


    def _preserve_asset_value(self, price):
        return self._is_up_market() or (datetime.datetime.now() > self.today230pm) or (price <= self.bought_price) or self.test_preserve_asset_value