import logging

import datetime
from pg_adapter import PG_Adapter
logger = logging.getLogger(__name__)


class OrchestratorBase():
    def __init__(self, target_symbol):
        self.pg_adapter = PG_Adapter()

    def record_transaction(self, price, instruction, quantity, order_id):
        sql_string = "insert into trades (order_type, price, timestamp, order_id, quantity, ticker) values ('{}', {}, '{}', {}, '{}', '{}');".format(instruction, 
            price,
            datetime.datetime.now(), 
            order_id,
            quantity,
            self.target_symbol)
        self.pg_adapter.exec_query(sql_string)

    def _bootstrap(self):
        sql_string = "select * from trades where ticker = '{}' order by timestamp desc limit 1;".format(self.target_symbol)
        resp = self.pg_adapter.exec_query(sql_string)
        if resp:
            action = resp[0][0]
            price = resp[0][1]
            if action == 'buy':
                self.waiting_for_action = 'sell'
                self.transaction_trigger.next_action = 'sell'
                self.transaction_trigger.bought_price = float(price[1:])