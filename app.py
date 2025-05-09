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

class App:
    def __init__(self):
        logging.basicConfig(filename='logs/app.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        print("Welcome to the trading app. Hit \'q\' to quit.")

        load_dotenv()

        symbols = [os.getenv('TARGET_SYMBOL'), os.getenv('INVERSE_TARGET_SYMBOL')]

        self.transaction_trigger = TransactionTrigger()
        self.orchestrator = Orchestrator(os.getenv('TARGET_SYMBOL'), self.transaction_trigger, symbols)

        self.inverse_transaction_trigger = InverseTransactionTrigger()
        self.inverse_orchestrator = Orchestrator(os.getenv('INVERSE_TARGET_SYMBOL'), self.inverse_transaction_trigger, symbols)

        self.source_price = 0

        self.equity_client = EquityClient(os.getenv('TARGET_SYMBOL'))

    def update_price(self, msgs: List[WebSocketMessage]):
        for m in msgs:
            self.source_price = m.price

    def orchestrate(self):
        while True:
            if self.orchestrator.orchestrate(self.source_price) != 'hold':
                self.inverse_orchestrator.account_status.update_positions()
                self.inverse_orchestrator._prepare_next_transaction()

    def inverse_orchestrate(self):
        while True:
            if self.inverse_orchestrator.orchestrate(self.source_price) != 'hold':
                self.orchestrator.account_status.update_positions()
                self.orchestrator._prepare_next_transaction()
    
    def update_prices(self):
        self.equity_client.streaming_client.run(self.update_price)
def main():
    app = App()

    # app.equity_client.streaming_client.run(app.update_price)
    thread_price = threading.Thread(target=app.update_prices)

    thread_orch = threading.Thread(target=app.orchestrate)
    # thread_inverse = threading.Thread(target=app.inverse_orchestrate)

    thread_price.start()
    thread_orch.start()
    # thread_inverse.start()

    thread_price.join()
    thread_orch.join()
    # thread_inverse.join()

if __name__ == "__main__":
    main()
