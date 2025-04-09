import pytest
from transaction_trigger import TransactionTrigger
import os
from freezegun import freeze_time

response = {"last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
"timestamp":1741532522429},"request_id":"44ac62cbfdae6adc14158dac0d57ba1a","status":"success",
"symbol":"BTC-USD", "ticker": {"todaysChangePerc": 1}}

down_response = {"last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
"timestamp":1741532522429},"request_id":"44ac62cbfdae6adc14158dac0d57ba1a","status":"success",
"symbol":"BTC-USD", "ticker": {"todaysChangePerc": -1}}

up_response = {"last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
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
def test_get_crypto_quote_sell(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    
    tt = TransactionTrigger()
    tt.get_action(10)
    tt.get_action(10)
    tt.get_action(13)
    tt.bought_price = 10
    assert tt.get_action(11.45) == 'sell'

@freeze_time("2012-01-14 12:21:34")
def test_override_false(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ['HOLDS_PER_OVERRIDE_CENT'] = '100'
    
    tt = TransactionTrigger()
    tt.number_of_holds=10
    tt.running_total=2
    tt.next_action='sell'
    tt.bought_price=10
    tt.running_total = -100
    tt.history=[10, 10, 10, 10, 10, 10, 10]
    assert tt._override_sell_price(9.9) == False
    
@freeze_time("2012-01-14 12:21:34")
def test_override_true(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ['HOLDS_PER_OVERRIDE_CENT'] = '1'
    
    tt = TransactionTrigger()
    tt.number_of_holds=10
    tt.next_action='sell'
    tt.bought_price=10
    tt.running_total = -1
    tt.history=[10, 10, 10, 10, 10, 10, 10]
    assert tt._override_sell_price(9.9) == True

@freeze_time("2012-01-14 12:21:34")
def test_get_crypto_quote_buy(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    
    tt = TransactionTrigger()
    tt.get_action(10)
    tt.get_action(10)
    assert tt.get_action(10.1) == 'buy'

@freeze_time("2012-01-14 12:21:34")
def test_running_total(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    
    tt = TransactionTrigger()
    tt.get_action(10)
    tt.get_action(10)
    tt.get_action(14)
    tt.get_action(20)
    tt.get_action(20)
    tt.get_action(20)
    tt.get_action(15)
    assert tt.running_total == 1

@freeze_time("2012-01-14 12:21:34")
def test_get_crypto_quote_hold(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    
    tt = TransactionTrigger()
    tt.get_action(10)
    tt.get_action(10)
    assert tt.get_action(10.01) == 'hold'

@freeze_time("2012-01-14 12:21:34")
def test_number_of_holds(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    
    tt = TransactionTrigger()
    tt.get_action(10)
    tt.get_action(10)
    assert tt.number_of_holds == 2

def test_is_down_market(mocker):
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockDownResponse())

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'

    tt = TransactionTrigger()
    assert tt._is_down_market() == True

def test_is_up_market(mocker):
    mock_account_status = mocker.patch('transaction_trigger.time.sleep')
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockUpResponse())

    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'

    tt = TransactionTrigger()
    assert tt._is_down_market() == False
    assert tt._is_up_market() == True