import logging
logger = logging.getLogger(__name__)
import os
import statistics
import time
import datetime

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
        self.velocity_threshold = float(os.getenv('VELOCITY_THRESHOLD', 500))
        self.ema_diff_limit = float(os.getenv('EMA_DIFF_LIMIT', 2))
        self.bid_spread_limit = float(os.getenv('BID_SPREAD_LIMIT', 4))

    def trending(self, new_diff):
        current_diff = self.ema_diff
        self.ema_diff = new_diff
        return abs(new_diff) <= 5 and abs(current_diff) <= 5
    
    def velocity(self):
        return abs(self.get_micro_price_direction(self.currency_client.micro_term_avg_price))
    
    def price_history_increasing(self):
        history_len = len(self.history)
        bisect_len = int(round(history_len/2,0))

        latter_half_history = self.history[bisect_len:]

        return statistics.mean(latter_half_history) >= statistics.mean(self.history)

    def price_history_decreasing(self):
        history_len = len(self.history)
        bisect_len = int(round(history_len/2,0))

        latter_half_history = self.history[bisect_len:]

        return statistics.mean(latter_half_history) <= statistics.mean(self.history)

    def _get_price_difference(self, price):
        average = statistics.mean(self.history)
        difference = price - average
        return ((difference/average) * 100)
    
    def get_short_price_direction(self, long_price_avg):
        short_avg = statistics.mean(self.history)
        return short_avg - long_price_avg
    
    def get_micro_price_direction(self, micro_price_avg):
        short_avg = statistics.mean(self.history)
        return short_avg - micro_price_avg
    
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
        logger.info("Bid spread: {}".format(self.currency_client.bid_spread))
        logger.info("Size diff: {}".format(self.currency_client.size_diff))
        logger.info("Short diff: {}".format(self.currency_client.short_size_diff))
        logger.info("Velocity: {}".format(self.velocity()))
        logger.info("Price history increasing: {}".format(self.price_history_increasing()))
        logger.info("Price history decreasing: {}".format(self.price_history_decreasing()))
        logger.info("Ceiling: {}".format((self.currency_client.high - self.limit_value)))
        logger.info("Floor: {}".format((self.currency_client.low + self.limit_value)))
        logger.info("Trend: {}".format((self.trend)))
        logger.info("---------------------")