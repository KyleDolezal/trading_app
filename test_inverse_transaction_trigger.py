import logging
logger = logging.getLogger(__name__)
import pytest
from inverse_transaction_trigger import InverseTransactionTrigger
import os
import datetime
from api.equity_quote import EquityClient
from freezegun import freeze_time

response = {"results": [{"price": 1.0}], "last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
"timestamp":1741532522429},"request_id":"44ac62cbfdae6adc14158dac0d57ba1a","status":"success",
"symbol":"BTC-USD", "ticker": {"todaysChangePerc": 1}}

down_response = {"results": [{"price": 1.0}], "last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
"timestamp":1741532522429},"request_id":"44ac62cbfdae6adc14158dac0d57ba1a","status":"success",
"symbol":"BTC-USD", "ticker": {"todaysChangePerc": -1}}

up_response = {"results": [{"price": 9999999999999999999.0}], "last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
"timestamp":1741532522429},"request_id":"44ac62cbfdae6adc14158dac0d57ba1a","status":"success",
"symbol":"BTC-USD", "ticker": {"todaysChangePerc": 1}}

class MockResponse(object):
    def json(param):
        return response
    
class MockUpResponse(object):
    def json(param):
        return up_response

class MockDownResponse(object):
    def json(param):
        return down_response

class MockMarketDown(object):
    def _is_up_market():
        return False

class MockClient(object):
    def __init__(self):
        self.snapshot = -5
        self.timestamp = 123
        self.macd_diff = -1
        self.ema_diff = -1
        self.longterm = -5
        self.low = -502
        self.size_diff = 0
        self.short_size_diff = 0
        self.bid_spread = 0
        self.short_term_avg_price = 100
        self.fixed_snapshot = 1
        self.micro_term_avg_price = 200
        self.short_term_history = [100, 100, 100]
        self.short_term_vol_avg_price = 100
        self.micro_term_vol_avg_price = 100
    def bootstrapped(self):
        return True
    def get_fixed_snapshot(self):
        return 10
    def is_up_market(self):
        return True
    def is_down_market(self):
        return True


class MockIndexClient(object):
    def __init__(self):
        self.snapshot = -5
        self.timestamp = 123
        self.macd_diff = -1
        self.ema_diff = -1
        self.longterm = -5
        self.low = -502
        self.size_diff = 0
        self.short_size_diff = 0
        self.bid_spread = 0
        self.short_term_avg_price = 100
        self.micro_term_avg_price = 200
        self.short_term_history = [100, 100, 100]
    def bootstrapped(self):
        return True
    def is_down_market(self):
        return True

@freeze_time("2012-01-14 12:21:34")
def test_get_crypto_quote_buy(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.equity_quote.EquityClient.get_snapshot', return_value=.1)
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.WebSocketClient')

    os.environ["HISTORY_LENGTH"] = '11'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    
    tt = InverseTransactionTrigger(history=[0], test_mode=True)
    tt.currency_client = MockClient()
    tt.index_client = MockIndexClient()
    tt.history=[12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12]

    assert tt.get_action(10.016) == 'buy'


@freeze_time("2012-01-14 12:21:34")
def test_price_history_decreasing(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.equity_quote.EquityClient.get_snapshot', return_value=.1)
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.WebSocketClient')

    os.environ["HISTORY_LENGTH"] = '11'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    
    tt = InverseTransactionTrigger(history=[0], test_mode=True)
    tt.currency_client = MockClient()
    tt.index_client = MockIndexClient()
    tt.history=[12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12]
    tt.price_history_decreasing = lambda : False
    assert tt.get_action(10.016) == 'hold'

    tt.price_history_decreasing = lambda : True
    assert tt.get_action(10.016) == 'buy'

@freeze_time("2012-01-14 12:21:34")
def test_get_crypto_quote_hold(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.WebSocketClient')
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["CURRENCY_API_KEY"] = 'key'
    
    tt = InverseTransactionTrigger(history=[0], test_mode=True)
    tt.currency_client = MockClient()
    tt.is_up_market = False
    tt.get_action(10)
    tt.get_action(10)
    assert tt.get_action(10.01) == 'hold'

def test_is_up_market(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.equity_quote.EquityClient.get_snapshot', return_value=.1)
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')


    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["CURRENCY_API_KEY"] = 'key'

    tt = InverseTransactionTrigger(history=[0], test_mode=True)
    tt.currency_client = MockClient()
    tt.cached_checks_limit = 100
    tt.currency_client.snapshot = -5.0
    tt.market_direction_threshold = -.1
    tt.target_symbol = 'SCHB'
    assert tt._is_up_market() == True


@freeze_time("2012-01-14 12:21:34")
def test_cancel_selloff(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.WebSocketClient')

    os.environ["HISTORY_LENGTH"] = '13'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.25'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    
    tt = InverseTransactionTrigger(history=[0], test_mode=True)
    tt.equity_client = MockClient()
    tt.currency_client = MockClient()
    tt.equity_client.micro_term_vol_avg_price = 100
    tt.equity_client.micro_term_vol_avg_price = 1
    tt.short_term_vol_avg_price = 1
    tt.vol_threshold = 1
    tt.history = [1, 2, 3, 4]

    tt.currency_client.size_diff = 100
   
    assert tt.cancel_selloff() == False

    tt = InverseTransactionTrigger(history=[0], test_mode=True)
    tt.equity_client = MockClient()
    tt.currency_client = MockClient()
    tt.equity_client.micro_term_vol_avg_price = 10000000
    tt.equity_client.micro_term_vol_avg_price = 10000000
    tt.short_term_vol_avg_price = 1
    tt.vol_threshold = 1
    tt.history = [5, 4, 3, 2]
    tt.currency_client.short_term_history=[0]
    tt.currency_client.size_diff = 100
    tt.test_mode = False
    tt.cancel_criteria = {'key': datetime.datetime.now()}
    assert tt.cancel_selloff() == True