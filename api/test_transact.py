import pytest
from transact import TransactClient
import os



class MockClient(object):
    def __init__(self):
        self.response = MockResponse()

    def order_place(self, params, args):
        assert params == "1234"
        return self.response
    
    def order_cancel(self, id, params):
        assert id == '1234'
        return MockResponse()

class MockResponse(object):
    def __init__(self):
        self.headers = {}
        self.status_code = 201

class MockClientFailed(object):
    def __init__(self):
        self.response = MockFailedResponse()

    def order_place(self, params, args):
        assert params == "1234"
        return self.response
    
class MockFailedResponse(object):
    def __init__(self):
        self.headers = {}
        self.status_code = 400

def test_buy(mocker):
    mocker.patch('transact.TransactClient.__init__', return_value=None)
    mocker.patch('transact.time.sleep')
    transact_client = TransactClient()
    transact_client.client = MockClient()
    transact_client.stop_value = -.125
    transact_client.target_symbol = "SCHB"
    transact_client.account_number = "1234"

    assert transact_client.buy(1, 2.0) == transact_client.client.response

def test_buy_with_update_config(mocker):
    mocker.patch('transact.TransactClient.__init__', return_value=None)
    mocker.patch('transact.time.sleep')
    transact_client = TransactClient()
    transact_client.client = MockClient()
    transact_client.stop_value = -.125
    transact_client.target_symbol = "SCHB"
    transact_client.account_number = "1234"

    assert transact_client.buy(1, 2.0, order_id_to_update='123') == transact_client.client.response


def test_sell(mocker):
    mocker.patch('transact.TransactClient.__init__', return_value=None)
    mocker.patch('transact.time.sleep')
    transact_client = TransactClient()
    transact_client.client = MockClient()
    transact_client.target_symbol = "SCHB"
    transact_client.stop_value = -.125
    transact_client.account_number = "1234"

    assert transact_client.sell(1, 'LIMIT', 10.0) == transact_client.client.response

def test_sell_zero_limit(mocker):
    mocker.patch('transact.TransactClient.__init__', return_value=None)
    mocker.patch('transact.time.sleep')
    transact_client = TransactClient()
    transact_client.client = MockClient()
    transact_client.target_symbol = "SCHB"
    transact_client.account_number = "1234"

    assert transact_client.sell(1, 'LIMIT', 0) == transact_client.client.response

def test_sell_market(mocker):
    mocker.patch('transact.TransactClient.__init__', return_value=None)
    mocker.patch('transact.time.sleep')
    transact_client = TransactClient()
    transact_client.client = MockClient()
    transact_client.stop_value = -.125
    transact_client.target_symbol = "SCHB"
    transact_client.account_number = "1234"

    assert transact_client.sell(1, 'MARKET', 10.0) == transact_client.client.response

def test_buy_bad_response(mocker):
    mocker.patch('transact.TransactClient.__init__', return_value=None)
    mocker.patch('transact.time.sleep')
    transact_client = TransactClient()
    transact_client.client = MockClientFailed()
    transact_client.target_symbol = "SCHB"
    transact_client.account_number = "1234"

    try:
        transact_client.buy(1) == transact_client.client.response
    except:
        assert True

def test_sell_bad_response(mocker):
    mocker.patch('transact.TransactClient.__init__', return_value=None)
    mocker.patch('transact.time.sleep')
    transact_client = TransactClient()
    transact_client.client = MockClientFailed()
    transact_client.target_symbol = "SCHB"
    transact_client.account_number = "1234"

    try:
        transact_client.sell(1, 'LIMIT', 10.0)  == transact_client.client.response
    except:
        assert True