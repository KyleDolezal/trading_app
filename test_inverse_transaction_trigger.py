import logging
logger = logging.getLogger(__name__)
import pytest
from inverse_transaction_trigger import InverseTransactionTrigger
import os
import datetime
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
    

@freeze_time("2012-01-14 12:21:34")
def test_get_crypto_quote_buy(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.equity_quote.EquityClient.get_snapshot', return_value=.1)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    
    tt = InverseTransactionTrigger(history=[0])
    tt.history=[]
    tt.equity_client.target_symbol = 'SCHB'
    tt.equity_client.api_key = 'key'
    tt.equity_client.today831am = 123

    tt.next_action = 'buy'
    tt.get_action(11)
    tt.get_action(11)
    tt.get_action(11)

    assert tt.get_action(10) == 'buy'


@freeze_time("2012-01-14 12:21:34")
def test_get_crypto_quote_blackout(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.equity_quote.EquityClient.get_snapshot', return_value=.1)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    
    tt = InverseTransactionTrigger(history=[0])
    tt.history=[]
    tt.equity_client.target_symbol = 'SCHB'
    tt.equity_client.api_key = 'key'
    tt.equity_client.today831am = 123
    tt.blackout_holds = 5

    tt.next_action = 'buy'
    tt.get_action(11)
    tt.get_action(11)
    tt.get_action(11)

    assert tt.get_action(10) == 'hold'


@freeze_time("2012-01-14 12:21:34")
def test_max_txns(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.equity_quote.EquityClient.get_snapshot', return_value=.1)
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    
    tt = InverseTransactionTrigger(history=[0])
    tt.history=[]
    tt.equity_client.target_symbol = 'SCHB'
    tt.equity_client.api_key = 'key'

    tt.next_action = 'buy'
    tt.get_action(11)
    tt.get_action(11)
    tt.get_action(11)
    tt.transactions = 1
    tt.max_transactions = 0

    assert tt.get_action(10) == 'hold'

@freeze_time("2012-01-14 12:21:34")
def test_get_crypto_quote_sell(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.equity_quote.EquityClient.get_snapshot', return_value=.1)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    
    tt = InverseTransactionTrigger(history=[0])
    tt.history=[]
    tt.equity_client.target_symbol = 'SCHB'
    tt.equity_client.api_key = 'key'

    tt.next_action = 'sell'
    tt.bought_price = 13
    tt.get_action(10)
    tt.get_action(10)
    assert tt.get_action(13) == 'sell'


@freeze_time("2012-01-14 12:21:34")
def test_get_crypto_quote_hold(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mocker.patch('api.currency_quote.WebSocketClient')
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["CURRENCY_API_KEY"] = 'key'
    
    tt = InverseTransactionTrigger(history=[0], test_mode=True)
    tt.target_symbol = 'SCHB'
    tt.get_action(10)
    tt.get_action(10)
    assert tt.get_action(10.01) == 'hold'

def test_is_down_market(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockDownResponse())
    mocker.patch('api.equity_quote.EquityClient.get_snapshot', return_value=.1)
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')


    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'

    tt = InverseTransactionTrigger(history=[0])
    tt.equity_client.target_symbol = 'SCHB'
    tt.equity_client.api_key = 'key'
    assert tt._is_down_market() == True

def test_is_up_market(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.equity_quote.EquityClient.get_snapshot', return_value=.1)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockUpResponse())
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')


    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["CURRENCY_API_KEY"] = 'key'

    tt = InverseTransactionTrigger(history=[0])
    tt.market_direction_threshold = -1
    tt.target_symbol = 'SCHB'
    tt.equity_client.target_symbol = 'SCHB'
    tt.equity_client.api_key = 'key'
    assert tt._is_up_market() == True



@freeze_time("2012-01-14 12:21:34")
def test_override_false(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.equity_quote.EquityClient.get_snapshot', return_value=.1)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mocker.patch('inverse_transaction_trigger.time.sleep')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.WebSocketClient')


    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ['HOLDS_PER_OVERRIDE_CENT'] = '10'
    
    tt = InverseTransactionTrigger(history=[0])
    tt.today841am = datetime.datetime.now().replace(hour=8, minute=41, second=0, microsecond=0)
    tt.equity_client.logger = logger
    tt.equity_client.today831am = datetime.datetime.now().replace(hour=8, minute=31, second=0, microsecond=0)
    tt.equity_client.target_symbol = 'SCHB'
    tt.target_symbol = 'SCHB'
    tt.equity_client.api_key = 'key'
    tt.number_of_holds=10
    tt.next_action='sell'
    tt.bought_price=10
    tt.quick_selloff_additional_threshold=50000
    tt.running_total = -100
    tt.history=[10, 10, 10, 10, 10, 10, 10]
    assert tt._override_sell_price(11) == False

def test_negative_price_action(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockUpResponse())
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.WebSocketClient')

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'

    tt = InverseTransactionTrigger(test_mode=True, history=[0])
    tt.target_symbol = 'SCHB'
    tt.next_action='sell'
    tt.bought_price=10
    tt.running_total = -100
    tt.history=[10, 10, 10, 10, 10, 10, 10]

    assert tt.get_action(10000000000000) == 'sell'

def test_preserve_asset_value(mocker):
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockUpResponse())
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.WebSocketClient')

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["EQUITY_API_KEY"] = 'key'

    tt = InverseTransactionTrigger(test_mode=True, history=[0])
    tt.target_symbol = 'SCHB'
    tt.next_action='sell'
    tt.bought_price=10
    tt.running_total = -100
    tt._is_up_market = lambda a=None : False
    tt.test_preserve_asset_value = False
    tt.history=[10, 10, 10, 10, 10, 10, 10]
    assert tt._preserve_asset_value(9) == True

    tt._is_up_market = lambda a=None : True
    assert tt._preserve_asset_value(10) == True

@freeze_time("2012-01-14 12:21:34")
def test_override_true(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mocker.patch('transaction_trigger.time.sleep')
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.CurrencyClient.__init__', return_value=None)

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["EQUITY_API_KEY"] = 'SCHB'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ['HOLDS_PER_OVERRIDE_CENT'] = '1'
    
    tt = InverseTransactionTrigger(history=[0])
    tt.target_symbol = 'SCHB'
    tt.number_of_holds=10
    tt.is_up_market=True

    tt.next_action='sell'
    tt.bought_price=10
    tt.running_total = -11
    tt.history=[10, 10, 10, 10, 10, 10, 10]
    assert tt._override_sell_price(1000.1) == True

@freeze_time("2012-01-14 12:21:34")
def test_status_multiplier(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mocker.patch('transaction_trigger.time.sleep')
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.CurrencyClient.__init__', return_value=None)

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["EQUITY_API_KEY"] = 'SCHB'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ['HOLDS_PER_OVERRIDE_CENT'] = '.00000000000001'
    
    tt = InverseTransactionTrigger(history=[0])
    tt.target_symbol = 'SCHB'
    tt.number_of_holds=10

    tt.next_action='sell'
    tt.bought_price=10
    tt.running_total = -11
    tt.history=[10, 10, 10, 10, 10, 10, 10]
    tt.is_up_market = True

    tt.status_multiplier = 1000
    assert tt._override_sell_price(10.01) == True
    tt.status_multiplier = -1
    tt.is_up_market = False
    assert tt._override_sell_price(10.01) == False

@freeze_time("2012-01-14 12:21:34")
def test_override_countdown(mocker):
    mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mocker.patch('transaction_trigger.time.sleep')
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mocker.patch('api.equity_quote.EquityClient.get_snapshot', return_value=.1)
    mocker.patch('api.currency_quote.CurrencyClient.__init__', return_value=None)

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["EQUITY_API_KEY"] = 'SCHB'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ['HOLDS_PER_OVERRIDE_CENT'] = '1'
    
    tt = InverseTransactionTrigger(history=[0])
    tt.target_symbol = 'SCHB'
    tt.number_of_holds=10

    tt.next_action='sell'
    tt.bought_price=10
    tt.running_total = -1
    tt.quick_selloff_additional_threshold=5000
    tt.history=[10, 10, 10, 10, 10, 10, 10]
    tt.override_countdown = datetime.timedelta(1)
    assert tt._override_sell_price(9.9) == False

    tt.override_countdown = datetime.timedelta(0)
    assert tt._override_sell_price(9.9) == True