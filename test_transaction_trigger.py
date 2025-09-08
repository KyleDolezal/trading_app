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
        self.broadbased_snapshot = 0
        self.broadbased_up_val = True
    def bootstrapped(self):
        return True
    def is_up_market(self):
        return True
    def broadbased_up(self):
        return self.broadbased_up_val

class MockClient(object):
    def __init__(self):
        self.snapshot = 5
        self.macd_diff = 1
        self.ema_diff = 1
        self.longterm = 5
        self.high = 1000000
        self.size_diff = 0
        self.short_size_diff = 0
        self.short_term_avg_price = 1
        self.fixed_snapshot = -1
        self.bid_spread = 0
        self.micro_term_avg_price = .5
        self.short_term_history = [1, 1, 1]
        self.short_term_vol_avg_price = 100
        self.micro_term_vol_avg_price = 100
        self.broadbased_snapshot = 0
        self.broadbased_up_val = True

    def bootstrapped(self):
        return True
    def get_fixed_snapshot(self):
        return -10
    def vol_history_diff(self):
        return 0
    def is_up_market(self):
        return True
    def is_down_market(self):
        return True
    def broadbased_up(self):
        return self.broadbased_up_val

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
    tt.index_client = MockIndexClient()
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
    tt.index_client = MockIndexClient()
    tt.short_upper_bound = 1
    assert tt._is_up_market() == False
    tt.short_upper_bound = 20
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
    tt.index_client = MockIndexClient()
    tt.history=[11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11]
    tt.broadbased_reference_ratio = {"up": True, "value": 1, "timestamp": datetime.datetime.now()}
    tt.get_action(11)
    assert tt.get_action(13) == 'buy'


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
    tt.index_client = MockIndexClient()
    tt.history=[11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11]

    tt.price_history_increasing = lambda : False
    assert tt.get_action(13) == 'hold'

    tt.price_history_increasing = lambda : True
    tt.broadbased_reference_ratio = {"up": True, "value": 1, "timestamp": datetime.datetime.now()}
    assert tt.get_action(13) == 'buy'

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
    
    tt = TransactionTrigger(history=[0], test_mode=True)
    tt.equity_client = MockClient()
    tt.currency_client = MockClient()
    tt.equity_client.micro_term_vol_avg_price = 100
    tt.equity_client.micro_term_vol_avg_price = 1
    tt.short_term_vol_avg_price = 1
    tt.vol_threshold = 1
    tt.history = [1, 2, 3, 4]

    tt.currency_client.size_diff = 100
   
    assert tt.cancel_selloff() == False

    tt = TransactionTrigger(history=[0], test_mode=True)
    tt.equity_client = MockClient()
    tt.currency_client = MockClient()
    tt.equity_client.micro_term_vol_avg_price = 100
    tt.equity_client.micro_term_vol_avg_price = 1
    tt.short_term_vol_avg_price = 1
    tt.vol_threshold = 1
    tt.history = [5, 4, 3, 2]
    tt.currency_client.short_term_history=[2100]
    tt.currency_client.size_diff = 100
    tt.test_mode = False
    tt.cancel_criteria = {'key': datetime.datetime.now()}
    assert tt.cancel_selloff() == True


@freeze_time("2012-01-14 12:21:34")
def test_last_trend(mocker):
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
    tt.velocity = lambda : 98
    tt.broadbased_reference_ratio = {"up": True, "value": 1, "timestamp": datetime.datetime.now()}
    assert tt.get_action(13) == 'buy'
    tt.last_trend = lambda : False
    assert tt.get_action(13) == 'hold'


@freeze_time("2012-01-14 12:21:34")
def test_last_trend_by_percent(mocker):
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
    tt.quick_selloff_threshold = 1
    tt.history=[11, 11, 11, 10]
    assert tt.last_trend_by_percent() == True
    tt.history=[11, 11, 11, 12]
    assert tt.last_trend_by_percent() == False


@freeze_time("2012-01-14 12:21:34")
def test_quick_selloff(mocker):
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
    tt.equity_client = MockClient()
    tt.currency_client = MockClient()
    tt.cached_checks_limit = 100
    tt.is_up_market = True
    tt.history=[11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11]
    assert tt.cancel_selloff() == False
    tt.history=[11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 8]
    tt.update_quick_selloff_criteria()
    assert tt.cancel_selloff() == True
    
@freeze_time("2012-01-14 12:21:34")
def test_broadbased_selloff(mocker):
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
    tt.equity_client = MockClient()
    tt.currency_client = MockClient()
    tt.cached_checks_limit = 100
    tt.is_up_market = True
    tt.history=[11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 8]
    tt.equity_client.broadbased_snapshot = 1
    assert tt.cancel_selloff() == False
    tt.equity_client.broadbased_snapshot = -1
    tt.update_quick_selloff_criteria()
    assert tt.cancel_selloff() == True

def test_broadbased(mocker):
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
    tt.index_client = MockIndexClient()
    tt.history=[11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11]
    tt.broadbased_reference_ratio = {"up": True, "value": 1, "timestamp": datetime.datetime.now()}
    tt.get_action(11)
    assert tt.get_action(13) == 'buy'
    tt.broadbased_reference_ratio = {"up": False, "value": 1, "timestamp": datetime.datetime.now()}
    assert tt.get_action(13) == 'hold'