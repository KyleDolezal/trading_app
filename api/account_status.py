import os
import schwabdev 
import logging
logger = logging.getLogger(__name__)
import pdb

class AccountStatus:
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
        
    def parse_account_info(self, account_response):
        current_cash = account_response.get('securitiesAccount').get('currentBalances').get('cashBalance')
        
        dtbp = account_response.get('securitiesAccount').get('currentBalances').get('dayTradingBuyingPower')

        for position in account_response.get('securitiesAccount').get('positions'):
            if position.get('instrument').get('symbol') == self.target_symbol:
                position_balance = position.get('marketValue')

        return {
            "tradable_funds": self.calculate_tradable_funds(current_cash, self.cash_to_save, dtbp),
            "position_balance": position_balance
        }

    def calculate_tradable_funds(self, current_cash, cash_to_save, dtbp):
        usable_cash = current_cash - int(cash_to_save)
        return min(usable_cash, dtbp)
        
    def get_account_status(self):
        try:
            response = self.client.account_details(self.account_number, fields='positions').json()
        except(Exception) as e:
            logger.error("Problem requesting account information", e)
            raise e
        
        return self.parse_account_info(response)