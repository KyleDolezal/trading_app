import logging
logger = logging.getLogger(__name__)
import pytest
from app import App

def test_get_buyable_shares():
    assert App.get_buyable_shares(100)== 75