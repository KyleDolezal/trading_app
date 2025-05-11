from api.currency_quote import CurrencyClient
import datetime
from api.equity_quote import EquityClient
from transaction_trigger import TransactionTrigger
import requests
from dotenv import load_dotenv
import os

load_dotenv()

TARGET_SYMBOL = 'IBIT'
SOURCE_SYMBOL = 'BTC'

START_TIMESTAMP = 1745415000000000000
END_TIMESTAMP = 1745438400000000000
TWO_THIRTY_PM = END_TIMESTAMP - 1800000000000

# Volatile flat day

HISTORY_LENGTH=50
CHANGE_THRESHOLD=.075
HOLDS_PER_OVERRIDE_CENT=.1
QUICK_SELLOFF_MULTIPLIER=10
TEST_PRESERVE_ASSET_VALUE=False

currency_client = CurrencyClient()
equity_client = EquityClient(TARGET_SYMBOL)
transaction_trigger = TransactionTrigger(test_mode=True)

total = 0
sold_price = 0
last_action = None
bought_price = 0
sold_in_last_half_hour = False
num_of_transactions = 0

transaction_trigger.history_length = HISTORY_LENGTH
transaction_trigger.change_threshold = CHANGE_THRESHOLD
transaction_trigger.holds_per_override_cent = HOLDS_PER_OVERRIDE_CENT
transaction_trigger.quick_selloff_multiplier = QUICK_SELLOFF_MULTIPLIER
transaction_trigger.test_preserve_asset_value = TEST_PRESERVE_ASSET_VALUE
transaction_trigger.today230pm = 9745415000000000000
future = datetime.datetime.now().replace(year=2030, hour=8, minute=31, second=0, microsecond=0)
past = datetime.datetime.now().replace(year=1990, hour=14, minute=31, second=0, microsecond=0)
transaction_trigger.today230pm = future
transaction_trigger.today7pm = future
for timestamp in range((START_TIMESTAMP-40500000000), END_TIMESTAMP, 150000000):
    if timestamp == TWO_THIRTY_PM:
        transaction_trigger.today230pm = past
    try:
        resp = requests.get("https://api.polygon.io/v3/trades/X:{}-USD?timestamp.gte={}&order=asc&limit=1&sort=timestamp&apiKey={}".format(SOURCE_SYMBOL, timestamp,  os.getenv('EQUITY_API_KEY')))
        price = resp.json()['results'][0]['price']
        action = transaction_trigger.get_action(price)
        if action != 'hold':
            num_of_transactions += 1
            resp = requests.get("https://api.polygon.io/v3/trades/{}?timestamp.gte={}&order=asc&limit=1&sort=timestamp&apiKey={}".format(TARGET_SYMBOL, timestamp + 300000000,  os.getenv('EQUITY_API_KEY')))
            price = resp.json()['results'][0]['price']
            if action == 'buy':
                print("bought at:", timestamp)
                total -= price
                last_action = 'bought'
                bought_price = price
            else:
                print("sold at:", timestamp)
                if timestamp > TWO_THIRTY_PM:
                    sold_in_last_half_hour = True
                total += price
                last_action = 'sold'
    except:
        pass

if last_action == 'bought':
    total += bought_price

print("total:", total)
print("sold_in_last_hour:", sold_in_last_half_hour)
print("num of transactions:", num_of_transactions)