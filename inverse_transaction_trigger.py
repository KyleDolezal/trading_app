import logging
logger = logging.getLogger(__name__)
from api.currency_quote import CurrencyClient
from transaction_base import TransactionBase
import datetime
import statistics

class InverseTransactionTrigger(TransactionBase):
    def __init__(self, test_mode=False, history=[], logger = logger, currency_client=None, target_symbol=None, equity_client = None):
        self.equity_client = equity_client
        super().__init__(test_mode, history, logger = logger, currency_client=currency_client,  target_symbol= target_symbol, equity_client=self.equity_client)
    def update_cancel_criteria(self):
        if self.test_mode:
            return
        now = datetime.datetime.now()
        if (abs(self.equity_client.micro_term_vol_avg_price - self.equity_client.short_term_vol_avg_price) > self.vol_threshold):
            self.cancel_criteria['micro_minus_short'] = now
        if (self.equity_client.fixed_snapshot > 0):
            self.cancel_criteria['equity_snap'] = now
        if (self.equity_client.is_up_market()):
            self.cancel_criteria['equity_direction'] = now
        if (self.price_history_increasing()):
            self.cancel_criteria['price_history_direction'] = now
        if (self.size_diff * self.size_selloff_threshold_multiplier) < abs(self.currency_client.size_diff):
            self.cancel_criteria['size'] = now

    def get_action(self, price=None):
        if price == None:
            price = self.currency_client.get_forex_quote()
        self.history.append(price)
        while len(self.history) > self.history_length:
            self.history = self.history[1:]

        if (datetime.datetime.now() < self.today831am) and not self.test_mode:
            return 'hold'
        elif (datetime.datetime.now() < self.today245pm or self.test_mode) and \
                self._is_up_market() and \
                self.size_diff > abs(self.currency_client.size_diff) and \
                self.size_diff > abs(self.currency_client.short_size_diff) and \
                self.size_floor < abs(self.currency_client.size_diff) and \
                (self.test_mode or self.equity_client.vol_history_diff() < self.vol_diff_threshold) and \
                self.currency_client.bootstrapped() and \
                (self.test_mode or self.equity_client.fixed_snapshot > 0) and \
                self.price_history_decreasing() and \
                self.last_trend() and \
                self.broadbased_reference_ratio_down() and \
                (self.test_mode or self.equity_client.bootstrapped()):
            return 'buy'
        else:
            return 'hold'
        
    def last_trend(self):
        return self.history[-1] <= statistics.mean(self.history)
    
    def broadbased_selloff(self):
        return self.broadbased_reference_ratio_up() and (self.test_mode or self.equity_client.vol_history_diff() < self.vol_diff_threshold)
        
    def last_trend_by_percent(self):
        diff = self.history[-1] - self.history[-2]
        percent = (diff / statistics.mean(self.history)) * 100
        return percent > self.quick_selloff_threshold

    def _determine_order_update(self, bought_source_price, bought_equity_bid_price, current_source_price, current_ask_price):
        return bought_source_price > current_source_price and bought_equity_bid_price <= current_ask_price

    def _is_up_market(self):        
        return ((self.currency_client.longterm <= (self.lower_bound * -1)) and (self.currency_client.longterm >= (self.upper_bound * -1)) and (self.currency_client.snapshot <= (self.lower_bound * -1)) and (self.currency_client.snapshot >= (self.short_upper_bound * -1)))