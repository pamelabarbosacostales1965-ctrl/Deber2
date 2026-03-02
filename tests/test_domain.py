import pytest
from decimal import Decimal

from app.domain.enums import CurrencyType, AccountStatus, TransactionType
from app.domain.value_objects import Money, Email, CustomerId, AccountId
from app.domain.entities import Customer, Account, Transaction, LedgerEntry
from app.domain.aggregates import BankingAggregate
from app.domain.exceptions import DomainError, InvalidTransaction, InsufficientFundsError, AccountFrozen


def test_email_validates_and_normalizes():
    e = Email("  TEST@Example.com ")
    assert e.value == "test@example.com"
    with pytest.raises(DomainError):
        Email("not-an-email")


def test_money_is_decimal_and_non_negative_and_2dp():
    m = Money(Decimal("10.129"), CurrencyType.USD)
    assert str(m.amount) == "10.13"
    with pytest.raises(DomainError):
        Money(Decimal("-1.00"), CurrencyType.USD)
    with pytest.raises(DomainError):
        Money("10.00", CurrencyType.USD)  # no Decimal


def test_account_balance_currency_must_match_account_currency():
    cid = CustomerId("c1")
    aid = AccountId("a1")
    with pytest.raises(DomainError):
        Account(id=aid, customer_id=cid, currency=CurrencyType.EUR, balance=Money(Decimal("0.00"), CurrencyType.USD))


def test_transaction_amount_must_be_positive():
    with pytest.raises(InvalidTransaction):
        Transaction(id="t1", type=TransactionType.DEPOSIT,
                    amount=Money(Decimal("0.00"), CurrencyType.USD),
                    currency=CurrencyType.USD)


def test_transfer_requires_from_and_to_and_not_equal():
    from_id = AccountId("a1")
    to_id = AccountId("a2")
    tx = Transaction(id="t2", type=TransactionType.TRANSFER,
                     amount=Money(Decimal("5.00"), CurrencyType.USD),
                     currency=CurrencyType.USD,
                     from_account_id=from_id, to_account_id=to_id)
    assert tx.from_account_id.value == "a1"

    with pytest.raises(InvalidTransaction):
        Transaction(id="t3", type=TransactionType.TRANSFER,
                    amount=Money(Decimal("5.00"), CurrencyType.USD),
                    currency=CurrencyType.USD,
                    from_account_id=from_id, to_account_id=from_id)

    with pytest.raises(InvalidTransaction):
        Transaction(id="t4", type=TransactionType.TRANSFER,
                    amount=Money(Decimal("5.00"), CurrencyType.USD),
                    currency=CurrencyType.USD,
                    from_account_id=None, to_account_id=to_id)


def test_ledger_entry_direction_validation():
    le = LedgerEntry(id="l1", account_id=AccountId("a1"), transaction_id="t1",
                     direction="CREDIT", amount=Money(Decimal("1.00"), CurrencyType.USD))
    assert le.direction == "CREDIT"
    with pytest.raises(DomainError):
        LedgerEntry(id="l2", account_id=AccountId("a1"), transaction_id="t1",
                    direction="XXX", amount=Money(Decimal("1.00"), CurrencyType.USD))


def test_deposit_updates_balance_and_adds_ledger():
    cid = CustomerId("c1")
    acc = Account(id=AccountId("a1"), customer_id=cid, currency=CurrencyType.USD,
                  balance=Money(Decimal("10.00"), CurrencyType.USD))
    agg = BankingAggregate(account=acc)

    tx = Transaction(id="t1", type=TransactionType.DEPOSIT,
                     amount=Money(Decimal("5.00"), CurrencyType.USD),
                     currency=CurrencyType.USD)
    le = LedgerEntry(id="l1", account_id=acc.id, transaction_id=tx.id,
                     direction="CREDIT", amount=tx.amount)

    agg.apply_deposit(tx, le)
    assert agg.account.balance.amount == Decimal("15.00")
    assert len(agg.ledger) == 1


def test_withdraw_insufficient_funds_raises():
    cid = CustomerId("c1")
    acc = Account(id=AccountId("a1"), customer_id=cid, currency=CurrencyType.USD,
                  balance=Money(Decimal("2.00"), CurrencyType.USD))
    agg = BankingAggregate(account=acc)

    tx = Transaction(id="t1", type=TransactionType.WITHDRAW,
                     amount=Money(Decimal("5.00"), CurrencyType.USD),
                     currency=CurrencyType.USD)
    le = LedgerEntry(id="l1", account_id=acc.id, transaction_id=tx.id,
                     direction="DEBIT", amount=tx.amount)

    with pytest.raises(InsufficientFundsError):
        agg.apply_withdraw(tx, le)


def test_frozen_account_cannot_operate():
    cid = CustomerId("c1")
    acc = Account(id=AccountId("a1"), customer_id=cid, currency=CurrencyType.USD,
                  balance=Money(Decimal("10.00"), CurrencyType.USD),
                  status=AccountStatus.FROZEN)
    agg = BankingAggregate(account=acc)

    tx = Transaction(id="t1", type=TransactionType.DEPOSIT,
                     amount=Money(Decimal("1.00"), CurrencyType.USD),
                     currency=CurrencyType.USD)
    le = LedgerEntry(id="l1", account_id=acc.id, transaction_id=tx.id,
                     direction="CREDIT", amount=tx.amount)

    with pytest.raises(AccountFrozen):
        agg.apply_deposit(tx, le)
