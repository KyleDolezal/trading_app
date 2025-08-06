import pytest
from equity_quote import EquityClient
import os

class MockClient(object):
    def get_equity_quote(params):
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
        self.bid_price = 46.75

class MockList(object):
    def __init__(self):
        self.bid_price = 46.75
        self.symbol = 'AAPL'
        self.target_symbol = 'AAPL'


def test_initializes_when_env_vars_present(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'IBIT'

    mock_account_status = mocker.patch('equity_quote.EquityClient.__init__')
    mock_account_status.return_value = None

    EquityClient('IBIT')

    assert True

def test_quote(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'IBIT'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_account_status = mocker.patch('equity_quote.EquityClient.__init__')
    mock_account_status.return_value = None

    mock_client = mocker.patch('equity_quote.RESTClient')
    mock_ws_client = mocker.patch('equity_quote.WebSocketClient')

    mock_client.return_value = MockClient()
    mock_ws_client.return_value = MockClient()

    ec = EquityClient('IBIT')
    ec.price = 0
    ec.test_mode = True
    ec.target_symbol = 'AAPL'
    ec.inverse_target_symbol = 'SCHB'
    ec.update_price([MockList(),MockList(),MockList()])
    quote = ec.get_equity_quote('AAPL')

    assert quote == 1.0

def test_parse_trade_response(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'IBIT'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_account_status = mocker.patch('equity_quote.EquityClient.__init__')
    mock_account_status.return_value = None

    mock_client = mocker.patch('equity_quote.RESTClient')
    mock_ws_client = mocker.patch('equity_quote.WebSocketClient')

    mock_client.return_value = MockClient()
    mock_ws_client.return_value = MockClient()

    ec = EquityClient('IBIT')

    response = {'results': [{'price': 1.0}]}

    assert ec._parse_trade_response(response) == 1

def test_parse_ema_price(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'IBIT'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_account_status = mocker.patch('equity_quote.EquityClient.__init__')
    mock_account_status.return_value = None

    mock_client = mocker.patch('equity_quote.RESTClient')
    mock_ws_client = mocker.patch('equity_quote.WebSocketClient')

    mock_client.return_value = MockClient()
    mock_ws_client.return_value = MockClient()

    ec = EquityClient('IBIT')

    response = {'results': {'values': [{'value': 1.0}]}}

    assert ec._parse_ema_price(response) == 1


def test_calculate_percent(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'IBIT'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_account_status = mocker.patch('equity_quote.EquityClient.__init__')
    mock_account_status.return_value = None

    mock_client = mocker.patch('equity_quote.RESTClient')
    mock_ws_client = mocker.patch('equity_quote.WebSocketClient')

    mock_client.return_value = MockClient()
    mock_ws_client.return_value = MockClient()

    ec = EquityClient('IBIT', test_mode=True)

    response = {'results': {'values': [{'value': 1.0}]}}

    assert ec._calculate_percent(1, 1.01) == 0.5000000000000115



def test_bid_ask_mean(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'IBIT'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_account_status = mocker.patch('equity_quote.EquityClient.__init__')
    mock_account_status.return_value = None

    mock_client = mocker.patch('equity_quote.RESTClient')
    mock_ws_client = mocker.patch('equity_quote.WebSocketClient')

    mock_client.return_value = MockClient()
    mock_ws_client.return_value = MockClient()

    ec = EquityClient(test_mode=True)
    ec.test_mode = True
    ec.ask_price = 1.0
    ec.price = 2.0

    assert ec.bid_ask_mean('IBIT') == 1.5
