import logging
logger = logging.getLogger(__name__)
from api_base import ApiBase

class OrderStatus(ApiBase):
    def __init__(self):
        super().__init__()

    def get_order_id(self, order_resp):
        try:
            return order_resp.headers.get('location', '/').split('/')[-1]
        except(Exception) as e:
            logger.error("Problem parsing order id: {}".format(e))
            raise e
        
    def parse_order_response(self, order_response):
        try:
            return order_response.get('status')
        except(Exception) as e:
            logger.error("Problem parsing order information: {}".format(e))
            raise e
        
    def get_order_status(self, order_number):
        try:
            response = self.client.order_details(self.account_number, order_number).json()

            return self.parse_order_response(response)
        except(Exception) as e:
            logger.error("Problem getting order information: {}".format(e))
            raise e