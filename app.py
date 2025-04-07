from dotenv import load_dotenv
from orchestrate import Orchestrator
from handle_exit import handle_exit
from transaction_trigger import TransactionTrigger
from inverse_transaction_trigger import InverseTransactionTrigger
import logging
import os
logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(filename='logs/app.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    print("Welcome to the trading app. Hit \'q\' to quit.")

    load_dotenv()

    transaction_trigger = TransactionTrigger()
    orchestrator = Orchestrator(os.getenv('TARGET_SYMBOL'), transaction_trigger)


    inverse_transaction_trigger = InverseTransactionTrigger()
    inverse_orchestrator = Orchestrator(os.getenv('INVERSE_TARGET_SYMBOL'), inverse_transaction_trigger)

    while True:
        orchestrator.orchestrate()
        inverse_orchestrator.orchestrate()
        handle_exit()

if __name__ == "__main__":
    main()