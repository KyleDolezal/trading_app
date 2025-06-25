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

class App:
    def __init__(self):
        logging.basicConfig(filename='logs/app.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        print("Welcome to the trading app. Hit \'q\' to quit.")
        load_dotenv()

        self.transaction_trigger = TransactionTrigger(logger=logger, test_mode=True)
        self.transaction_trigger.blackout_holds=0
        self.transaction_trigger.today445pm = datetime.datetime.now().replace(hour=23, minute=45, second=0, microsecond=0)
        self.transaction_trigger.today7pm = datetime.datetime.now().replace(hour=23, minute=45, second=0, microsecond=0)

        self.inverse_transaction_trigger = InverseTransactionTrigger(logger=logger, test_mode=True)
        self.inverse_transaction_trigger.blackout_holds=0
        self.inverse_transaction_trigger.today445pm = datetime.datetime.now().replace(hour=23, minute=45, second=0, microsecond=0)
        self.inverse_transaction_trigger.today7pm = datetime.datetime.now().replace(hour=23, minute=45, second=0, microsecond=0)

        self.currency_client = CurrencyClient(logger = logger)


    def orchestrate(self):  
        try:
            while True:
                if self.inverse_transaction_trigger.next_action == 'buy':
                    action = self.transaction_trigger.get_action(self.currency_client.get_forex_quote())
                    if action != 'hold':
                        logger.info('action in transaction trigger: {} value: {}'.format(action, self.currency_client.get_forex_quote()))
        except Exception as e:
            logging.error(e)


    def inverse_orchestrate(self):
        try:
            while True:
                if self.transaction_trigger.next_action == 'buy':
                    action = self.inverse_transaction_trigger.get_action(self.currency_client.get_forex_quote())
                    if action != 'hold':
                        logger.info('action in inverse transaction trigger: {} value: {}'.format(action, self.currency_client.get_forex_quote()))
        except Exception as e:
            logging.error(e)


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
