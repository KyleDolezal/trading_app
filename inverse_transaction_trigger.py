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
        if ((datetime.datetime.now() < self.today831am or datetime.datetime.now() > self.today7pm)) and not self.test_mode:
            return 'hold'
        elif (percent_difference < self.change_threshold) \
                and abs(percent_difference) > self.change_threshold and \
                (datetime.datetime.now() < self.today230pm or self.test_mode) and \
                self._is_up_market() and \
                self._time_since_snapshot() < 80 and \
                price > (self.currency_client.low + self.limit_value):
            return 'buy'
        else:
            return 'hold'

    def _is_up_market(self):        
        return ((self.currency_client.snapshot <= (self.lower_bound * -1)) and (self.currency_client.snapshot >= (self.upper_bound * -1)) and (self.currency_client.macd_diff < 0) and (self.currency_client.ema_diff < 0) and (self.currency_client.longterm < 0))
