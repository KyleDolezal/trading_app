import logging
logger = logging.getLogger(__name__)
import os
import statistics
from api.currency_quote import CurrencyClient
import time
from transaction_base import TransactionBase
import datetime

class TransactionTrigger(TransactionBase):
    def __init__(self, test_mode=False):
        super().__init__(test_mode)
    
    def get_action(self, price):
        self.history.append(price)
        if len(self.history) > self.history_length:
            self.history = self.history[1:]

        percent_difference = self._get_price_difference(price)

        if (datetime.datetime.now() < self.today830am or datetime.datetime.now() > self.today7pm) and not self.test_mode:
            self.running_total = 0
            return 'hold'
        if datetime.datetime.now() > self.today230pm:
            self.holds_per_override_cent = self.holds_per_override_cent * .999
        if (self.next_action == 'buy') and \
                (percent_difference > self.change_threshold) and \
                (datetime.datetime.now() < self.today230pm or self.test_mode) and \
                not self._is_down_market():
            self.next_action = 'sell'
            self.bought_price = price
            self.running_total -= price
            self.number_of_holds = 0
            return 'buy'
        elif (self.next_action == 'sell') and (self._preserve_asset_value(price) or self._override_sell_price(price)) \
                and (percent_difference < self.change_threshold) \
                and abs(percent_difference) > self.change_threshold:
            self.next_action = 'buy'
            self.running_total += price
            self.number_of_holds = 0
            return 'sell'
        else:
            self.number_of_holds += 1
            return 'hold'
    
    def _override_sell_price(self, price):
        override_amount = float(.01 / self.holds_per_override_cent) * self.number_of_holds
        spread = self.bought_price - price
        will_override = self._significant_negative_price_action(price) or \
            ((spread - override_amount <= 0) and (self.running_total + price >= 0))
        if will_override:
            logger.info('Overriding sell behavior for transaction trigger')
        return will_override
    
    def _preserve_asset_value(self, price):
        return self._is_down_market() or (datetime.datetime.now() > self.today230pm) or (price >= self.bought_price) or self.test_preserve_asset_value