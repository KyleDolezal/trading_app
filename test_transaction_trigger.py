import pytest
from transaction_trigger import TransactionTrigger
import os
from freezegun import freeze_time

response = {"results": [{"price": .00001}], "last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
"timestamp":1741532522429},"request_id":"44ac62cbfdae6adc14158dac0d57ba1a","status":"success",
"symbol":"BTC-USD", "ticker": {"todaysChangePerc": 1}}

down_response = {"results": [{"price": .0001}], "last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
"timestamp":1741532522429},"request_id":"44ac62cbfdae6adc14158dac0d57ba1a","status":"success",
"symbol":"BTC-USD", "ticker": {"todaysChangePerc": -1}}

up_response = {"results": [{"price": 1.0}], "last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
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
    
@freeze_time("2012-01-14 12:21:34")
def test_override_false(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
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
    os.environ['HOLDS_PER_OVERRIDE_CENT'] = '20'
    
    tt = TransactionTrigger(history=[0])
    tt.target_symbol = 'SCHB'
    tt.number_of_holds=1
    tt.running_total=2
    tt.currency_client.api_key = "key"

    tt.next_action='sell'
    tt.bought_price=100
    tt.history=[100,100,100]
    assert tt._override_sell_price(99) == False
    
@freeze_time("2012-01-14 12:21:34")
def test_override_true(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
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
    
    tt = TransactionTrigger(history=[0])
    tt.target_symbol = 'SCHB'
    tt.number_of_holds=10
    tt.currency_client.api_key = "key"

    tt.next_action='sell'
    tt.bought_price=10
    tt.running_total = -1
    tt.history=[10, 10, 10, 10, 10, 10, 10]
    assert tt._override_sell_price(9.9) == True

@freeze_time("2012-01-14 12:21:34")
def test_get_crypto_quote_hold(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.CurrencyClient.__init__', return_value=None)

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    
    tt = TransactionTrigger(history=[0])
    tt.equity_client.target_symbol = 'SCHB'
    tt.equity_client.api_key = "key"
    tt.currency_client.api_key = "key"

    tt.get_action(10)
    tt.get_action(10)
    assert tt.get_action(10.1) == 'hold'

@freeze_time("2012-01-14 12:21:34")
def test_running_total(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.CurrencyClient.__init__', return_value=None)

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    
    tt = TransactionTrigger(history=[0])
    tt.equity_client.target_symbol = 'SCHB'
    tt.equity_client.api_key = "key"
    tt.currency_client.api_key = "key"

    tt.get_action(10)
    tt.get_action(10)
    tt.get_action(14)
    tt.get_action(20)
    tt.get_action(20)
    tt.get_action(20)
    tt.get_action(15)
    assert tt.running_total == 0

@freeze_time("2012-01-14 12:21:34")
def test_get_crypto_quote_hold(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.currency_quote.CurrencyClient.__init__', return_value=None)

    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    
    tt = TransactionTrigger(history=[0])
    tt.equity_client.target_symbol = 'SCHB'
    tt.equity_client.api_key = "key"
    tt.currency_client.api_key = "key"
    tt.get_action(10)
    tt.get_action(10)
    assert tt.get_action(10.01) == 'hold'

@freeze_time("2012-01-14 12:21:34")
def test_number_of_holds(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.CurrencyClient.__init__', return_value=None)

    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    
    tt = TransactionTrigger(history=[0])
    tt.equity_client.target_symbol = 'SCHB'
    tt.equity_client.api_key = "key"
    tt.currency_client.api_key = "key"
    tt.get_action(10)
    tt.get_action(10)
    assert tt.number_of_holds == 2

def test_is_down_market(mocker):
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mocker.patch('currency_quote.requests.get', return_value=MockDownResponse())
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.CurrencyClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')
    mocker.patch('api.currency_quote.CurrencyClient.__init__', return_value=None)


    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'

    tt = TransactionTrigger(history=[0])
    tt.equity_client.target_symbol = 'SCHB'
    tt.equity_client.api_key = "key"
    tt.currency_client.api_key = "key"
    assert tt._is_down_market() == True

def test_is_up_market(mocker):
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockUpResponse())
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')
    mocker.patch('api.currency_quote.CurrencyClient.__init__', return_value=None)

    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ["INDEX_TICKER"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'

    tt = TransactionTrigger(history=[0])
    tt.market_direction_threshold = -1
    tt.equity_client.target_symbol = 'SCHB'
    tt.equity_client.api_key = 'key'
    tt.target_symbol = 'SCHB'
    assert tt._is_up_market() == True

def test_negative_price_action(mocker):
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockUpResponse())
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.CurrencyClient.__init__', return_value=None)

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["EQUITY_API_KEY"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'

    tt = TransactionTrigger(test_mode=True,  history=[0])
    tt.equity_client.target_symbol = 'SCHB'
    tt.equity_client.api_key = "key"
    tt.next_action='sell'
    tt.bought_price=10
    tt.running_total = -100
    tt.history=[10, 10, 10, 10, 10, 10, 10]

    assert tt.get_action(1) == 'sell'


def test_sell(mocker):
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockUpResponse())
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.CurrencyClient.__init__', return_value=None)

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'

    tt = TransactionTrigger(test_mode=True, history=[0])
    tt.equity_client.target_symbol = 'SCHB'
    tt.equity_client.api_key = "key"
    tt.next_action='sell'
    tt.bought_price=10
    tt.running_total = -100
    tt.history=[10, 10, 10, 10, 10, 10, 10]

    assert tt.get_action(1) == 'sell'


def test_preserve_asset_value(mocker):
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockUpResponse())
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mocker.patch('api.currency_quote.CurrencyClient.__init__', return_value=None)

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'

    tt = TransactionTrigger(test_mode=True, history=[0])
    tt.equity_client.target_symbol = 'SCHB'
    tt.equity_client.api_key = "key"
    tt.next_action='sell'
    tt.bought_price=10
    tt.running_total = -100
    tt._is_up_market = lambda a=None : False
    tt.test_preserve_asset_value = False

    tt.history=[10, 10, 10, 10, 10, 10, 10]
    assert tt._preserve_asset_value(11) == True

    tt._is_up_market = lambda a=None : True
    assert tt._preserve_asset_value(10) == True

@freeze_time("2012-01-14 12:21:34")
def test_status_multiplier(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
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
    os.environ['HOLDS_PER_OVERRIDE_CENT'] = '20'
    
    tt = TransactionTrigger(history=[0])
    tt.target_symbol = 'SCHB'
    tt.number_of_holds=50
    tt.running_total=2
    tt.currency_client.api_key = "key"

    tt.next_action='sell'
    tt.bought_price=100
    tt.history=[100,100,100]
    tt.status_multiplier = 100
    assert tt._override_sell_price(99) == True

    tt.status_multiplier = 1
    assert tt._override_sell_price(99) == False

@freeze_time("2012-01-14 12:21:34")
def test_get_crypto_quote_buy(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    
    tt = TransactionTrigger(history=[11, 11, 11])
    tt.history=[]
    tt.equity_client.target_symbol = 'SCHB'
    tt.is_down_market = False
    tt.equity_client.api_key = 'key'

    tt.next_action = 'buy'
    tt.get_action(11)
    assert tt.get_action(13) == 'buy'


@freeze_time("2012-01-14 12:21:34")
def test_max_txns(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mocker.patch('api.equity_quote.EquityClient.__init__', return_value=None)
    mocker.patch('transaction_base.TransactionBase._boot_strap')
    mocker.patch('api.index_quote.IndexClient.__init__', return_value=None)
    mock_ws_client = mocker.patch('api.currency_quote.WebSocketClient')

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["MARKET_DIRECTION_THRESHOLD"] = '.2'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    
    tt = TransactionTrigger(history=[11, 11, 11])
    tt.history=[]
    tt.equity_client.target_symbol = 'SCHB'
    tt.is_down_market = False
    tt.equity_client.api_key = 'key'

    tt.next_action = 'buy'
    tt.get_action(11)
    tt.max_transactions = 0
    tt.transactions = 1
    assert tt.get_action(13) == 'hold'

