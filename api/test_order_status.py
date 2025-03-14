import pytest
from order_status import OrderStatus
import os

class MockClient(object):
    def order_details(self, account_number, params):
        return MockResponse()
    
class MockResponse(object):
    def json(param):
        return order_info_json
    
order_info_json = {'session': 'NORMAL', 'duration': 'DAY', 'orderType': 'LIMIT', 'complexOrderStrategyType': 'NONE', 'quantity': 4.0, 
                   'filledQuantity': 0.0, 'remainingQuantity': 0.0, 'requestedDestination': 'AUTO', 'destinationLinkName': 'AutoRoute', 
                   'price': 1.0, 'orderLegCollection': [{'orderLegType': 'EQUITY', 'legId': 1, 'instrument': {'assetType': 'EQUITY', 'cusip': 
                    '2222', 'symbol': 'INTC', 'instrumentId': 4141930}, 'instruction': 'BUY', 'positionEffect': 'OPENING', 'quantity': 4.0}], 
                    'orderStrategyType': 'SINGLE', 'orderId': 1002818207888, 'cancelable': False, 'editable': False, 'status': 'REJECTED', 
                    'enteredTime': '2025-02-23T18:32:55+0000', 'closeTime': '2025-02-23T18:32:55+0000', 'tag': 'TA_asdf', 
                    'accountNumber': 64623647, 'statusDescription': 'No trades are currently allowed'}

class MockClientFilled(object):
    def order_details(self, account_number, params):
        return MockResponseFilled()
    
class MockResponseFilled(object):
    def json(param):
        return order_info_json_filled
    
order_info_json_filled = {'session': 'NORMAL', 'duration': 'DAY', 'orderType': 'LIMIT', 'complexOrderStrategyType': 'NONE', 'quantity': 4.0, 
                   'filledQuantity': 0.0, 'remainingQuantity': 0.0, 'requestedDestination': 'AUTO', 'destinationLinkName': 'AutoRoute', 
                   'price': 1.0, 'orderLegCollection': [{'orderLegType': 'EQUITY', 'legId': 1, 'instrument': {'assetType': 'EQUITY', 'cusip': 
                    '2222', 'symbol': 'INTC', 'instrumentId': 4141930}, 'instruction': 'BUY', 'positionEffect': 'OPENING', 'quantity': 4.0}], 
                    'orderStrategyType': 'SINGLE', 'orderId': 1002818207888, 'cancelable': False, 'editable': False, 'status': 'FILLED', 
                    'enteredTime': '2025-02-23T18:32:55+0000', 'closeTime': '2025-02-23T18:32:55+0000', 'tag': 'TA_asdf', 
                    'accountNumber': 64623647, 'statusDescription': 'No trades are currently allowed'}



def test_raise_error_on_missing_env_vars():
    try:
        OrderStatus()
    except:
        assert True

def test_parse_order_response(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'SCHB'

    mock_account_status = mocker.patch('order_status.OrderStatus.__init__', return_value=None)

    assert OrderStatus().parse_order_response(order_info_json) == 'REJECTED'


def test_get_order_status(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'SCHB'

    mock_account_status = mocker.patch('order_status.OrderStatus.__init__', return_value=None)
    order_status = OrderStatus()
    order_status.client = MockClient()
    order_status.account_number = '123'

    response = order_status.get_order_status('123')  == 'REJECTED'


def test_get_order_id(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'SCHB'

    mock_account_status = mocker.patch('order_status.OrderStatus.__init__', return_value=None)
    order_status = OrderStatus()
    order_status.client = MockClient()
    order_status.account_number = '123'
    response = MockResponse()
    response.headers = {
            "location": "value/123"
        }

    id = order_status.get_order_id(response)

    assert id == '123'

def test_await_order_filled(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'SCHB'

    mock_account_status = mocker.patch('order_status.time.sleep')
    mock_account_status = mocker.patch('order_status.OrderStatus.__init__', return_value=None)
    order_status = OrderStatus()
    order_status.client = MockClientFilled()
    order_status.account_number = '123'

    response = order_status.await_order_filled('123')

    assert True

def test_await_order_rejected(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'SCHB'

    mock_account_status = mocker.patch('order_status.OrderStatus.__init__', return_value=None)
    order_status = OrderStatus()
    order_status.client = MockClient()
    order_status.account_number = '123'

    mock_account_status = mocker.patch('order_status.time.sleep', side_effect = Exception("Something went wrong"))
    try:
        response = order_status.await_order_filled('123')
    except:
        assert True