from __future__ import annotations
from enum import Enum


class AccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    TRANSFER = "TRANSFER"


class CurrencyType(str, Enum):
    USD = "USD"   # puedes dejar solo USD, pero modelado
    EUR = "EUR"
