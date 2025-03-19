import os
import logging
logger = logging.getLogger(__name__)
from polygon import RESTClient

class EquityClient:
    def __init__(self):
        self.api_key = os.getenv('EQUITY_API_KEY')
        self.equity_ticker = os.getenv('TARGET_SYMBOL')

        if self.api_key is None:
            raise ValueError("api key must be present")

        self.client = RESTClient(self.api_key)

    def parse_quote(self, quote_response):
        return quote_response.price

    def get_equity_quote(self):
        try:
            response = self.client.get_last_trade(self.equity_ticker)
        except(Exception) as e:
            logger.error("Problem requesting quote information: {}".format(e))
            raise e
        
        return self.parse_quote(response)