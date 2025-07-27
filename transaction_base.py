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
        self.history = history
        self.currency_client = currency_client
        if len(self.history) == 0:
            self._populate_price()
        self.logger = logger

        self.limit_value = float(os.getenv('LIMIT_VALUE', 500))
        self.sales = []
        self.today831am = datetime.datetime.now().replace(hour=8, minute=31, second=0, microsecond=0)
        self.today230pm = datetime.datetime.now().replace(hour=14, minute=30, second=0, microsecond=0)
        self.today445pm = datetime.datetime.now().replace(hour=16, minute=45, second=0, microsecond=0)
        self.today7pm = datetime.datetime.now().replace(hour=19, minute=00, second=0, microsecond=0)

    def _get_price_difference(self, price):
        average = statistics.mean(self.history)
        difference = price - average
        return ((difference/average) * 100)

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