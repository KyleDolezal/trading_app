from dotenv import load_dotenv
from handle_exit import handle_exit
import logging
logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(filename='logs/app.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    print("Welcome to the trading app. Hit \'q\' to quit.")

    load_dotenv()

    while True:
        handle_exit()


if __name__ == "__main__":
    main()