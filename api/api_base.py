import os
import schwabdev 
import logging
logger = logging.getLogger(__name__)
import pdb

class ApiBase:
    def __init__(self):
        logging.basicConfig(filename='logs/account_status.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        self.account_number = os.getenv('ACCOUNT_NUMBER')
        self.app_key = os.getenv('APP_KEY') 
        self.app_secret = os.getenv('APP_SECRET')
        self.cash_to_save = os.getenv('CASH_TO_SAVE')
        self.target_symbol = os.getenv("TARGET_SYMBOL")

        if self.account_number is None or self.app_key is None or self.app_secret is None:
            raise ValueError("account number, app key, and app secret environment variables must be present")
        try:
            self.client = schwabdev.Client(self.app_key, self.app_secret)
        except(Exception) as e:
            logger.error("Problem creating client", e)
            raise e