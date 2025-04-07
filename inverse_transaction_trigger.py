import logging
logger = logging.getLogger(__name__)
import os
import statistics
from api.currency_quote import CurrencyClient
import time
from transaction_base import TransactionBase
import datetime

class TransactionTrigger(TransactionBase):
    def __init__(self):
        super().__init__()
    
    def get_action(self, price):
        self.history.append(price)
        if len(self.history) > self.history_length:
            self.history = self.history[1:]

        percent_difference = self._get_price_difference(price)

        if datetime.datetime.now() < self.today830am:
            return 'hold'

        if (self.next_action == 'sell') and \
                (price <= self.bought_price) and \
                (percent_difference > self.change_threshold):
            self.next_action = 'buy'
            return 'sell'
        elif (self.next_action == 'buy') \
                and (percent_difference < self.change_threshold) \
                and abs(percent_difference) > self.change_threshold and \
                (datetime.datetime.now() < self.today230pm) and \
                not self._is_up_market():
            self.next_action = 'sell'
            self.bought_price = price
            return 'buy'
        else:
            return 'hold'