"""
Modelos ORM de SQLAlchemy e implementaciones de repositorios concretos.

Cada modelo ORM se centra exclusivamente en la persistencia.
Las funciones de mapeo convierten entre entidades ORM y de 
dominio, de modo que la capa de dominio permanece completamente 
libre de importaciones de SQLAlchemy.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.domain.entities import Account, Customer, LedgerEntry, Transaction
from app.domain.enums import AccountStatus, CurrencyType, TransactionStatus, TransactionType
from app.domain.value_objects import AccountId, CustomerId, Email, Money
from app.repositories.database import Base

# ---------------------------------------------------------------------------
# ORM Models
# ---------------------------------------------------------------------------


class CustomerModel(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="ACTIVE")


class AccountModel(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="ACTIVE")


class TransactionModel(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="PENDING")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    from_account_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    to_account_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)


class LedgerEntryModel(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    account_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    transaction_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(6), nullable=False)  # DEBIT / CREDIT
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------------------------
# Mapper helpers — ORM <-> Domain
# ---------------------------------------------------------------------------


def _customer_to_orm(c: Customer) -> CustomerModel:
    return CustomerModel(
        id=c.id.value,
        name=c.name,
        email=c.email.value,
        status=c.status,
    )


def _orm_to_customer(row: CustomerModel) -> Customer:
    return Customer(
        id=CustomerId(row.id),
        name=row.name,
        email=Email(row.email),
        status=row.status,
    )


def _account_to_orm(a: Account) -> AccountModel:
    return AccountModel(
        id=a.id.value,
        customer_id=a.customer_id.value,
        currency=a.currency.value,
        balance=a.balance.amount,
        status=a.status.value,
    )


def _orm_to_account(row: AccountModel) -> Account:
    currency = CurrencyType(row.currency)
    return Account(
        id=AccountId(row.id),
        customer_id=CustomerId(row.customer_id),
        currency=currency,
        balance=Money(Decimal(str(row.balance)), currency),
        status=AccountStatus(row.status),
    )


def _transaction_to_orm(t: Transaction) -> TransactionModel:
    return TransactionModel(
        id=t.id,
        type=t.type.value,
        amount=t.amount.amount,
        currency=t.currency.value,
        status=t.status.value,
        created_at=t.created_at,
        from_account_id=t.from_account_id.value if t.from_account_id else None,
        to_account_id=t.to_account_id.value if t.to_account_id else None,
    )


def _orm_to_transaction(row: TransactionModel) -> Transaction:
    currency = CurrencyType(row.currency)
    return Transaction(
        id=row.id,
        type=TransactionType(row.type),
        amount=Money(Decimal(str(row.amount)), currency),
        currency=currency,
        status=TransactionStatus(row.status),
        created_at=row.created_at,
        from_account_id=AccountId(row.from_account_id) if row.from_account_id else None,
        to_account_id=AccountId(row.to_account_id) if row.to_account_id else None,
    )


def _ledger_to_orm(e: LedgerEntry) -> LedgerEntryModel:
    return LedgerEntryModel(
        id=e.id,
        account_id=e.account_id.value,
        transaction_id=e.transaction_id,
        direction=e.direction,
        amount=e.amount.amount,
        currency=e.amount.currency.value,
        created_at=e.created_at,
    )


def _orm_to_ledger(row: LedgerEntryModel) -> LedgerEntry:
    currency = CurrencyType(row.currency)
    return LedgerEntry(
        id=row.id,
        account_id=AccountId(row.account_id),
        transaction_id=row.transaction_id,
        direction=row.direction,
        amount=Money(Decimal(str(row.amount)), currency),
        created_at=row.created_at,
    )


# ---------------------------------------------------------------------------
# Concrete Repository Implementations
# ---------------------------------------------------------------------------


class SQLAlchemyCustomerRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def save(self, customer: Customer) -> Customer:
        existing = self._s.get(CustomerModel, customer.id.value)
        if existing:
            existing.name = customer.name
            existing.email = customer.email.value
            existing.status = customer.status
        else:
            self._s.add(_customer_to_orm(customer))
        self._s.flush()
        self._s.commit() 
        return customer

    def find_by_id(self, customer_id: CustomerId) -> Optional[Customer]:
        row = self._s.get(CustomerModel, customer_id.value)
        return _orm_to_customer(row) if row else None

    def find_by_email(self, email: str) -> Optional[Customer]:
        row = self._s.query(CustomerModel).filter_by(email=email.lower().strip()).first()
        return _orm_to_customer(row) if row else None

    def list_all(self) -> List[Customer]:
        return [_orm_to_customer(r) for r in self._s.query(CustomerModel).all()]


class SQLAlchemyAccountRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def save(self, account: Account) -> Account:
        existing = self._s.get(AccountModel, account.id.value)
        if existing:
            existing.balance = account.balance.amount
            existing.status = account.status.value
        else:
            self._s.add(_account_to_orm(account))
        self._s.flush()
        self._s.commit()
        return account

    def find_by_id(self, account_id: AccountId) -> Optional[Account]:
        row = self._s.get(AccountModel, account_id.value)
        return _orm_to_account(row) if row else None

    def find_by_customer_id(self, customer_id: CustomerId) -> List[Account]:
        rows = self._s.query(AccountModel).filter_by(customer_id=customer_id.value).all()
        return [_orm_to_account(r) for r in rows]

    def update_balance(self, account: Account) -> None:
        """Convenience alias — same as save() for balance updates."""
        self.save(account)


class SQLAlchemyTransactionRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def save(self, transaction: Transaction) -> Transaction:
        existing = self._s.get(TransactionModel, transaction.id)
        if existing:
            existing.status = transaction.status.value
        else:
            self._s.add(_transaction_to_orm(transaction))
        self._s.flush()
        return transaction

    def find_by_id(self, transaction_id: str) -> Optional[Transaction]:
        row = self._s.get(TransactionModel, transaction_id)
        return _orm_to_transaction(row) if row else None

    def find_by_account_id(
        self, account_id: AccountId, limit: int = 50, offset: int = 0
    ) -> List[Transaction]:
        account_id_str = account_id.value
        rows = (
            self._s.query(TransactionModel)
            .filter(
                (TransactionModel.from_account_id == account_id_str)
                | (TransactionModel.to_account_id == account_id_str)
            )
            .order_by(TransactionModel.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [_orm_to_transaction(r) for r in rows]

    def count_recent_by_account(self, account_id: AccountId, minutes: int) -> int:
        """Usado en VelocityRule risk strategy."""
        from sqlalchemy import text

        cutoff = f"NOW() - INTERVAL '{minutes} minutes'"
        # dialect-agnostic approach using func.now() may differ; use raw for clarity
        result = (
            self._s.query(func.count(TransactionModel.id))
            .filter(
                (
                    (TransactionModel.from_account_id == account_id.value)
                    | (TransactionModel.to_account_id == account_id.value)
                ),
                TransactionModel.created_at
                >= func.now() - func.make_interval(0, 0, 0, 0, 0, minutes),
            )
            .scalar()
        )
        return result or 0

    def sum_today_by_account(self, account_id: AccountId) -> Decimal:
        """Usado en DailyLimitRule risk strategy."""
        result = (
            self._s.query(func.coalesce(func.sum(TransactionModel.amount), 0))
            .filter(
                (
                    (TransactionModel.from_account_id == account_id.value)
                    | (TransactionModel.to_account_id == account_id.value)
                ),
                func.date(TransactionModel.created_at) == func.current_date(),
                TransactionModel.status == TransactionStatus.APPROVED.value,
            )
            .scalar()
        )
        return Decimal(str(result))


class SQLAlchemyLedgerRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def save(self, entry: LedgerEntry) -> LedgerEntry:
        self._s.add(_ledger_to_orm(entry))
        self._s.flush()
        return entry

    def find_by_account_id(self, account_id: AccountId) -> List[LedgerEntry]:
        rows = (
            self._s.query(LedgerEntryModel)
            .filter_by(account_id=account_id.value)
            .order_by(LedgerEntryModel.created_at.desc())
            .all()
        )
        return [_orm_to_ledger(r) for r in rows]

    def find_by_transaction_id(self, transaction_id: str) -> List[LedgerEntry]:
        rows = (
            self._s.query(LedgerEntryModel)
            .filter_by(transaction_id=transaction_id)
            .all()
        )
        return [_orm_to_ledger(r) for r in rows]