import os
import schwabdev 
import logging
logger = logging.getLogger(__name__)
import pdb
from api_base import ApiBase

class AccountStatus(ApiBase):
    def __init__(self):
        super().__init__()
        
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