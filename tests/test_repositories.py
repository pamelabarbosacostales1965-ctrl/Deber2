"""
tests/test_repositories.py — 4+ tests for repository implementations.
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from app.domain.entities import Customer, Account, LedgerEntry
from app.domain.enums import AccountStatus, CurrencyType, TransactionStatus, TransactionType
from app.domain.value_objects import AccountId, CustomerId, Email, Money
from tests.conftest import make_account, make_customer


# ---------------------------------------------------------------------------
# CustomerRepository
# ---------------------------------------------------------------------------

class TestCustomerRepository:
    def test_save_and_find_by_id(self, customer_repo):
        customer = Customer(
            id=CustomerId("cust-001"),
            name="Bob",
            email=Email("bob@example.com"),
            status="ACTIVE",
        )
        customer_repo.save(customer)

        found = customer_repo.find_by_id(CustomerId("cust-001"))
        assert found is not None
        assert found.name == "Bob"
        assert found.email.value == "bob@example.com"

    def test_find_by_email(self, customer_repo):
        customer = Customer(
            id=CustomerId("cust-002"),
            name="Carol",
            email=Email("carol@example.com"),
            status="ACTIVE",
        )
        customer_repo.save(customer)

        found = customer_repo.find_by_email("carol@example.com")
        assert found is not None
        assert found.id.value == "cust-002"

    def test_find_by_id_missing_returns_none(self, customer_repo):
        result = customer_repo.find_by_id(CustomerId("does-not-exist"))
        assert result is None

    def test_update_on_save(self, customer_repo):
        """Saving an existing id should update the record, not create a duplicate."""
        customer = Customer(
            id=CustomerId("cust-003"),
            name="Dave",
            email=Email("dave@example.com"),
            status="ACTIVE",
        )
        customer_repo.save(customer)
        customer.status = "FROZEN"
        customer_repo.save(customer)

        found = customer_repo.find_by_id(CustomerId("cust-003"))
        assert found.status == "FROZEN"


# ---------------------------------------------------------------------------
# AccountRepository
# ---------------------------------------------------------------------------

class TestAccountRepository:
    def _make_account(self, account_id="acc-001", customer_id="cust-001") -> Account:
        currency = CurrencyType.USD
        return Account(
            id=AccountId(account_id),
            customer_id=CustomerId(customer_id),
            currency=currency,
            balance=Money(Decimal("100.00"), currency),
            status=AccountStatus.ACTIVE,
        )

    def test_save_and_find_by_id(self, account_repo):
        acc = self._make_account()
        account_repo.save(acc)

        found = account_repo.find_by_id(AccountId("acc-001"))
        assert found is not None
        assert found.balance.amount == Decimal("100.00")
        assert found.status == AccountStatus.ACTIVE

    def test_find_by_customer_id(self, account_repo):
        for i in range(3):
            account_repo.save(self._make_account(account_id=f"acc-{i}", customer_id="cust-X"))

        accounts = account_repo.find_by_customer_id(CustomerId("cust-X"))
        assert len(accounts) == 3

    def test_balance_update(self, account_repo):
        acc = self._make_account()
        account_repo.save(acc)
        acc.balance = Money(Decimal("250.00"), CurrencyType.USD)
        account_repo.save(acc)

        found = account_repo.find_by_id(AccountId("acc-001"))
        assert found.balance.amount == Decimal("250.00")

    def test_find_missing_returns_none(self, account_repo):
        result = account_repo.find_by_id(AccountId("ghost"))
        assert result is None


# ---------------------------------------------------------------------------
# LedgerRepository
# ---------------------------------------------------------------------------

class TestLedgerRepository:
    def test_save_and_find_by_account(self, ledger_repo):
        entry = LedgerEntry(
            id="le-001",
            account_id=AccountId("acc-001"),
            transaction_id="tx-001",
            direction="CREDIT",
            amount=Money(Decimal("50.00"), CurrencyType.USD),
        )
        ledger_repo.save(entry)

        entries = ledger_repo.find_by_account_id(AccountId("acc-001"))
        assert len(entries) == 1
        assert entries[0].direction == "CREDIT"
        assert entries[0].amount.amount == Decimal("50.00")

    def test_find_by_transaction_id(self, ledger_repo):
        for direction in ("DEBIT", "CREDIT"):
            ledger_repo.save(LedgerEntry(
                id=f"le-{direction}",
                account_id=AccountId("acc-001"),
                transaction_id="tx-transfer",
                direction=direction,
                amount=Money(Decimal("100.00"), CurrencyType.USD),
            ))

        entries = ledger_repo.find_by_transaction_id("tx-transfer")
        assert len(entries) == 2
        directions = {e.direction for e in entries}
        assert directions == {"DEBIT", "CREDIT"}