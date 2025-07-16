import logging
logger = logging.getLogger(__name__)
import os
import statistics
from api.currency_quote import CurrencyClient
import time
from transaction_base import TransactionBase
import datetime

class TransactionTrigger(TransactionBase):
    def __init__(self, test_mode=False, history=[], logger = logger, currency_client = None,  target_symbol = None):
        super().__init__(test_mode, history, logger = logger, currency_client = currency_client, target_symbol =  target_symbol)
    def get_action(self, price=None):
        if price == None:
            price = self.currency_client.get_forex_quote()
        self.history.append(price)
        while len(self.history) > self.history_length:
            self.history = self.history[1:]

        percent_difference = self._get_price_difference(price)
    
        if ((datetime.datetime.now() < self.today831am or datetime.datetime.now() > self.today7pm)) and not self.test_mode:
            self.running_total = 0
            self.transactions = 0
            return 'hold'

        if (self.next_action == 'buy') and \
                (percent_difference > self.change_threshold) and \
                (datetime.datetime.now() < self.today230pm or self.test_mode) and \
                self.running_total >= 0 and \
                self.number_of_holds >= self.blackout_holds and \
                self.transactions <= self.max_transactions and \
                self._is_up_market() and \
                self._time_since_snapshot() < 80:
            self.next_action = 'sell'
            self.transactions += 1
            self.bought_price = price
            self.running_total -= price
            self.number_of_holds = 0
            self.bought_time = datetime.datetime.now()
            if self.test_mode:
                self.profit -= price
            return 'buy'
        elif (self.next_action == 'sell') and \
                (percent_difference < self.change_threshold) and \
                abs(percent_difference) > self.change_threshold and \
                (self._preserve_asset_value(price) or self._override_sell_price(price)) :
            self.next_action = 'buy'
            self.cached_checks = self.cached_checks_limit
            if self._override_sell_price(price):
                self.running_total += price
            else:
                self.running_total += self.bought_price
            self.transactions += 1
            if self.test_mode:
                self.profit += price
                logger.info('profit for asset: {}'.format(self.profit))
            if self._significant_negative_price_action(price):
                return 'sell override'
            elif self._override_sell_price(price):
                return 'sell spread'
            else:
                self.sales.append(percent_difference)
                return 'sell'
        else:
            self.number_of_holds += 1
            self.keep_market_direction_snapshots_updated()
            self._diagnosis(price)
            return 'hold'
    
    def _override_sell_price(self, price):
        if self._is_down_market():
            status_multiplier = self.status_multiplier
        else:
            status_multiplier = 1 / self.status_multiplier
        override_amount = float(.01 / self.holds_per_override_cent) * self.number_of_holds * status_multiplier
        spread = self.bought_price - price
        spread_override = ((spread - override_amount <= 0) and self._time_elapsed() >= self.override_countdown)
        will_override = self._significant_negative_price_action(price) or \
            spread_override
        if spread_override:
            self.logger.info('Overriding sell behavior for transaction trigger')
            self.is_down_market = True
        return will_override
    
    def _preserve_asset_value(self, price):
        return (datetime.datetime.now() > self.today445pm and not self.test_mode) or (price >= self.bought_price) or self.test_preserve_asset_value
    
    def _is_down_market(self):
        if self.is_down_market == None or self.cached_checks >= self.cached_checks_limit:
            self.is_down_market = self.currency_client.snapshot <= 0
            self.cached_checks = 0
        else:
            self.cached_checks += 1
        return self.is_down_market
        
    def _is_up_market(self):
        if self.is_up_market == None or self.cached_checks >= self.cached_checks_limit:
            self.is_up_market = ((self.currency_client.snapshot >= self.market_direction_threshold) and (self.currency_client.macd_diff > 0) and (self.currency_client.ema_diff > 0) and (self.currency_client.longterm > 0))
            self.cached_checks = 0
        else:
            self.cached_checks += 1
        return self.is_up_market