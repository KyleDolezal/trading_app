import os
import schwabdev 
import logging
logger = logging.getLogger(__name__)
from api.api_base import ApiBase
from api.equity_quote import EquityClient

class AccountStatus(ApiBase):
    def __init__(self):
        super().__init__()
        self.equity_client = EquityClient()
        self.update_positions()
        
    def parse_account_info(self, account_response):
        current_cash = account_response.get('securitiesAccount').get('currentBalances').get('cashBalance')
        
        dtbp = account_response.get('securitiesAccount').get('currentBalances').get('dayTradingBuyingPower')

        position_balance = None
        for position in account_response.get('securitiesAccount').get('positions'):
            if position.get('instrument').get('symbol') == self.target_symbol:
                position_balance = position.get('marketValue')
        return {
            "tradable_funds": self.calculate_tradable_funds(current_cash, self.cash_to_save, dtbp),
            "position_balance": position_balance
        }

    def calculate_tradable_funds(self, current_cash, cash_to_save, dtbp):
        usable_cash = current_cash - int(float(cash_to_save))
        return min(usable_cash, dtbp)
    
    def calculate_buyable_shares(self):
        price = self.equity_client.get_equity_quote()
        shares = int(round(self.funds / price, 0))
        return {"price": price, "shares": shares}
    
    def calculate_sellable_shares(self):
        price = self.equity_client.get_equity_quote()
        return int(round(self.position_balance / price, 0))

    def update_positions(self):
        account_status = self.get_account_status()
        self.funds = account_status['tradable_funds']
        self.position_balance = account_status['position_balance']
        if self.position_balance == None:
            self.position_balance = 0
        
    def get_account_status(self):
        try:
            response = self.client.account_details(self.account_number, fields='positions').json()
        except(Exception) as e:
            logger.error("Problem requesting account information: {}".format(e))
            raise e
        
        return self.parse_account_info(response)