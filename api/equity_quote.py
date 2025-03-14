import os
import schwabdev 
import logging
logger = logging.getLogger(__name__)
from api.api_base import ApiBase

class EquityClient(ApiBase):
    def __init__(self):
        super().__init__()
        
    def parse_quote(self, quote_response):
        return quote_response['{}'.format(os.getenv('TARGET_SYMBOL'))]['extended']['lastPrice']

    def get_equity_quote(self):
        try:
            response = self.client.quotes(['{}'.format(os.getenv('TARGET_SYMBOL'))]).json()
        except(Exception) as e:
            logger.error("Problem requesting quote information: {}".format(e))
            raise e
        
        return self.parse_quote(response)