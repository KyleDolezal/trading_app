import logging
import threading
logger = logging.getLogger(__name__)
import os
import statistics
import time
import datetime
from api.equity_quote import EquityClient

class TransactionBase:
    def __init__(self, test_mode=False, history=[], logger = logger, currency_client=None, target_symbol=None, equity_client=EquityClient(test_mode=True)):
        self.equity_client = equity_client
        self.test_mode = test_mode
        self.target_symbol= target_symbol
        self.history_length = int(os.getenv('HISTORY_LENGTH'))
        self.change_threshold = float(os.getenv('CHANGE_THRESHOLD'))
        self.lower_bound = float(os.getenv('LOWER_BOUND', 5))
        self.upper_bound = float(os.getenv('UPPER_BOUND', 22))
        self.short_upper_bound = float(os.getenv('SHORT_UPPER_BOUND', 22))
        self.size_diff = float(os.getenv('SIZE_DIFF', .05))
        self.history = history
        self.currency_client = currency_client
        if len(self.history) == 0:
            self._populate_price()
        self.logger = logger
        self.vol_diff_threshold = float(os.getenv('VOL_DIFF_THRESHOLD', .1))

        self.limit_value = float(os.getenv('LIMIT_VALUE', 500))
        self.sales = []
        self.today831am = datetime.datetime.now().replace(hour=8, minute=31, second=0, microsecond=0)
        self.today245pm = datetime.datetime.now().replace(hour=14, minute=45, second=0, microsecond=0)
        self.ema_diff = 0
        self.velocity_threshold = float(os.getenv('VELOCITY_THRESHOLD', 500))
        self.ema_diff_limit = float(os.getenv('EMA_DIFF_LIMIT', 2))
        self.bid_spread_limit = float(os.getenv('BID_SPREAD_LIMIT', 4))
        self.vol_threshold = float(os.getenv('VOL_THRESHOLD', .0125))
        self.size_selloff_threshold_multiplier = float(os.getenv('SIZE_SELLOFF_THRESHOLD_MULTIPLIER', 4))
        self.quick_selloff_threshold = float(os.getenv('QUICK_SELLOFF_THRESHOLD', .1))

        time_731am = datetime.datetime.now().replace(hour=7, minute=31, second=0, microsecond=0)
        self.cancel_criteria = {
            'micro_minus_short': time_731am,
            'equity_snap': time_731am,
            'size': time_731am,
            'equity_direction': time_731am,
            'price_history_direction':  time_731am
        }
        self.broadbased_reference_ratio = {
            "value": .5,
            "timestamp": time_731am,
            "up": False 
        }

        self.quick_selloff_criteria = time_731am

        thread_cancel_criteria = threading.Thread(target=self.update_cancel_sell_attributes)
        if not self.test_mode:
            thread_cancel_criteria.start()
        
        thread_selloff_criteria = threading.Thread(target=self.update_quick_selloff_criteria_task)
        if not self.test_mode:
            thread_selloff_criteria.start()

        thread_ratio = threading.Thread(target=self.update_broadbased_reference_ratio)
        if not self.test_mode:
            thread_ratio.start()

    def update_broadbased_reference_ratio(self):
        if  self.equity_client.short_term_avg_price != 0:
            now = datetime.datetime.now()
            current_ratio = float(self.equity_client.broadbased_average / self.equity_client.short_term_avg_price)
            if self.broadbased_reference_ratio['value'] != current_ratio:
                self.broadbased_reference_ratio = {
                    "value": current_ratio,
                    "up": current_ratio > self.broadbased_reference_ratio['value'],
                    "timestamp": now
                }
        

    def update_cancel_sell_attributes(self):
        while True:
            self.update_cancel_criteria()

    def update_quick_selloff_criteria_task(self):
        while True:
            self.update_quick_selloff_criteria()

    def update_quick_selloff_criteria(self):
        if self.last_trend_by_percent():
            self.quick_selloff_criteria = datetime.datetime.now()
        
    def cancel_selloff(self):
        now = datetime.datetime.now()
        if self.broadbased_selloff() or (abs((self.quick_selloff_criteria - now).total_seconds()) < 5):
            return True
        
        for key in self.cancel_criteria.keys():
            if (abs((self.cancel_criteria[key] - now).total_seconds()) > 15):
                return False
        return True
    
    def broadbased_reference_ratio_up(self):
        now = datetime.datetime.now()
        if (abs((self.broadbased_reference_ratio['timestamp'] - now).total_seconds()) > 7):
            return False
        return self.broadbased_reference_ratio['up']

    def broadbased_reference_ratio_down(self):
        now = datetime.datetime.now()
        if (abs((self.broadbased_reference_ratio['timestamp'] - now).total_seconds()) > 7):
            return False
        return not self.broadbased_reference_ratio['up']
                
    def trending(self, new_diff):
        current_diff = self.ema_diff
        self.ema_diff = new_diff
        return abs(new_diff) <= 5 and abs(current_diff) <= 5
    
    def velocity(self):
        return abs(self.get_micro_price_direction(self.currency_client.micro_term_avg_price))
    
    def price_history_increasing(self):
        return statistics.mean(self.history) >= statistics.mean(self.currency_client.short_term_history)

    def price_history_decreasing(self):
        return statistics.mean(self.history) <= statistics.mean(self.currency_client.short_term_history)

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
        logger.info("---------------------")