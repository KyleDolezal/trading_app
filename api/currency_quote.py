import logging
logger = logging.getLogger(__name__)
import os
import requests
import time

class CurrencyClient:
    def __init__(self):
        self.api_key = os.getenv('CURRENCY_API_KEY')
        self.currency_ticker = os.getenv('CURRENCY_TICKER')

        if self.api_key is None:
            raise ValueError("api key must be present")

    def get_crypto_quote(self):
        response = None
        for i in range(20):
            try:
                response = requests.get("https://api.polygon.io/v1/last/crypto/{}/USD?apiKey={}".format(self.currency_ticker, self.api_key))
            except(Exception) as e:
                logger.error("Problem requesting currency information: {}".format(e))
                time.sleep(1)
        
        if response.json()['status'] != 'success':
            logger.error('Problem getting currency information')
            raise Exception('Problem with currency API')
        
        return CurrencyClient.parse_crypto_response(response)

    def parse_crypto_response(response):
        return response.json()['last']['price']
    
    def get_forex_quote(self):
        response = requests.get("https://api.polygon.io/v1/conversion/{}/USD?amount=1&precision=2&apiKey={}".format(self.currency_ticker, self.api_key))
        
        if response.json()['status'] != 'success':
            logger.error('Problem getting currency information')
            raise Exception('Problem with currency API')
        
        return CurrencyClient.parse_forex_response(response)

    def parse_forex_response(response):
        return response.json()['last']['ask']
