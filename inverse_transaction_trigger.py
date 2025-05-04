import logging
logger = logging.getLogger(__name__)
import os
import statistics
from api.currency_quote import CurrencyClient
import time
from transaction_base import TransactionBase
import datetime

class InverseTransactionTrigger(TransactionBase):
    def __init__(self, test_mode=False):
        super().__init__(test_mode)
    
    def get_action(self, price):
        self.history.append(price)
        if len(self.history) > self.history_length:
            self.history = self.history[1:]

        percent_difference = self._get_price_difference(price)
        
        if datetime.datetime.now() < self.today830am and not self.test_mode:
            return 'hold'
        
        if datetime.datetime.now() > self.today230pm:
            self.holds_per_override_cent = self.holds_per_override_cent * .99

        if (self.next_action == 'sell') and \
                (self._preserve_asset_value(price) or self._override_sell_price(price)) and \
                (percent_difference > self.change_threshold):
            self.next_action = 'buy'
            return 'sell'
        elif (self.next_action == 'buy') \
                and (percent_difference < self.change_threshold) \
                and abs(percent_difference) > self.change_threshold and \
                (datetime.datetime.now() < self.today230pm or self.test_mode) and \
                not self._is_up_market():
            self.next_action = 'sell'
            self.bought_price = price
            return 'buy'
        else:
            return 'hold'

    def _override_sell_price(self, price):
        override_amount = (.01 / self.holds_per_override_cent) * self.number_of_holds
        spread = self.bought_price - price
        will_override = self._significant_negative_price_action(price) or \
            ((spread - override_amount <= 0) and (self.running_total + price <= 0))

        if will_override:
            logger.info('Overriding sell behavior for inverse transaction trigger')
        return will_override


    def _preserve_asset_value(self, price):
        return self._is_up_market() or (datetime.datetime.now() > self.today230pm) or (price <= self.bought_price) or self.test_preserve_asset_value