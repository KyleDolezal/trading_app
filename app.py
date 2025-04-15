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

    symbols = [os.getenv('TARGET_SYMBOL'), os.getenv('INVERSE_TARGET_SYMBOL')]

    transaction_trigger = TransactionTrigger()
    orchestrator = Orchestrator(os.getenv('TARGET_SYMBOL'), transaction_trigger, symbols)


    inverse_transaction_trigger = InverseTransactionTrigger()
    inverse_orchestrator = Orchestrator(os.getenv('INVERSE_TARGET_SYMBOL'), inverse_transaction_trigger, symbols)

    while True:
        if orchestrator.orchestrate() != 'hold':
            inverse_orchestrator.account_status.update_positions()

        if inverse_orchestrator.orchestrate() != 'hold':
            orchestrator.account_status.update_positions()

        handle_exit()

if __name__ == "__main__":
    main()