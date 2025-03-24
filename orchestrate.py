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
        self.buyable_shares = self.account_status.calculate_buyable_shares()
        time.sleep(1)
        self.sellable_shares = self.account_status.calculate_sellable_shares()
        self.waiting_for_action = 'buy'

    def orchestrate(self):
        action = self.transaction_trigger.get_action(self.currency_client.get_crypto_quote())

        if action == 'buy':
            order = self.transact_client.buy(self.buyable_shares)
            if order:
                order_id = self.order_status.get_order_id(order)
                self.waiting_for_action = 'sell'
            self.account_status.update_positions()
            self.sellable_shares = self.account_status.calculate_sellable_shares()
        elif 'sell' in action:
            order = self.transact_client.sell(self.sellable_shares, 'MARKET')
            if order:
                order_id = self.order_status.get_order_id(order)
                self.order_status.await_order_filled(order_id)
                self.waiting_for_action = 'buy'
            self.account_status.update_positions()
            self.buyable_shares = self.account_status.calculate_buyable_shares()['shares']
        elif action == 'hold':
            if self.waiting_for_action == 'buy':
                self.buyable_shares = self.account_status.calculate_buyable_shares()['shares']
            elif self.waiting_for_action == 'sell':
                self.sellable_shares = self.account_status.calculate_sellable_shares()

        time.sleep(.2)