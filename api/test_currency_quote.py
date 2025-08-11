import pytest
from currency_quote import CurrencyClient
import os

response = {"last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
"timestamp":1741532522429},"request_id":"44ac62cbfdae6adc14158dac0d57ba1a","status":"success",
"symbol":"BTC-USD"}

fx_response = {"converted":0.63,"from":"AUD","initialAmount":1,"last":{"ask":0.6309,"bid":0.6305,"exchange":48,
                "timestamp":1741384796000},"request_id":"9803987b84aad36f50fefb6391b4bf2c","status":"success",
                "symbol":"AUD/USD","to":"USD"}

class MockClient(object):
    def get_forex_quote(params):
        return MockResponse()
    def quotes(params, kwargs):
        return MockResponse()
    def get_last_trade(self, params):
        return MockResponse()
    def subscribe(self, params):
        pass
    def run(self, params):
        pass
    
class MockResponse(object):
    def __init__(self):
        self.price = 46.75

class MockList(object):
    def __init__(self):
        self.price = 46.75
        self.bid_price = 46.75
        self.ask_size=0
        self.ask_price=0
        self.close = 46.75
        self.volume = 0
        self.low = 0
        self.high = 1000000

class MockResponse(object):
    def json(param):
        return response
    
class MockFXResponse(object):
    def json(param):
        return fx_response
    
def test_quote(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_account_status = mocker.patch('currency_quote.CurrencyClient.__init__')
    mock_account_status.return_value = None

    mock_client = mocker.patch('currency_quote.RESTClient')
    mock_ws_client = mocker.patch('currency_quote.WebSocketClient')

    mock_client.return_value = MockClient()
    mock_ws_client.return_value = MockClient()

    ec = CurrencyClient()
    ec.short_term_history_len = 10
    ec.price = 0
    ec.size = []
    ec.short_size = []
    ec.short_term_history = []
    ec.update_price([MockList(),MockList(),MockList()])
    quote = ec.get_forex_quote()

    assert quote == 46.75

def test_parse_snapshot(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_account_status = mocker.patch('currency_quote.CurrencyClient.__init__')
    mock_account_status.return_value = None

    mock_client = mocker.patch('currency_quote.RESTClient')
    mock_ws_client = mocker.patch('currency_quote.WebSocketClient')

    mock_client.return_value = MockClient()
    mock_ws_client.return_value = MockClient()

    ec = CurrencyClient()
    assert ec.parse_snapshot({'results': {'values': [{'value': 51, 'timestamp': '123'}]}}) == {'value': 1.0, 'timestamp': '123'}


def test_parse_macd(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_account_status = mocker.patch('currency_quote.CurrencyClient.__init__')
    mock_account_status.return_value = None

    mock_client = mocker.patch('currency_quote.RESTClient')
    mock_ws_client = mocker.patch('currency_quote.WebSocketClient')

    mock_client.return_value = MockClient()
    mock_ws_client.return_value = MockClient()

    ec = CurrencyClient()
    assert ec.parse_macd({'results': {'values': [{'value': 51, 'signal': 50}]}}) == 1

def parse_bounds(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_account_status = mocker.patch('currency_quote.CurrencyClient.__init__')
    mock_account_status.return_value = None

    mock_client = mocker.patch('currency_quote.RESTClient')
    mock_ws_client = mocker.patch('currency_quote.WebSocketClient')

    mock_client.return_value = MockClient()
    mock_ws_client.return_value = MockClient()

    ec = CurrencyClient()
    assert ec.parse_bounds({'ticker': {'day': [{'h': 51, 'l': 50}]}}) == {'high': 51, 'low': 50}

def test_update_size(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_account_status = mocker.patch('currency_quote.CurrencyClient.__init__')
    mock_account_status.return_value = None

    mock_client = mocker.patch('currency_quote.RESTClient')
    mock_ws_client = mocker.patch('currency_quote.WebSocketClient')

    mock_client.return_value = MockClient()
    mock_ws_client.return_value = MockClient()

    ec = CurrencyClient()
    ec.size = [1, 2, 3, 4, 5, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]
    ec.size_diff = 0
    ec.previous_avg = 0
    ec.update_size(1)
    assert ec.size_diff == 5.92