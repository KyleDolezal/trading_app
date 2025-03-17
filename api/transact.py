import logging
logger = logging.getLogger(__name__)
from api.api_base import ApiBase

class TransactClient(ApiBase):
    def __init__(self):
        super().__init__()

    def buy(self, quantity):
        request_body_json = {
            "orderType": "MARKET",
            "session": "NORMAL",
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {"instruction": "BUY",
                "quantity": quantity,
                "instrument": {
                    "symbol": self.target_symbol,
                    "assetType": "EQUITY"
                }
                }
            ]
        }

        order = self.client.order_place(self.account_number, request_body_json)

        if order.status_code != 201:
            logger.error("Error with order: {}".format(order.headers))
            raise Exception()
        
        return order

    def sell(self, quantity, mode, bounds_value):
        request_body_json = {
            "orderType": mode,
            "session": "NORMAL",
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "price": bounds_value,
            "orderLegCollection": [
                {"instruction": "SELL",
                "quantity": quantity,
                "instrument": {
                    "symbol": self.target_symbol,
                    "assetType": "EQUITY"
                }
                }
            ]
        }

        order = self.client.order_place(self.account_number, request_body_json)

        if order.status_code != 201:
            logger.error("Error with order: {}".format(order.headers))
            raise Exception()
        
        return order