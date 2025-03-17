import logging

from api.account_status import AccountStatus
from api.currency_quote import CurrencyClient
from api.order_status import OrderStatus
from api.equity_quote import EquityClient
from api.transact import TransactClient
from transaction_trigger import TransactionTrigger
logger = logging.getLogger(__name__)
import time

class Orchestrator():
    def __init__(self):
        self.account_status = AccountStatus()
        self.order_status = OrderStatus()
        self.transact_client = TransactClient()
        self.equity_client = EquityClient()
        self.currency_client = CurrencyClient()
        self.transaction_trigger = TransactionTrigger()
        self.bought_price = self.equity_client.get_equity_quote()
        time.sleep(1)
        self.buyable_shares = self.account_status.calculate_buyable_shares()
        time.sleep(1)
        self.sellable_shares = self.account_status.calculate_sellable_shares()
        self.waiting_for_action = 'buy'

    def orchestrate(self):
        action = self.transaction_trigger.get_action(self.currency_client.get_crypto_quote())

        if action == 'buy':
            order = self.transact_client.buy(self.buyable_shares)
            self.order_status.await_order_filled(order)
            self.account_status.update_positions()
            self.sellable_shares = self.account_status.calculate_sellable_shares()
            self.waiting_for_action = 'sell'
        elif action == 'self':
            order = self.transact_client.sell(self.sellable_shares, 'LIMIT', self.bought_price)
            self.order_status.await_order_filled(order)
            self.account_status.update_positions()
            buyable_dict = self.account_status.calculate_buyable_shares()
            self.buyable_shares = buyable_dict['shares']
            self.bought_price = buyable_dict['price']
            self.waiting_for_action = 'buy'
        elif action == 'hold':
            if self.waiting_for_action == 'buy':
                buyable_dict = self.account_status.calculate_buyable_shares()
                self.buyable_shares = buyable_dict['shares']
                self.bought_price = buyable_dict['price']
            elif self.waiting_for_action == 'sell':
                self.sellable_shares = self.account_status.calculate_sellable_shares()

        time.sleep(1)