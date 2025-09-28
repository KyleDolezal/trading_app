import logging

from api.account_status import AccountStatus
from api.order_status import OrderStatus
from api.transact import TransactClient
import time
import datetime
from pg_adapter import PG_Adapter
logger = logging.getLogger(__name__)
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
        if test_mode:
            self.buyable_shares = 1
        else:
            self.buyable_shares = self.account_status.calculate_buyable_shares()['shares']
        if test_mode:
            self.sellable_shares = 1
        else:
            self.sellable_shares = self.account_status.calculate_sellable_shares()
        self.waiting_for_action = 'buy'
        self.today3pm = datetime.datetime.now().replace(hour=15, minute=00, second=0, microsecond=0)
        self.equity_bought_price = 0
        self.limit_id = ''
        self.stop_id = ''

    def orchestrate(self, source_price=None):
        action = self.transaction_trigger.get_action(source_price)
        if source_price == None:
            source_price = self.transaction_trigger.get_price()
        
        if self.waiting_for_action == 'sell':
            self._sell_action(source_price)
        else:
            if self.waiting_for_action == 'buy' and action == 'buy' and self.buyable_shares > 0:
                self._buy_action(source_price)
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
        
    def _sell_action(self, source_price):
        if self.test_mode:
            logger.info('Selling in test mode')
            self.record_transaction(source_price, 'sell', 1, "'test_{}'".format(str(uuid.uuid4())))
            self.waiting_for_action = 'buy'
            self.buyable_shares = 1
        
        else:
            if self.sellable_shares == 0:
                self.sellable_shares = self.buyable_shares
    
            res = self.order_status.await_order_filled([str(self.limit_id), str(self.stop_id)], selloff_check_method=self.transaction_trigger.cancel_selloff)
            if res == None:
                logger.info('Cancelling outstanding sell orders and selling at market due to market conditions')
                self.transact_client.cancel(self.limit_id)
                self.transact_client.cancel(self.stop_id)
                self.transact_client.sell(self.sellable_shares, 'market')
                time.sleep(2)
            
            self.record_transaction(source_price, 'sell', self.sellable_shares, self.limit_id)
            
            self.account_status.update_positions()
            self.buyable_shares = self.account_status.calculate_buyable_shares()['shares']
        self.waiting_for_action = 'buy'

    def handle_contrary_trend(self, order_id):
        if not self.transaction_trigger.last_trend():
            logger.info("Cancelling due to last trend")
            self.transact_client.cancel(order_id)

    def _buy_action(self, source_price=None):
        if self.buyable_shares < 1:
            return
        if self.test_mode:
            logger.info('Buying in test mode')
            self.record_transaction(source_price, 'buy', 1, "'test_{}'".format(str(uuid.uuid4())))
            self.transaction_trigger._diagnostic()
            self.sellable_shares = 1
            self.waiting_for_action = 'sell'
            return            
         
        now = datetime.datetime.now()
        self.equity_client.lastbought = now

        if source_price == None:
            source_price = self.transaction_trigger.get_price()
    
        order = None
        for i in range(20):
            quantity = self.buyable_shares
            try:
                if quantity < 1:
                    return
                order = self.transact_client.buy(self.buyable_shares, self.equity_client.bid_ask_mean(self.target_symbol))
                self.transaction_trigger._diagnostic()
                break
            except(Exception) as e:
                time.sleep(.01)
            if i % 5 == 0:
                self.account_status.update_positions()
                self.buyable_shares = self.account_status.calculate_buyable_shares()['shares']
                time.sleep(5)
        order_id = self.order_status.get_order_id(order)
        self._populate_order_sell_ids(order_id)
        self.handle_contrary_trend(order_id)
        self.equity_bought_price = self.order_status.await_order_filled([order_id], buy_order=True)

        if self.equity_bought_price == None:
            time.sleep(1)
            self.handle_contrary_trend(order_id)
            self.equity_bought_price = self.order_status.await_order_filled([order_id], buy_order=True)

        if self.equity_bought_price == None:    
            self.transact_client.cancel(order_id)
            time.sleep(.025)
            self.account_status.update_positions()
            self.buyable_shares = self.account_status.calculate_buyable_shares()['shares']
            return
        
        self.record_transaction(source_price, 'buy', quantity, order_id)
        self.account_status.update_positions()
        self.sellable_shares = self.account_status.calculate_sellable_shares()
        self.waiting_for_action = 'sell'

    
    def _populate_order_sell_ids(self, buy_id):
        order_id_int_ref = int(buy_id)
        self.limit_id = order_id_int_ref + 2
        self.stop_id = self.limit_id + 1