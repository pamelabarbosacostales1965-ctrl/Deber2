from __future__ import annotations

from decimal import Decimal
from typing import Protocol, runtime_checkable

from app.domain.entities import Transaction
from app.domain.value_objects import Money


@runtime_checkable
class FeeStrategy(Protocol):
    def calculate_fee(self, amount: Money) -> Money: ...


@runtime_checkable
class RiskStrategy(Protocol):
    """
    Genera app.domain.exceptions.FraudDetected si 
    la transacción infringe la regla. Devuelve 
    None si la transacción es aceptable.
    """
    def evaluate(self, transaction: Transaction) -> None: ...