import logging
logger = logging.getLogger(__name__)
import os
import statistics
from api.currency_quote import CurrencyClient
import time

class TransactionTrigger:
    def __init__(self):
        self.history_length = int(os.getenv('HISTORY_LENGTH'))
        self.change_threshold = float(os.getenv('CHANGE_THRESHOLD'))
        self.history = []
        self.next_action = None
        self._boot_strap()
    
    def get_action(self, price):
        self.history.append(price)
        if len(self.history) > self.history_length:
            self.history = self.history[1:]

        average = statistics.mean(self.history)

        difference = price - average
        percent_difference = (difference/average) * 100

        if (self.next_action == 'buy') and (percent_difference > self.change_threshold):
            self.next_action = 'sell'
            return 'buy'
        elif (self.next_action == 'sell') and (percent_difference < self.change_threshold) and abs(percent_difference) > self.change_threshold:
            self.next_action = 'buy'
            if abs(percent_difference) > (self.change_threshold * 5):
                return 'sell_market'
            else:
                return 'sell'
        else:
            return 'hold'
        
    def _boot_strap(self):
        currency_client = CurrencyClient()

        for i in range(self.history_length):
            self.history.append(currency_client.get_crypto_quote())
            time.sleep(1)

        self.next_action = 'buy'

        