import logging
logger = logging.getLogger(__name__)
import os
import statistics
import time
import datetime
import time

class TransactionBase:
    def __init__(self, test_mode=False, history=[], logger = logger, currency_client=None, target_symbol=None):
        self.test_mode = test_mode
        self.target_symbol= target_symbol
        self.history_length = int(os.getenv('HISTORY_LENGTH'))
        self.change_threshold = float(os.getenv('CHANGE_THRESHOLD'))
        self.lower_bound = float(os.getenv('LOWER_BOUND', 5))
        self.upper_bound = float(os.getenv('UPPER_BOUND', 22))
        self.size_diff = float(os.getenv('SIZE_DIFF', .05))
        self.history = history
        self.currency_client = currency_client
        if len(self.history) == 0:
            self._populate_price()
        self.logger = logger

        self.limit_value = float(os.getenv('LIMIT_VALUE', 500))
        self.sales = []
        self.today831am = datetime.datetime.now().replace(hour=8, minute=31, second=0, microsecond=0)
        self.today245pm = datetime.datetime.now().replace(hour=14, minute=45, second=0, microsecond=0)
        self.ema_diff = 0

    def trending(self, new_diff):
        current_diff = self.ema_diff
        self.ema_diff = new_diff
        return abs(new_diff) >= abs(current_diff)

    def _get_price_difference(self, price):
        average = statistics.mean(self.history)
        difference = price - average
        return ((difference/average) * 100)
    
    def get_short_term_diff(self, price, length=-10):
        return price - self.history[length]
    
    def _time_since_snapshot(self):
        if self.test_mode:
            return 1
        return time.time() - self.currency_client.timestamp

    def _populate_price(self):
        while len(self.history) < self.history_length:
            price = self.currency_client.get_forex_quote()
            self.history.append(price)

    def get_price(self):
        return self.currency_client.price
    
    def _diagnostic(self):
        logger.info("Buy action ----------------")
        logger.info("Size diff: {}".format(self.currency_client.size_diff))
        logger.info("Time since snapshot: {}".format(self._time_since_snapshot()))
        logger.info("Snapshot value: {}".format(self.currency_client.snapshot))
        logger.info("MACD diff: {}".format(self.currency_client.macd_diff))
        logger.info("EMA diff: {}".format(self.currency_client.ema_diff))
        logger.info("Longterm value: {}".format(self.currency_client.longterm))
        logger.info("Shorterm history: {}".format(self.get_short_term_diff(self.get_price())))
        logger.info("---------------------")