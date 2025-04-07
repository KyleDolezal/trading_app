import logging

from api.account_status import AccountStatus
from api.currency_quote import CurrencyClient
from api.order_status import OrderStatus
from api.equity_quote import EquityClient
from api.transact import TransactClient
from orchestrator_base import OrchestratorBase
from transaction_trigger import TransactionTrigger
import time
import datetime
from pg_adapter import PG_Adapter
logger = logging.getLogger(__name__)
import os


class Orchestrator(OrchestratorBase):
    def __init__(self, target_symbol):
        super().__init__()
        self.target_symbol = target_symbol
        self.account_status = AccountStatus(EquityClient(target_symbol), target_symbol)
        self.order_status = OrderStatus()
        self.transact_client = TransactClient(target_symbol)
        self.equity_client = EquityClient(target_symbol)
        self.currency_client = CurrencyClient()
        self.transaction_trigger = TransactionTrigger()
        self.buyable_shares = self.account_status.calculate_buyable_shares()['shares']
        time.sleep(1)
        self.sellable_shares = self.account_status.calculate_sellable_shares()
        self.waiting_for_action = 'buy'
        self._bootstrap()
