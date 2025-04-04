import os
import schwabdev 
import logging
logger = logging.getLogger(__name__)

class ApiBase:
    def __init__(self):
        self.account_number = os.getenv('ACCOUNT_NUMBER')
        self.app_key = os.getenv('APP_KEY') 
        self.app_secret = os.getenv('APP_SECRET')
        self.cash_to_save = os.getenv('CASH_TO_SAVE')

        if self.account_number is None or self.app_key is None or self.app_secret is None:
            raise ValueError("account number, app key, and app secret environment variables must be present")
        try:
            self.client = schwabdev.Client(self.app_key, self.app_secret)
        except(Exception) as e:
            logger.error("Problem creating client: {}".format(e))
            raise e