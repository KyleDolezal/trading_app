import logging
logger = logging.getLogger(__name__)
from api.api_base import ApiBase
import time
import datetime

class OrderStatus(ApiBase):
    def __init__(self):
        super().__init__()
        self.today655pm = datetime.datetime.now().replace(hour=17, minute=42, second=0, microsecond=0)

    def get_order_id(self, order_resp):
        try:
            return order_resp.headers.get('location', '/').split('/')[-1]
        except(Exception) as e:
            logger.error("Problem parsing order id: {}".format(e))
            raise e
        
    def parse_order_response(self, order_response):
        try:
            price = 0
            if order_response.get('orderActivityCollection'):
                price = round(order_response['orderActivityCollection'][0]['executionLegs'][0]['price'], 2)
            status = order_response.get('status')
            return {"status": status, "price": price}
        except(Exception) as e:
            logger.error("Problem parsing order information: {}".format(e))
            raise e
        
    def get_order_status(self, order_number):
        response = None
        for i in range(20):
            try:
                response = self.client.order_details(self.account_number, order_number).json()
                return self.parse_order_response(response)
            except(Exception) as e:
                logger.error("Problem getting order information: {}".format(e))
                time.sleep(5)
        raise Exception('Problem with getting order status')

    def await_order_filled(self, order_numbers, buy_order = False):
        order_filled = False
        while order_filled != True:
            for order in order_numbers:
                order_info = self.get_order_status(order)
                status = order_info['status']
            
                if status.upper() == 'FILLED':
                    order_filled = True
                    return order_info['price']

                if buy_order:
                    logger.info("initial buy order not filled")
                    return None
                
                time.sleep(2)