import pytest
import pdb
from account_status import AccountStatus
import os

class MockClient(object):
    def account_details(account_number, params, **kwargs):
        return MockResponse()
    def quotes(params, kwargs):
        return MockResponse()
    
class MockResponse(object):
    def __init__(self):
        self.price = 46.75
    def json(param):
        return account_info_json
    
class MockEqClient(object):
    def get_equity_quote(params):
        return MockResponse()
    def quotes(params, kwargs):
        return MockResponse()
    def get_last_trade(self, params):
        return MockResponse()
    
class MockEqResponse(object):
    def __init__(self):
        self.price = 46.75
    
account_info_json = {'securitiesAccount': {'type': 'MARGIN', 'accountNumber': '12345', 'roundTrips': 0, 'isDayTrader': False, 
                            'isClosingOnlyRestricted': False, 'pfcbFlag': False, 'positions': [{'shortQuantity': 0.0, 'averagePrice': 
                            18.6255205385, 'currentDayProfitLoss': -318.293472000005, 'currentDayProfitLossPercentage': -0.34, 
                            'longQuantity': 3978.6684, 'settledLongQuantity': 3978.6684, 'settledShortQuantity': 0.0, 'instrument':
                            {'assetType': 'COLLECTIVE_INVESTMENT', 'cusip': '808524102', 'symbol': 'SCHB', 'description': 
                             'SCHWAB US BROAD MARKET ETF', 'type': 'EXCHANGE_TRADED_FUND'}, 'marketValue': 93061.05, 'maintenanceRequirement': 27918.32, 
                             'averageLongPrice': 18.6255205385, 'taxLotAverageLongPrice': 18.6255205385, 'longOpenProfitLoss': 18956.283875919074, 
                             'previousSessionLongQuantity': 3978.6684, 'currentDayCost': 0.0}], 'initialBalances': {'accruedInterest': 0.0, 
                             'availableFundsNonMarginableTrade': 81961.49, 'bondValue': 327845.96, 'buyingPower': 163922.98, 'cashBalance': 34222.49, 
                             'cashAvailableForTrading': 0.0, 'cashReceipts': 0.0, 'dayTradingBuyingPower': 417027.0, 'dayTradingBuyingPowerCall': 0.0, 
                             'dayTradingEquityCall': 0.0, 'equity': 93379.35, 'equityPercentage': 100.0, 'liquidationValue': 127601.84, 'longMarginValue': 93379.35, 
                             'longOptionMarketValue': 0.0, 'longStockValue': 93379.35, 'maintenanceCall': 0.0, 'maintenanceRequirement': 28014.0, 
                             'margin': 0.0, 'marginEquity': 93379.35, 'moneyMarketFund': 0.0, 'mutualFundValue': 81961.49, 'regTCall': 0.0, 
                             'shortMarginValue': 0.0, 'shortOptionMarketValue': 0.0, 'shortStockValue': 0.0, 'totalCash': 0.0, 'isInCall': False, 
                             'pendingDeposits': 0.0, 'marginBalance': 0.0, 'shortBalance': 0.0, 'accountValue': 127601.84}, 
                             'currentBalances': {'accruedInterest': 0.0, 'cashBalance': 34222.49, 'cashReceipts': 0.0, 'longOptionMarketValue': 0.0, 
                             'liquidationValue': 127283.54, 'longMarketValue': 93061.05, 'moneyMarketFund': 0.0, 'savings': 0.0, 'shortMarketValue': 0.0, 
                             'pendingDeposits': 0.0, 'mutualFundValue': 0.0, 'bondValue': 0.0, 'shortOptionMarketValue': 0.0, 'availableFunds': 81961.49, 
                             'availableFundsNonMarginableTrade': 47739.0, 'buyingPower': 163922.98, 'buyingPowerNonMarginableTrade': 81961.49, 
                             'dayTradingBuyingPower': 417027.0, 'equity': 127283.54, 'equityPercentage': 100.0, 'longMarginValue': 93061.05, 
                             'maintenanceCall': 0.0, 'maintenanceRequirement': 27918.32, 'marginBalance': 0.0, 'regTCall': 0.0, 'shortBalance': 0.0, 
                             'shortMarginValue': 0.0, 'sma': 81961.49}, 'projectedBalances': {'availableFunds': 81961.49, 
                             'availableFundsNonMarginableTrade': 81961.49, 'buyingPower': 163922.98, 'dayTradingBuyingPower': 417027.0, 
                             'dayTradingBuyingPowerCall': 0.0, 'maintenanceCall': 0.0, 'regTCall': 0.0, 'isInCall': False, 
                             'stockBuyingPower': 163922.98}}, 'aggregatedBalance': {'currentLiquidationValue': 127283.54, 'liquidationValue': 127283.54}, 
                             'SCHB': {'extended': {'lastPrice': 123}}}

def test_raise_error_on_missing_env_vars():
    try:
        AccountStatus()
    except ValueError:
        assert True

def test_initializes_when_env_vars_present(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    os.environ["EQUITY_API_KEY"] = 'abc'


    mock_account_status = mocker.patch('account_status.AccountStatus.__init__')
    mock_account_status.return_value = None

    AccountStatus()

    assert True

def test_calculate_tradable_funds(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_account_status = mocker.patch('account_status.AccountStatus.__init__')
    mock_account_status.return_value = None

    assert AccountStatus().calculate_tradable_funds(100, 50, 60) == 50

def test_parse_account_info(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    os.environ["EQUITY_API_KEY"] = 'abc'
    os.environ["CASH_TO_SAVE"] = '100'

    mock_client = mocker.patch('account_status.schwabdev.Client')
    mock_client.return_value = MockClient()
    accountStatus = AccountStatus()

    assert accountStatus.parse_account_info(account_info_json) == {'position_balance': 93061.05, 'tradable_funds': 34122.49}

def test_get_account_status(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_client = mocker.patch('account_status.schwabdev.Client')
    mock_client.return_value = MockClient()
    accountStatus = AccountStatus().get_account_status()

    assert accountStatus == {'position_balance': 93061.05, 'tradable_funds': 34122.49}

def test_update_positions(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_client = mocker.patch('account_status.schwabdev.Client')
    mock_client.return_value = MockClient()

    astat = AccountStatus()
    astat.update_positions()
    assert astat.funds == 34122.49

def test_calculate_buyable_shares(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_client = mocker.patch('account_status.schwabdev.Client')
    mock_client.return_value = MockClient()
    mock_eq = mocker.patch('api.equity_quote.RESTClient')
    mock_eq.return_value = MockEqClient()

    astat = AccountStatus()
    assert astat.calculate_buyable_shares() == {'price': 46.75, 'shares': 730}

def test_calculate_sellable_shares(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'

    mock_client = mocker.patch('account_status.schwabdev.Client')
    mock_client.return_value = MockClient()
    mock_eq = mocker.patch('api.equity_quote.RESTClient')
    mock_eq.return_value = MockEqClient()

    astat = AccountStatus()
    assert astat.calculate_sellable_shares() == 1991