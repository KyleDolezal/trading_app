import pytest
from transaction_trigger import TransactionTrigger
import os
import datetime
from freezegun import freeze_time
import logging
logger = logging.getLogger(__name__)
from api.equity_quote import EquityClient

response = {"results": [{"price": .00001}], "last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
"timestamp":1741532522429},"request_id":"44ac62cbfdae6adc14158dac0d57ba1a","status":"success",
"symbol":"BTC-USD", "ticker": {"todaysChangePerc": 1}}

down_response = {"results": [{"price": .0001}], "last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
"timestamp":1741532522429},"request_id":"44ac62cbfdae6adc14158dac0d57ba1a","status":"success",
"symbol":"BTC-USD", "ticker": {"todaysChangePerc": -1}}

up_response = {"results": [{"price": 1.0}], "last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
"timestamp":1741532522429},"request_id":"44ac62cbfdae6adc14158dac0d57ba1a","status":"success",
"symbol":"BTC-USD", "ticker": {"todaysChangePerc": 1}}


class MockClient(object):
    def __init__(self):
        self.snapshot = 1
        self.macd_diff = 1
        self.ema_diff = 1
        self.longterm = 5
        self.high = 1000000
        self.size_diff = 0
        self.short_size_diff = 0
        self.short_term_avg_price = 1
        self.bid_spread = 0
        self.micro_term_avg_price = .5
    def bootstrapped(self):
        return True

class MockResponse(object):
    def json(param):
        return response
    
class MockUpResponse(object):
    def json(param):
        return up_response

class MockDownResponse(object):
    def json(param):
        return down_response
    
@freeze_time("2012-01-14 12:21:34")
def test_get_crypto_quote_hold(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)

    os.environ["HISTORY_LENGTH"] = '13'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    
    tt = TransactionTrigger(history=[0], test_mode=True)
    tt.currency_client = MockClient()
    tt.history = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    tt.get_action(10)
    tt.get_action(10)
    assert tt.get_action(10) == 'hold'

def test_is_up_market(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')
    mocker.patch('api.currency_quote.CurrencyClient.__init__', return_value=None)
    mocker.patch('api.equity_quote.EquityClient.get_snapshot', return_value=.1)

    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ["INDEX_TICKER"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'

    tt = TransactionTrigger(history=[0], test_mode=True)
    tt.currency_client = MockClient()
    tt.cached_checks_limit = 100
    tt.currency_client = MockClient()
    tt.is_down_market = False
    tt.market_direction_threshold = -1
    tt.target_symbol = 'SCHB'
    assert tt._is_up_market() == True


@freeze_time("2012-01-14 12:21:34")
def test_get_crypto_quote_buy(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')

    os.environ["HISTORY_LENGTH"] = '13'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.25'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    
    tt = TransactionTrigger(history=[0], test_mode=True)
    tt.currency_client = MockClient()
    tt.cached_checks_limit = 100
    tt.is_up_market = True
    tt.history=[11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11]

    tt.get_action(11)
    assert tt.get_action(13) == 'buy'

def test_trending(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')
    mocker.patch('api.currency_quote.CurrencyClient.__init__', return_value=None)
    mocker.patch('api.equity_quote.EquityClient.get_snapshot', return_value=.1)

    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ["INDEX_TICKER"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'

    tt = TransactionTrigger(history=[0], test_mode=True)
    tt.currency_client = MockClient()
    tt.currency_client = MockClient()
    tt.market_direction_threshold = -1
    tt.target_symbol = 'SCHB'
    tt.ema_diff = 1
    assert tt.trending(1.1111111) == True
    assert tt.trending(-6) == False

@freeze_time("2012-01-14 12:21:34")
def test_price_history_increasing(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')

    os.environ["HISTORY_LENGTH"] = '13'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.25'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    
    tt = TransactionTrigger(history=[0], test_mode=True)
    tt.currency_client = MockClient()
    tt.cached_checks_limit = 100
    tt.is_up_market = True
    tt.history=[11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11]

    tt.price_history_increasing = lambda : False
    assert tt.get_action(13) == 'hold'

    tt.price_history_increasing = lambda : True
    assert tt.get_action(13) == 'buy'

@freeze_time("2012-01-14 12:21:34")
def test_velocity(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')

    os.environ["HISTORY_LENGTH"] = '13'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.25'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    
    tt = TransactionTrigger(history=[0], test_mode=True)
    tt.currency_client = MockClient()
    tt.cached_checks_limit = 100
    tt.is_up_market = True
    tt.history=[11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11]
    tt.velocity_threshold = 99
    tt.velocity = lambda : 100
    assert tt.get_action(13) == 'hold'
    tt.velocity = lambda : 98
    assert tt.get_action(13) == 'buy'