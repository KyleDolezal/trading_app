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
            self.running_total = 0
            return 'hold'
        if (self.next_action == 'buy') and \
                (percent_difference > self.change_threshold) and \
                (datetime.datetime.now() < self.today230pm) and \
                not self._is_down_market():
            self.next_action = 'sell'
            self.bought_price = price
            self.running_total -= price
            self.number_of_holds = 0
            return 'buy'
        elif (self.next_action == 'sell') and ((price >= self.bought_price) or self._override_sell_price(price)) \
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
        override_amount = (.01 / self.holds_per_override_cent) * self.number_of_holds
        spread = self.bought_price - price
        return (override_amount - spread <= 0) and (self.running_total + price >= 0)
    