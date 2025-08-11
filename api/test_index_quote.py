import pytest
from index_quote import IndexClient
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
        self.value = 46.75

class MockList(object):
    def __init__(self):
        self.value = 46.75
        self.close = 46.75
        self.volume = 0
        self.low = 0
        self.high = 1000000


def test_quote(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'IBIT'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_init = mocker.patch('index_quote.IndexClient.__init__')
    mock_init.return_value = None
    mock_account_status =  mock_ws_client = mocker.patch('index_quote.WebSocketClient')
    mock_account_status.return_value = None

    mock_ws_client.return_value = MockClient()

    ec = IndexClient()
    ec.short_term_history_len = 10
    ec.price = 0
    ec.size = []
    ec.short_size = []
    ec.short_term_history = []
    ec.update_price([MockList(),MockList(),MockList()])
    quote = ec.get_equity_quote()

    assert quote == 46.75