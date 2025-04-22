from api.currency_quote import CurrencyClient
from api.equity_quote import EquityClient
from transaction_trigger import TransactionTrigger
import requests
from dotenv import load_dotenv
import os

load_dotenv()

TARGET_SYMBOL = 'IBIT'
SOURCE_SYMBOL = 'BTC'
START_TIMESTAMP = 1743687000000000000
END_TIMESTAMP = 1743710400000000000
HISTORY_LENGTH=50
CHANGE_THRESHOLD=.05
HOLDS_PER_OVERRIDE_CENT=7

currency_client = CurrencyClient()
equity_client = EquityClient(TARGET_SYMBOL)
transaction_trigger = TransactionTrigger(test_mode=True)

total = 0
sold_price = 0
last_action = None
bought_price = 0

transaction_trigger.history_length = HISTORY_LENGTH
transaction_trigger.change_threshold = CHANGE_THRESHOLD
transaction_trigger.holds_per_override_cent = HOLDS_PER_OVERRIDE_CENT

for timestamp in range(START_TIMESTAMP, END_TIMESTAMP, 500000000):
    try:
        resp = requests.get("https://api.polygon.io/v3/trades/X:{}-USD?timestamp.gte={}&order=asc&limit=1&sort=timestamp&apiKey={}".format(SOURCE_SYMBOL, timestamp,  os.getenv('EQUITY_API_KEY')))
        price = resp.json()['results'][0]['price']
        action = transaction_trigger.get_action(price)

        if action != 'hold':
            resp = requests.get("https://api.polygon.io/v3/trades/{}?timestamp.gte={}&order=asc&limit=1&sort=timestamp&apiKey={}".format(TARGET_SYMBOL, timestamp,  os.getenv('EQUITY_API_KEY')))
            price = resp.json()['results'][0]['price']
            if action == 'buy':
                total -= price
                last_action = 'bought'
                bought_price = price
            else:
                total += price
                last_action = 'sold'
    except:
        pass

if last_action == 'bought':
    total += bought_price

print("total:", total)