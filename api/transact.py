import logging
logger = logging.getLogger(__name__)
from api.api_base import ApiBase
import time
from api.order_status import OrderStatus

class TransactClient(ApiBase):
    def __init__(self):
        super().__init__()
        self.order_status = OrderStatus()
    
    def _transact(self, json):
        order = None
        for i in range(20):
            try:
                order = self.client.order_place(self.account_number, json)
                break
            except(Exception) as e:
                time.sleep(5)
        if order.status_code != 201:
            logger.error("Error with order: {}".format(order.headers))
            logger.error(self.order_status.get_order_id(order))
            logger.error(json)
            return None
        else:
            return order

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

        return self._transact(request_body_json)
    

    def sell(self, quantity, mode, bounds_value):
        bounds_value = round(bounds_value, 2)
        request_body_json = {}
        if mode == 'market':
            request_body_json = {
                "orderType": 'MARKET',
                "session": "NORMAL",
                "duration": "DAY",
                "orderStrategyType": "SINGLE",
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
        else:
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
        
        return self._transact(request_body_json)
        