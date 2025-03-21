import pytest
from order_status import OrderStatus
import os

class MockClient(object):
    def order_details(self, account_number, params):
        return MockResponse()
    
class MockResponse(object):
    def json(param):
        return order_info_json
    
order_info_json = {'status': 201, 'session': 'NORMAL', 'duration': 'DAY', 'orderType': 'LIMIT', 'complexOrderStrategyType': 'NONE', 'quantity': 21.0, 'filledQuantity': 21.0, 'remainingQuantity': 0.0, 'requestedDestination': 'AUTO', 'destinationLinkName': 'JNST', 'price': 48.75, 'orderLegCollection': [{'orderLegType': 'EQUITY', 'legId': 1, 'instrument': {'assetType': 'COLLECTIVE_INVESTMENT', 'cusip': '46438F101', 'symbol': 'IBIT', 'description': 'ISHARES BITCOIN ETF', 'instrumentId': 211446341, 'type': 'EXCHANGE_TRADED_FUND'}, 'instruction': 'SELL', 'positionEffect': 'CLOSING', 'quantity': 21.0}], 'orderStrategyType': 'SINGLE', 'orderId': 1002974972859, 'cancelable': False, 'editable': False, 'status': 'REJECTED', 'enteredTime': '2025-03-20T13:43:44+0000', 'closeTime': '2025-03-20T13:43:44+0000', 'accountNumber': 64623647, 'orderActivityCollection': [{'activityType': 'EXECUTION', 'activityId': 93918428795, 'executionType': 'FILL', 'quantity': 21.0, 'orderRemainingQuantity': 0.0, 'executionLegs': [{'legId': 1, 'quantity': 21.0, 'mismarkedQuantity': 0.0, 'price': 48.75, 'time': '2025-03-20T13:43:44+0000', 'instrumentId': 211446341}]}]}

class MockClientFilled(object):
    def order_details(self, account_number, params):
        return MockResponseFilled()

class MockClientFilledNone(object):
    def order_details(self, account_number, params):
        return MockResponseFilledNone()

class MockResponseFilledNone(object):
    def json(param):
        return NoneObject()
    
class NoneObject(object):
    def get(_, param):
        return None
    
class MockResponseFilled(object):
    def json(param):
        return order_info_json_filled
    
order_info_json_filled = {'status': 201, 'session': 'NORMAL', 'duration': 'DAY', 'orderType': 'LIMIT', 'complexOrderStrategyType': 'NONE', 'quantity': 21.0, 'filledQuantity': 21.0, 'remainingQuantity': 0.0, 'requestedDestination': 'AUTO', 'destinationLinkName': 'JNST', 'price': 48.75, 'orderLegCollection': [{'orderLegType': 'EQUITY', 'legId': 1, 'instrument': {'assetType': 'COLLECTIVE_INVESTMENT', 'cusip': '46438F101', 'symbol': 'IBIT', 'description': 'ISHARES BITCOIN ETF', 'instrumentId': 211446341, 'type': 'EXCHANGE_TRADED_FUND'}, 'instruction': 'SELL', 'positionEffect': 'CLOSING', 'quantity': 21.0}], 'orderStrategyType': 'SINGLE', 'orderId': 1002974972859, 'cancelable': False, 'editable': False, 'status': 'FILLED', 'enteredTime': '2025-03-20T13:43:44+0000', 'closeTime': '2025-03-20T13:43:44+0000', 'accountNumber': 64623647, 'orderActivityCollection': [{'activityType': 'EXECUTION', 'activityId': 93918428795, 'executionType': 'FILL', 'quantity': 21.0, 'orderRemainingQuantity': 0.0, 'executionLegs': [{'legId': 1, 'quantity': 21.0, 'mismarkedQuantity': 0.0, 'price': 48.75, 'time': '2025-03-20T13:43:44+0000', 'instrumentId': 211446341}]}]}



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

    assert OrderStatus().parse_order_response(order_info_json)['status'] == 'REJECTED'


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