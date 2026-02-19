import pytest
from app.patterns.fee_strategy import NoFee, FlatFee, PercentFee

def test_no_fee():
    strategy = NoFee()
    assert strategy.calculate(100.0) == 0.0

def test_flat_fee():
    strategy = FlatFee()
    assert strategy.calculate(100.0) == 5.0