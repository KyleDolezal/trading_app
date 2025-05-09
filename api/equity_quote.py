import os
import logging
logger = logging.getLogger(__name__)
from polygon import RESTClient
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, Feed, Market
from typing import List

class EquityClient:
    def __init__(self, target_symbol):
        self.api_key = os.getenv('EQUITY_API_KEY')
        self.target_symbol = target_symbol
        self.equity_ticker = os.getenv('EQUITY_TICKER', 'SCHB')

        if self.api_key is None:
            raise ValueError("api key must be present")

        self.client = RESTClient(self.api_key)

        self.streaming_client = WebSocketClient(
	    api_key=self.api_key,
            feed=Feed.RealTime,
            market=Market.Stocks
	    )

        self.streaming_client.subscribe("T.{}".format(self.equity_ticker))

    def parse_quote(self, quote_response):
        return quote_response.price

    def get_equity_quote(self):
        try:
            response = self.client.get_last_trade(self.target_symbol)
        except(Exception) as e:
            logger.error("Problem requesting quote information: {}".format(e))
            raise e
        
        return self.parse_quote(response)