import logging
logger = logging.getLogger(__name__)
import pytest
from app import App

def test_get_buyable_shares():
    assert App.get_buyable_shares(100)== 75

def test_will_override():
    assert App.will_override('hold', 2, 1) == False

    assert App.will_override('sell override', 2, 3) == False

    assert App.will_override('sell override', 2, 1) == True