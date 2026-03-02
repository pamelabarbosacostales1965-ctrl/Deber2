from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Literal

from .enums import AccountStatus, TransactionStatus, TransactionType, CurrencyType
from .value_objects import CustomerId, AccountId, Email, Money
from .exceptions import DomainError, InvalidTransaction


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


LEDGER_DIRECTIONS = ("DEBIT", "CREDIT")
LedgerDirection = Literal["DEBIT", "CREDIT"]


@dataclass
class Customer:
    id: CustomerId
    name: str
    email: Email
    status: str = "ACTIVE"

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise DomainError("Customer.name vacío")


@dataclass
class Account:
    id: AccountId
    customer_id: CustomerId
    currency: CurrencyType
    balance: Money
    status: AccountStatus = AccountStatus.ACTIVE

    def __post_init__(self):
        if self.balance.currency != self.currency:
            raise DomainError("Account.balance.currency != Account.currency")


@dataclass
class Transaction:
    id: str
    type: TransactionType
    amount: Money
    currency: CurrencyType
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = field(default_factory=utcnow)

    # Para transfer
    from_account_id: Optional[AccountId] = None
    to_account_id: Optional[AccountId] = None

    def __post_init__(self):
        if self.amount.amount <= Decimal("0.00"):
            raise InvalidTransaction("Monto debe ser > 0")
        if self.currency != self.amount.currency:
            raise InvalidTransaction("Transaction.currency != amount.currency")

        if self.type == TransactionType.TRANSFER:
            if not self.from_account_id or not self.to_account_id:
                raise InvalidTransaction("Transfer requiere from_account_id y to_account_id")
            if self.from_account_id == self.to_account_id:
                raise InvalidTransaction("from_account_id y to_account_id no pueden ser iguales")


@dataclass
class LedgerEntry:
    id: str
    account_id: AccountId
    transaction_id: str
    direction: LedgerDirection  # "DEBIT" or "CREDIT"
    amount: Money
    created_at: datetime = field(default_factory=utcnow)

    def __post_init__(self):
        if self.direction not in LEDGER_DIRECTIONS:
            raise DomainError("LedgerEntry.direction debe ser DEBIT o CREDIT")