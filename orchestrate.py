import logging

from api.account_status import AccountStatus
from api.currency_quote import CurrencyClient
from api.order_status import OrderStatus
from api.equity_quote import EquityClient
from api.transact import TransactClient
from transaction_trigger import TransactionTrigger
import time
import datetime
from pg_adapter import PG_Adapter
logger = logging.getLogger(__name__)
import os


class Orchestrator():
    def __init__(self, target_symbol, transaction_trigger, symbols):
        self.target_symbol = target_symbol
        self.pg_adapter = PG_Adapter()
        self.account_status = AccountStatus(EquityClient(target_symbol), target_symbol, symbols, transaction_trigger)
        self.order_status = OrderStatus()
        self.transact_client = TransactClient(target_symbol)
        self.equity_client = EquityClient(target_symbol)
        self.currency_client = CurrencyClient()
        self.transaction_trigger = transaction_trigger
        self.buyable_shares = self.account_status.calculate_buyable_shares()['shares']
        time.sleep(1)
        self.sellable_shares = self.account_status.calculate_sellable_shares()
        self.waiting_for_action = 'buy'
        self._bootstrap()
        self.today3pm = datetime.datetime.now().replace(hour=15, minute=00, second=0, microsecond=0)

    def orchestrate(self, source_price):
        action = self.transaction_trigger.get_action(source_price)

        if action == 'buy' and self.buyable_shares > 0:
            order = None
            for i in range(20):
                try:
                    order = self.transact_client.buy(self.buyable_shares)
                    break
                except(Exception) as e:
                    self.account_status.update_positions()
                    self.buyable_shares = self.account_status.calculate_buyable_shares()['shares']
                    time.sleep(5)
            order_id = self.order_status.get_order_id(order)
            self.order_status.await_order_filled(order_id)
            quantity = self.buyable_shares
            self.record_transaction(source_price, 'buy', quantity, order_id)
            self.waiting_for_action = 'sell'
            self.account_status.update_positions()
            self.sellable_shares = self.account_status.calculate_sellable_shares()
        elif 'sell' in action and self.sellable_shares > 0:
            order = None
            for i in range(20):
                try:
                    if datetime.datetime.now() < self.today3pm:
                        order = self.transact_client.sell(self.sellable_shares, 'MARKET')  
                    else:
                        order = self.transact_client.sell(self.sellable_shares, 'LIMIT', self.equity_client.get_equity_quote())
                    break
                except(Exception) as e:
                    self.account_status.update_positions()
                    self.sellable_shares = self.account_status.calculate_sellable_shares()
                    time.sleep(5)
            order_id = self.order_status.get_order_id(order)
            self.order_status.await_order_filled(order_id)
            quantity = self.sellable_shares
            self.record_transaction(source_price, 'sell', quantity, order_id)
            self.waiting_for_action = 'buy'
            self.account_status.update_positions()
            self.buyable_shares = self.account_status.calculate_buyable_shares()['shares']
        else:
            self._prepare_next_transaction()

        return action

    def _prepare_next_transaction(self):
        if self.waiting_for_action == 'buy':
            self.buyable_shares = self.account_status.calculate_buyable_shares()['shares']
        elif self.waiting_for_action == 'sell':
            self.sellable_shares = self.account_status.calculate_sellable_shares()
            
    def record_transaction(self, price, instruction, quantity, order_id):
        sql_string = "insert into trades (order_type, price, timestamp, order_id, quantity, ticker) values ('{}', {}, '{}', {}, '{}', '{}');".format(instruction, 
            price,
            datetime.datetime.now(), 
            order_id,
            quantity,
            self.target_symbol)
        for i in range(20):
            try:
                self.pg_adapter.exec_query(sql_string)
                return
            except(Exception) as e:
                logger.error("Problem with db txn: {}".format(e))
                time.sleep(5)
        

    def _bootstrap(self):
        sql_string = "select * from trades where ticker = '{}' order by timestamp desc limit 1;".format(self.target_symbol)
        resp = self.pg_adapter.exec_query(sql_string)
        if resp:
            action = resp[0][0]
            price = resp[0][1]
            price = price.replace(',', '')
            if action == 'buy':
                self.waiting_for_action = 'sell'
                self.transaction_trigger.next_action = 'sell'
                self.transaction_trigger.bought_price = float(price[1:])