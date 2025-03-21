import logging
logger = logging.getLogger(__name__)
from api.api_base import ApiBase
import time
import pdb

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
            price = order_response['orderActivityCollection'][0]['executionLegs'][0]['price']
            status = order_response.get('status')
            return {"status": status, "price": price}
        except(Exception) as e:
            logger.error("Problem parsing order information: {}".format(e))
            raise e
        
    def get_order_status(self, order_number):
        try:
            response = self.client.order_details(self.account_number, order_number).json()

            return self.parse_order_response(response)
        except(Exception) as e:
            logger.error("Problem getting order information: {}".format(e))
        
    def await_order_filled(self, order_number):
        order_filled = False
        while order_filled != True:
            order_info = self.get_order_status(order_number)
            status = order_info['status']
           
            if status.upper() == 'FILLED':
                order_filled = True
                return order_info['price']

            time.sleep(1)