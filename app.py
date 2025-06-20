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

        today841am = datetime.datetime.now().replace(hour=8, minute=41, second=0, microsecond=0)
        while datetime.datetime.now() < today841am:
            pass

        symbols = [os.getenv('TARGET_SYMBOL'), os.getenv('INVERSE_TARGET_SYMBOL')]

        pg_adapter = PG_Adapter()

        self.transaction_trigger = TransactionTrigger(logger = logger)
        self.orchestrator = Orchestrator(os.getenv('TARGET_SYMBOL'), self.transaction_trigger, symbols, pg_adapter, logger = logger)

        self.inverse_transaction_trigger = InverseTransactionTrigger(logger = logger)

        self.inverse_orchestrator = Orchestrator(os.getenv('INVERSE_TARGET_SYMBOL'), self.inverse_transaction_trigger, symbols, pg_adapter, logger = logger)

        self.currency_client = CurrencyClient(logger = logger)


    def orchestrate(self):
        try:
            while True:
                if self.orchestrator.orchestrate(self.currency_client.get_forex_quote()) != 'hold':
                    self.inverse_orchestrator.account_status.update_positions()
                    self.inverse_orchestrator._prepare_next_transaction()
        except Exception as e:
            logging.error(e)


    def inverse_orchestrate(self):
        try:
            while True:
                if self.inverse_orchestrator.orchestrate(self.currency_client.get_forex_quote()) != 'hold':
                    self.orchestrator.account_status.update_positions()
                    self.orchestrator._prepare_next_transaction()
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
