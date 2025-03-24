import pytest
from transaction_trigger import TransactionTrigger
import os

response = {"last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
"timestamp":1741532522429},"request_id":"44ac62cbfdae6adc14158dac0d57ba1a","status":"success",
"symbol":"BTC-USD"}

class MockResponse(object):
    def json(param):
        return response
    
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

def test_get_crypto_quote_sell_market(mocker):
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
    tt.bought_price = 9
    assert tt.get_action(9) == 'sell_market'

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