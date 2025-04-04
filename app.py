from dotenv import load_dotenv
from orchestrate import Orchestrator
from handle_exit import handle_exit
import logging
import os
logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(filename='logs/app.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    print("Welcome to the trading app. Hit \'q\' to quit.")

    load_dotenv()

    orchestrator = Orchestrator(os.getenv('TARGET_SYMBOL'))

    while True:
        orchestrator.orchestrate()
        handle_exit()

if __name__ == "__main__":
    main()