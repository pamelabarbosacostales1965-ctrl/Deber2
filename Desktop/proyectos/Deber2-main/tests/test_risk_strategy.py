import pytest
from app.patterns.risk_strategy import MaxAmountStrategy

def test_max_amount_risk():
    strategy = MaxAmountStrategy(500)
    assert strategy.validate(400) is True
    assert strategy.validate(600) is False