from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone


def utcnow():
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = utcnow()


@dataclass(frozen=True)
class CustomerCreated(DomainEvent):
    customer_id: str = ""


@dataclass(frozen=True)
class AccountCreated(DomainEvent):
    account_id: str = ""


@dataclass(frozen=True)
class TransactionApproved(DomainEvent):
    transaction_id: str = ""
