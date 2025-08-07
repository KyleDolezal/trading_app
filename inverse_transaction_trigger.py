import logging
logger = logging.getLogger(__name__)
from api.currency_quote import CurrencyClient
from transaction_base import TransactionBase
import datetime

class InverseTransactionTrigger(TransactionBase):
    def __init__(self, test_mode=False, history=[], logger = logger, currency_client=None, target_symbol=None):
        super().__init__(test_mode, history, logger = logger, currency_client=currency_client,  target_symbol= target_symbol)
    
    def get_action(self, price=None):
        if price == None:
            price = self.currency_client.get_forex_quote()
        self.history.append(price)
        while len(self.history) > self.history_length:
            self.history = self.history[1:]

        percent_difference = self._get_price_difference(price)
        if (datetime.datetime.now() < self.today831am) and not self.test_mode:
            return 'hold'
        elif (percent_difference < self.change_threshold) \
                and abs(percent_difference) > self.change_threshold and \
                (datetime.datetime.now() < self.today245pm or self.test_mode) and \
                self._is_up_market() and \
                self._time_since_snapshot() < 180 and \
                self.size_diff > abs(self.currency_client.size_diff) and \
                self.size_diff > abs(self.currency_client.short_size_diff) and \
                self.currency_client.bid_spread < 4 and \
                self.get_short_price_direction(self.currency_client.short_term_avg_price) < 0 and \
                self.get_micro_price_direction(self.currency_client.micro_term_avg_price) < 0 and \
                self.currency_client.bootstrapped() and \
                not self.price_history_increasing() and \
                self.velocity() < self.velocity_threshold and \
                price > (self.currency_client.low + self.limit_value):
            return 'buy'
        else:
            return 'hold'

    def _determine_order_update(self, bought_source_price, bought_equity_bid_price, current_source_price, current_ask_price):
        return bought_source_price > current_source_price and bought_equity_bid_price <= current_ask_price

    def _is_up_market(self):        
        return ((self.currency_client.longterm <= (self.lower_bound * -1)) and (self.currency_client.longterm >= (self.upper_bound * -1)) and (self.currency_client.macd_diff < 0) and (self.currency_client.ema_diff < self.ema_diff_limit) and (self.currency_client.snapshot < 0))
