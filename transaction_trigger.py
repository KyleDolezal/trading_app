import logging
logger = logging.getLogger(__name__)
from api.currency_quote import CurrencyClient
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
    
        if (datetime.datetime.now() < self.today831am) and not self.test_mode:
            return 'hold'

        if (percent_difference > self.change_threshold) and \
                (datetime.datetime.now() < self.today245pm or self.test_mode) and \
                self._is_up_market() and \
                self._time_since_snapshot() < 120 and \
                self.size_diff > abs(self.currency_client.size_diff) and \
                self.get_short_term_diff(price) >= 0 and \
                self.currency_client.bid_spread < 5 and \
                self.trending(self.currency_client.ema_diff) and \
                price < (self.currency_client.high - self.limit_value):
            return 'buy'
        else:
            return 'hold'
    

    def _is_up_market(self):
        return ((self.currency_client.snapshot >= self.lower_bound) and (self.currency_client.snapshot <= self.upper_bound) and (self.currency_client.macd_diff > 0) and (self.currency_client.ema_diff > 0) and (self.currency_client.longterm > 0))