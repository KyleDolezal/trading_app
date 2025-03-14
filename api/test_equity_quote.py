import pytest
from equity_quote import EquityClient
import os

class MockClient(object):
    def get_equity_quote(params):
        return MockResponse()
    def quotes(params, kwargs):
        return MockResponse()
    
class MockResponse(object):
    def json(param):
        return json
    
json = {'IBIT': {'assetMainType': 'EQUITY', 'assetSubType': 'ETF', 'quoteType': 'NBBO', 'realtime': True, 
        'ssid': 91509352, 'symbol': 'IBIT', 'extended': {'askPrice': 0.0, 'askSize': 0, 'bidPrice': 0.0, 'bidSize': 0, 
        'lastPrice': 46.75, 'lastSize': 2000, 'mark': 0.0, 'quoteTime': 1741939200000, 'totalVolume': 0, 
        'tradeTime': 1741938929000}, 'fundamental': {'avg10DaysVolume': 59234358.0, 'avg1YearVolume': 38286952.0, 
        'divAmount': 0.0, 'divFreq': 0, 'divPayAmount': 0.0, 'divYield': 0.0, 'eps': 0.0, 'fundLeverageFactor': 0.0, 
        'peRatio': 0.0}, 'quote': {'52WeekHigh': 61.75, '52WeekLow': 28.23, 'askMICId': 'ARCX', 'askPrice': 47.45, 
        'askSize': 22, 'askTime': 1741959668279, 'bidMICId': 'XNAS', 'bidPrice': 47.44, 'bidSize': 39, 'bidTime': 
        1741959668412, 'closePrice': 45.52, 'highPrice': 47.68, 'lastMICId': 'XADF', 'lastPrice': 47.4401, 
        'lastSize': 6800, 'lowPrice': 47.38, 'mark': 47.4401, 'markChange': 1.9201, 'markPercentChange': 4.21814587, 
        'netChange': 1.9201, 'netPercentChange': 4.21814587, 'openPrice': 47.385, 'postMarketChange': 0.0, 
        'postMarketPercentChange': 0.0, 'quoteTime': 1741959668412, 'securityStatus': 'Normal', 
        'totalVolume': 5260552, 'tradeTime': 1741959668144}, 'reference': {'cusip': '46438F101', 
        'description': 'ISHARES BITCOIN ETF', 'exchange': 'Q', 'exchangeName': 'NASDAQ', 'isHardToBorrow': True, 
        'isShortable': True, 'htbRate': 0.0}, 'regular': {'regularMarketLastPrice': 47.4401, 
        'regularMarketLastSize': 6800, 'regularMarketNetChange': 1.9201, 'regularMarketPercentChange': 4.21814587, 
        'regularMarketTradeTime': 1741959668144}}}

def test_raise_error_on_missing_env_vars():
    try:
        ()
    except EquityClient:
        assert True

def test_initializes_when_env_vars_present(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'IBIT'

    mock_account_status = mocker.patch('equity_quote.EquityClient.__init__')
    mock_account_status.return_value = None

    EquityClient()

    assert True

def test_parse_quote(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'IBIT'
    os.environ["CASH_TO_SAVE"] = '100'

    mock_client = mocker.patch('equity_quote.schwabdev.Client')
    mock_client.return_value = None
    equity_client = EquityClient()

    assert equity_client.parse_quote(json) == 46.75

def test_quote(mocker):
    os.environ["ACCOUNT_NUMBER"] = '123'
    os.environ["APP_KEY"] = 'key'
    os.environ["APP_SECRET"] = 'secret'
    os.environ["TARGET_SYMBOL"] = 'IBIT'
    os.environ["CASH_TO_SAVE"] = '100'

    mock_client = mocker.patch('equity_quote.schwabdev.Client')
    mock_client.return_value = MockClient()
    quote = EquityClient().get_equity_quote()

    assert quote == 46.75