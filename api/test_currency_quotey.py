import pytest
from currency_quote import CurrencyClient
import os

response = {"last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
"timestamp":1741532522429},"request_id":"44ac62cbfdae6adc14158dac0d57ba1a","status":"success",
"symbol":"BTC-USD"}

fx_response = {"converted":0.63,"from":"AUD","initialAmount":1,"last":{"ask":0.6309,"bid":0.6305,"exchange":48,
                "timestamp":1741384796000},"request_id":"9803987b84aad36f50fefb6391b4bf2c","status":"success",
                "symbol":"AUD/USD","to":"USD"}

class MockResponse(object):
    def json(param):
        return response
    
class MockFXResponse(object):
    def json(param):
        return fx_response
    
def test_parse_crypto_quote():
    assert CurrencyClient.parse_crypto_response(MockResponse()) == 83712.2

def test_get_crypto_quote(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockResponse())
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    
    assert CurrencyClient().get_crypto_quote() == 83712.2

def test_get_crypto_quote_without_env_vars():
    try:
        CurrencyClient()
    except:
        assert True
   
def test_parse_crypto_quote():
    assert CurrencyClient.parse_forex_response(MockFXResponse()) == 0.6309

def test_get_crypto_quote(mocker):
    mock_account_status = mocker.patch('currency_quote.requests.get', return_value=MockFXResponse())
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'

    assert CurrencyClient().get_forex_quote() == 0.6309
