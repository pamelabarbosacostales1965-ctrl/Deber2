from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from .enums import AccountStatus, TransactionStatus, TransactionType, CurrencyType
from .value_objects import CustomerId, AccountId, Email, Money
from .exceptions import DomainError, InvalidTransaction


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Customer:
    """
    Domain entity representing a bank customer.
    
    Attributes:
        id: Unique customer identifier
        name: Customer's full name (non-empty)
        email: Customer's email (EmailValue Object)
        status: Account status (default: ACTIVE)
    
    Invariants:
        - name must not be empty or whitespace-only
    """
    id: CustomerId
    name: str
    email: Email
    status: str = "ACTIVE"

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise DomainError("Customer.name vacío")


@dataclass
class Account:
    """
    Domain entity representing a customer's bank account (wallet).
    
    Attributes:
        id: Unique account identifier
        customer_id: Reference to the account owner
        currency: Account's currency (e.g., USD)
        balance: Current balance as Money value object
        status: Account status (default: ACTIVE)
    
    Invariants:
        - balance currency must match account currency
    """
    """
    Domain entity representing a financial transaction.
    
    Attributes:
        id: Unique transaction identifier
        type: Transaction type (DEPOSIT, WITHDRAW, TRANSFER)
        amount: Transaction amount as Money value object
        currency: Transaction currency
        status: Transaction status (default: PENDING)
        created_at: Timestamp of transaction creation (UTC)
        from_account_id: Source account (for TRANSFER)
        to_account_id: Destination account (for TRANSFER)
    
    Invariants:
        - amount must be greater than 0
        - transaction currency must match amount currency
        - TRANSFER transactions must have both from and to accounts
        - from_account_id cannot equal to_account_id
    """
    id: str
    type: TransactionType
    amount: Money
    currency: CurrencyType
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = field(default_factory=utcnow)
ance.currency != self.currency:
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
    direction: str  # "DEBIT" o "CREDIT"
    amount: Money
    created_at: datetime = field(default_factory=utcnow)

    def __post_init__(self):
        if self.direction not in ("DEBIT", "CREDIT"):
            raise DomainError("LedgerEntry.direction debe ser DEBIT o CREDIT")
