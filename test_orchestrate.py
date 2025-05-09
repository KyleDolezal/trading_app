import pytest
from orchestrate import Orchestrator
import os

class MockClientBuy(object):
    def order_details(a, b, c):
        return MockResponse()
    def account_details(account_number, params, **kwargs):
        return MockResponse()
    def quotes(params, kwargs):
        return MockResponse()
    def order_place(params, arg, order_info):
        assert order_info['orderLegCollection'][0]['instruction'] == 'BUY'
        return MockResponse()
    
class MockAS(object):
    def update_positions(self):
        pass
    def calculate_sellable_shares(self):
        pass
    def calculate_buyable_shares(self):
        return {'shares': 1}

class MockPGClient(object):
    def exec_query(self, text):
        pass

class MockEquityClient(object):
    def get_crypto_quote():
        return 123
    
class MockTTClient(object):
    def get_action():
        return 'buy'
    def buy(self, quantity):
        pass
    def sell(self, quantity, price):
        pass

class MockResponse(object):
    def __init__(self):
        self.status_code = 201
    def json(param):
        return account_info_json

class MockClientSell(object):
    def order_details(a, b, c):
        return MockResponse()
    def account_details(account_number, params, **kwargs):
        return MockResponse()
    def quotes(params, kwargs):
        return MockResponse()
    def order_place(params, arg, order_info):
        assert order_info['orderLegCollection'][0]['instruction'] == 'SELL'
        return MockResponse()
    
class MockClientMarket(object):
    def order_details(a, b, c):
        return MockResponse()
    def account_details(account_number, params, **kwargs):
        return MockResponse()
    def quotes(params, kwargs):
        return MockResponse()
    def order_place(params, arg, order_info):
        assert order_info['orderType'] == 'MARKET'
        return MockResponse()
    
class MockTT(object):
    def get_action(param, kwargs):
        return 'buy'
    
class MockTTSell(object):
    def get_action(param, kwargs):
        return 'sell'
class MockTTSellMarket(object):
    def get_action(param, kwargs):
        return 'sell_market'

class MockOS(object):
    def get_order_status(param, kwargs):
        return 'status'
    def get_order_id(param, order):
        return 555
    def await_order_filled(params, kwargs):
        pass

fx_response = {"last":{"conditions":[1],"exchange":1,"price":83712.2,"size":0.00473092,""
"timestamp":1741532522429},"request_id":"44ac62cbfdae6adc14158dac0d57ba1a","status":"success",
"symbol":"BTC-USD"}

class MockFXResponse(object):
    def json(param):
        return fx_response
    
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


def test_buy(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    os.environ["EQUITY_API_KEY"] = 'abc'
    os.environ["CASH_TO_SAVE"] = '100'
    mocker.patch('orchestrate.Orchestrator.__init__', return_value=None)
    mocker.patch('orchestrate.time.sleep')
    mocker.patch('currency_quote.requests.get', return_value=MockFXResponse())
    mock_client = mocker.patch('api.equity_quote.RESTClient')
    mock_client = mocker.patch('account_status.schwabdev.Client')
    mock_client.return_value = MockClientBuy()

    orchestrator = Orchestrator('AAPL', MockTT())
    orchestrator.target_symbol = 'AAPL'
    orchestrator.buyable_shares = 1
    orchestrator.account_status = MockAS()
    orchestrator.transact_client = MockTTClient()
    orchestrator.currency_client = MockEquityClient
    orchestrator.pg_adapter = MockPGClient()
    orchestrator.transaction_trigger = MockTT()
    orchestrator.order_status = MockOS()

    orchestrator.orchestrate(100)

def test_sell(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    mocker.patch('orchestrate.time.sleep')
    mocker.patch('orchestrate.Orchestrator.__init__', return_value=None)
    mocker.patch('currency_quote.requests.get', return_value=MockFXResponse())
    mock_client = mocker.patch('api.equity_quote.RESTClient')

    mock_client = mocker.patch('account_status.schwabdev.Client')
    mock_client.return_value = MockClientSell()

    orchestrator = Orchestrator('AAPL', MockTT())
    orchestrator.target_symbol = 'AAPL'
    orchestrator.sellable_shares = 1
    orchestrator.account_status = MockAS()
    orchestrator.transact_client = MockTTClient()
    orchestrator.currency_client = MockEquityClient
    orchestrator.pg_adapter = MockPGClient()
    orchestrator.transaction_trigger = MockTTSell()
    orchestrator.order_status = MockOS()
    orchestrator.orchestrate(100)

def test_sell_market(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'SCHB'
    os.environ["HISTORY_LENGTH"] = '3'
    os.environ["CHANGE_THRESHOLD"] = '.1'
    os.environ["CASH_TO_SAVE"] = '100'
    os.environ["EQUITY_API_KEY"] = 'abc'
    os.environ["CURRENCY_TICKER"] = '123'
    os.environ["CURRENCY_API_KEY"] = 'key'
    mocker.patch('orchestrate.time.sleep')
    mocker.patch('currency_quote.requests.get', return_value=MockFXResponse())
    mocker.patch('orchestrate.Orchestrator.__init__', return_value=None)
    mock_client = mocker.patch('api.equity_quote.RESTClient')

    mock_client = mocker.patch('account_status.schwabdev.Client')
    mock_client.return_value = MockClientMarket()

    orchestrator = Orchestrator('AAPL', MockTT())
    orchestrator.target_symbol = 'AAPL'
    orchestrator.sellable_shares = 1
    orchestrator.account_status = MockAS()
    orchestrator.transact_client = MockTTClient()
    orchestrator.currency_client = MockEquityClient
    orchestrator.pg_adapter = MockPGClient()
    orchestrator.transaction_trigger = MockTTSellMarket()
    orchestrator.order_status = MockOS()
    orchestrator.orchestrate(100)