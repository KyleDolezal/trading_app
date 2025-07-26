import logging

from api.account_status import AccountStatus
from api.order_status import OrderStatus
from api.equity_quote import EquityClient
from api.transact import TransactClient
from transaction_trigger import TransactionTrigger
import time
import datetime
from pg_adapter import PG_Adapter
logger = logging.getLogger(__name__)
import os
import uuid

class Orchestrator():
    def __init__(self, target_symbol, transaction_trigger, symbols, pg_adapter, logger = logger, equity_client = None, test_mode = False):
        self.test_mode = test_mode
        self.target_symbol = target_symbol
        self.pg_adapter = pg_adapter
        self.logger = logger
        self.account_status = AccountStatus(equity_client, target_symbol, symbols, transaction_trigger)
        self.order_status = OrderStatus()
        self.transact_client = TransactClient(target_symbol)
        self.equity_client = equity_client
        self.transaction_trigger = transaction_trigger
        self.buyable_shares = self.account_status.calculate_buyable_shares()['shares']
        time.sleep(1)
        self.sellable_shares = self.account_status.calculate_sellable_shares()
        self.waiting_for_action = 'buy'
        self._bootstrap()
        self.today3pm = datetime.datetime.now().replace(hour=15, minute=00, second=0, microsecond=0)
        self.equity_bought_price = 0
        self.limit_id = ''
        self.stop_id = ''

    def orchestrate(self, source_price=None):
        action = self.transaction_trigger.get_action(source_price)
        if source_price == None:
            source_price = self.transaction_trigger.get_price()
        
        if 'sell' in action and not self.test_mode and self.sellable_shares == 0:
            self.account_status.update_positions()
            self.sellable_shares = self.account_status.calculate_sellable_shares()

        if action == 'buy' and self.buyable_shares > 0:
            self._buy_action(source_price)
        elif 'sell' in action and (self.sellable_shares > 0  or self.test_mode):
            if self.test_mode:
                logger.info('Selling in test mode')
                self.record_transaction(source_price, 'sell', 1, "'test_{}'".format(str(uuid.uuid4())))
                self.waiting_for_action = 'buy'
                self.buyable_shares = 1
            else:
                # order = None
                # for i in range(20):
                #     try:
                #         if datetime.datetime.now() < self.today3pm and (action == 'sell override' or action == 'sell spread'):
                #             order = self.transact_client.sell(self.sellable_shares, 'MARKET')  
                #         else:
                #             sell_price = self.equity_client.get_equity_quote(self.target_symbol)
                #             if self.equity_bought_price != None and self.equity_bought_price > 0:
                #                 sell_price = self.equity_bought_price
                #             order = self.transact_client.sell(self.sellable_shares, 'LIMIT', sell_price)
                #         break
                #     except(Exception) as e:
                #         self.account_status.update_positions()
                #         self.sellable_shares = self.account_status.calculate_sellable_shares()
                #         time.sleep(5)
                # order_id = self.order_status.get_order_id(order)
                self.order_status.await_order_filled([str(self.limit_id), str(self.stop_id)])
                quantity = self.sellable_shares
                self.record_transaction(source_price, 'sell', quantity, self.limit_id)
                self.account_status.update_positions()
                self.buyable_shares = self.account_status.calculate_buyable_shares()['shares']
            self.waiting_for_action = 'buy'
            self.transaction_trigger.number_of_holds = 0
        else:
            if not self.test_mode:
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
                self.logger.error("Problem with db txn: {}".format(e))
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

    def _buy_action(self, source_price=None, race_condition=False):
        self.transaction_trigger.next_action = 'hold'

        if source_price == None:
            source_price = self.transaction_trigger.get_price()
        
        if self.buyable_shares < 1:
            return
            
        if self.test_mode:
            logger.info('Buying in test mode')
            self.record_transaction(source_price, 'buy', 1, "'test_{}'".format(str(uuid.uuid4())))
          
            self.sellable_shares = 1
        else:
            order = None
            for i in range(20):
                quantity = self.buyable_shares
                try:
                    order = self.transact_client.buy(self.buyable_shares, self.equity_client.get_equity_quote(self.target_symbol))
                    break
                except(Exception) as e:
                    time.sleep(.01)
                if i % 5 == 0:
                    self.account_status.update_positions()
                    self.buyable_shares = self.account_status.calculate_buyable_shares()['shares']
                    time.sleep(5)
            order_id = self.order_status.get_order_id(order)
            order_id_int_ref = int(order_id)
            self.limit_id = order_id_int_ref + 1
            self.stop_id = self.limit_id + 1
            self.equity_bought_price = self.order_status.await_order_filled([order_id])

            if self.equity_bought_price == -1:
                self.waiting_for_action = 'buy'
                self.transaction_trigger.next_action = 'buy'
                self.equity_bought_price = self.equity_client.price
                return

            if self.equity_bought_price == 0:
                self.equity_bought_price = self.equity_client.price
            self.record_transaction(source_price, 'buy', quantity, order_id)
            self.account_status.update_positions()
            self.sellable_shares = self.account_status.calculate_sellable_shares()
        
        if race_condition:
            time.sleep(10)
            self.transaction_trigger._boot_strap()
        
        if self.equity_bought_price > -1:
            self.waiting_for_action = 'sell'
            self.transaction_trigger.next_action = 'sell'
            self.transaction_trigger.number_of_holds = 0
            self.transaction_trigger.bought_price = source_price
            self.transaction_trigger.bought_time = datetime.datetime.now()