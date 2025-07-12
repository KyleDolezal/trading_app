from dotenv import load_dotenv
from orchestrate import Orchestrator
from handle_exit import handle_exit
from transaction_trigger import TransactionTrigger
from inverse_transaction_trigger import InverseTransactionTrigger
from api.equity_quote import EquityClient
import logging
import os
import threading
logger = logging.getLogger(__name__)
from datetime import datetime
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, Feed, Market
from typing import List
from pg_adapter import PG_Adapter
from api.currency_quote import CurrencyClient
import datetime
import time

class App:
    def __init__(self):
        logging.basicConfig(filename='logs/app.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        print("Welcome to the trading app. Hit \'q\' to quit.")
        load_dotenv()

        self.equity_client = EquityClient(logger = logger)

        today841am = datetime.datetime.now().replace(hour=8, minute=41, second=0, microsecond=0)
        while datetime.datetime.now() < today841am:
            pass

        symbols = [os.getenv('TARGET_SYMBOL'), os.getenv('INVERSE_TARGET_SYMBOL')]

        self.quick_selloff_block = int(os.getenv('QUICK_SELLOFF_BLOCK', 10000))
        self.quick_selloff_countdown = 0

        pg_adapter = PG_Adapter()
        
        self.currency_client = CurrencyClient(logger = logger)

        self.transaction_trigger = TransactionTrigger(logger = logger, currency_client = self.currency_client, target_symbol = os.getenv('TARGET_SYMBOL'))
        self.orchestrator = Orchestrator(os.getenv('TARGET_SYMBOL'), self.transaction_trigger, symbols, pg_adapter, logger = logger, equity_client = self.equity_client)

        self.inverse_transaction_trigger = InverseTransactionTrigger(logger = logger, currency_client = self.currency_client, target_symbol = os.getenv('INVERSE_TARGET_SYMBOL'))

        self.inverse_orchestrator = Orchestrator(os.getenv('INVERSE_TARGET_SYMBOL'), self.inverse_transaction_trigger, symbols, pg_adapter, logger = logger, equity_client = self.equity_client)



    def orchestrate(self):
        try:
            while True:
                action = self.orchestrator.orchestrate() 
                self.quick_selloff_countdown += 1
                if action != 'hold':
                    if App.will_override(action, self.quick_selloff_countdown, self.quick_selloff_block):
                        self.quick_selloff_countdown = 0
                        self.transaction_trigger.is_down_market = True
                        self.inverse_orchestrator.buyable_shares = App.get_buyable_shares(self.inverse_orchestrator.account_status.get_last_quantity())
                        self.inverse_orchestrator._buy_action(race_condition=True)
                        time.sleep(2)
                        self.orchestrator.account_status.update_positions()

                    self.inverse_orchestrator.account_status.update_positions()
                    self.inverse_orchestrator.transaction_trigger.invalidate_cache()
                    self.inverse_orchestrator.transaction_trigger.is_down_market = True

                    self.inverse_orchestrator._prepare_next_transaction()
        except Exception as e:
            logging.error(e)


    def inverse_orchestrate(self):
        try:
            while True:
                action = self.inverse_orchestrator.orchestrate()
                self.quick_selloff_countdown += 1
                if action != 'hold':
                    if App.will_override(action, self.quick_selloff_countdown, self.quick_selloff_block):
                        self.quick_selloff_countdown = 0
                        self.inverse_transaction_trigger.is_up_market = True
                        self.orchestrator.buyable_shares = App.get_buyable_shares(self.orchestrator.account_status.get_last_quantity())
                        self.orchestrator._buy_action(race_condition=True)
                        time.sleep(2)
                        self.inverse_orchestrator.account_status.update_positions()

                    self.orchestrator.account_status.update_positions()
                    self.orchestrator.transaction_trigger.invalidate_cache()
                    self.orchestrator.transaction_trigger.is_down_market = True

                    self.orchestrator._prepare_next_transaction()
        except Exception as e:
            logging.error(e)

    def get_buyable_shares(resp):
        return round(resp * .75)
    
    def will_override(action, countdown, selloff_block):
        return action == 'sell override' and countdown >= selloff_block


def main():
    app = App()

    thread_orch = threading.Thread(target=app.orchestrate)
    thread_inverse = threading.Thread(target=app.inverse_orchestrate)

    thread_orch.start()
    thread_inverse.start()

    thread_orch.join()
    thread_inverse.join()

if __name__ == "__main__":
    main()
