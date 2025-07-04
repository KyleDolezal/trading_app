import os
import schwabdev 
import time
import logging
logger = logging.getLogger(__name__)
from api.api_base import ApiBase
from api.equity_quote import EquityClient
from pg_adapter import PG_Adapter

class AccountStatus(ApiBase):
    def __init__(self, equity_client, target_symbol, symbols, transaction_trigger):
        super().__init__()
        self.equity_client = equity_client
        self.target_symbol = target_symbol
        self.num_clients = int(os.getenv('NUM_CLIENTS'))
        self.pg_adapter = PG_Adapter()
        self.symbols = symbols
        self.transaction_trigger = transaction_trigger
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
        price = self.equity_client.get_equity_quote(self.target_symbol)
        shares = int(round(self.funds / price, 0))
        if not self.securities_bought() and not self.transaction_trigger._is_down_market() and not self.transaction_trigger._is_up_market():
            shares = round(shares / self.num_clients)
            
        return {"price": price, "shares": shares}
    
    def calculate_sellable_shares(self):
        price = self.equity_client.get_equity_quote(self.target_symbol)
        return int(round(self.position_balance / price, 0))

    def update_positions(self):
        account_status = self.get_account_status()
        self.funds = account_status['tradable_funds']
        self.position_balance = account_status['position_balance']
        if self.position_balance == None:
            self.position_balance = 0
        
    def get_account_status(self):
        response = None
        for i in range(20):
            try:
                response = self.client.account_details(self.account_number, fields='positions').json()
                return self.parse_account_info(response)
            except(Exception) as e:
                logger.error("Problem requesting account information: {}".format(e))
                time.sleep(5)
        
        raise Exception('Problem with getting account status')
    
    def securities_bought(self):
        sql_string = "with trades as ( select row_number() over (partition by ticker order by timestamp desc), * from trades where ticker in ({})) select order_type from trades where row_number = 1;".format(", ".join([f"'{s}'" for s in self.symbols]))
        resp = self.pg_adapter.exec_query(sql_string)
        if resp:
            for action in resp:
                if action[0] == 'buy':
                    return True
        return False

    def get_last_quantity(self):
        sql_string = "with trades as ( select row_number() over (partition by ticker order by timestamp desc), * from trades where ticker = '{}') select quantity from trades where row_number = 1;".format(self.target_symbol)
        resp = self.pg_adapter.exec_query(sql_string)
        try:
            if resp:
                return int(round(resp[0][0]))
        except:
            return 0