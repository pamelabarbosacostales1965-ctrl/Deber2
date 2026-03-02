"""
tests/test_services.py — 5+ tests for CustomerService, AccountService, TransactionService.
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from app.domain.enums import TransactionStatus, TransactionType
from app.domain.exceptions import (
    AccountFrozen,
    DomainError,
    FraudDetected,
    InsufficientFundsError,
)
from app.domain.value_objects import AccountId, Money
from app.domain.enums import CurrencyType
from app.services.strategies import FeeStrategy, RiskStrategy
from app.domain.entities import Transaction
from tests.conftest import make_account, make_customer


# ---------------------------------------------------------------------------
# CustomerService
# ---------------------------------------------------------------------------

class TestCustomerService:
    def test_create_customer_success(self, customer_service):
        customer = customer_service.create_customer("Alice", "alice@test.com")
        assert customer.name == "Alice"
        assert customer.email.value == "alice@test.com"

    def test_duplicate_email_raises(self, customer_service):
        customer_service.create_customer("Alice", "alice@test.com")
        with pytest.raises(DomainError, match="ya registrado"):
            customer_service.create_customer("Alice 2", "alice@test.com")

    def test_get_nonexistent_customer_raises(self, customer_service):
        with pytest.raises(DomainError, match="no encontrado"):
            customer_service.get_customer("bad-id")


# ---------------------------------------------------------------------------
# AccountService
# ---------------------------------------------------------------------------

class TestAccountService:
    def test_create_account_for_existing_customer(self, customer_service, account_service):
        customer = make_customer(customer_service)
        account = make_account(account_service, customer.id.value)

        assert account.balance.amount == Decimal("0.00")
        assert account.customer_id.value == customer.id.value

    def test_create_account_for_missing_customer_raises(self, account_service):
        with pytest.raises(DomainError, match="no encontrado"):
            account_service.create_account("ghost-id")


# ---------------------------------------------------------------------------
# TransactionService
# ---------------------------------------------------------------------------

class TestTransactionService:
    def _setup(self, customer_service, account_service, transaction_service):
        customer = make_customer(customer_service)
        account = make_account(account_service, customer.id.value)
        return account

    def test_deposit_increases_balance(
        self, customer_service, account_service, transaction_service
    ):
        acc = self._setup(customer_service, account_service, transaction_service)
        tx = transaction_service.deposit(acc.id.value, Decimal("200.00"))

        assert tx.status == TransactionStatus.APPROVED
        assert tx.type == TransactionType.DEPOSIT

        updated = account_service.get_account(acc.id.value)
        assert updated.balance.amount == Decimal("200.00")

    def test_withdraw_decreases_balance(
        self, customer_service, account_service, transaction_service
    ):
        acc = self._setup(customer_service, account_service, transaction_service)
        transaction_service.deposit(acc.id.value, Decimal("500.00"))
        tx = transaction_service.withdraw(acc.id.value, Decimal("150.00"))

        assert tx.status == TransactionStatus.APPROVED
        updated = account_service.get_account(acc.id.value)
        assert updated.balance.amount == Decimal("350.00")

    def test_withdraw_insufficient_funds_raises(
        self, customer_service, account_service, transaction_service
    ):
        acc = self._setup(customer_service, account_service, transaction_service)
        transaction_service.deposit(acc.id.value, Decimal("50.00"))

        with pytest.raises(InsufficientFundsError):
            transaction_service.withdraw(acc.id.value, Decimal("200.00"))

    def test_transfer_moves_funds_atomically(
        self, customer_service, account_service, transaction_service
    ):
        c1 = make_customer(customer_service, "Sender", "sender@test.com")
        c2 = make_customer(customer_service, "Receiver", "receiver@test.com")
        acc1 = make_account(account_service, c1.id.value)
        acc2 = make_account(account_service, c2.id.value)

        transaction_service.deposit(acc1.id.value, Decimal("1000.00"))
        tx = transaction_service.transfer(acc1.id.value, acc2.id.value, Decimal("300.00"))

        assert tx.status == TransactionStatus.APPROVED
        assert tx.type == TransactionType.TRANSFER

        updated1 = account_service.get_account(acc1.id.value)
        updated2 = account_service.get_account(acc2.id.value)
        assert updated1.balance.amount == Decimal("700.00")
        assert updated2.balance.amount == Decimal("300.00")

    def test_risk_strategy_rejection_rolls_back(
        self, customer_service, account_service, account_repo, transaction_repo, ledger_repo, session
    ):
        """When risk strategy raises FraudDetected, balances must be unchanged."""
        from app.services.transaction_service import TransactionService

        class AlwaysRejectRisk:
            def evaluate(self, tx: Transaction) -> None:
                raise FraudDetected("Blocked by test risk rule")

        svc = TransactionService(
            account_repo=account_repo,
            transaction_repo=transaction_repo,
            ledger_repo=ledger_repo,
            session=session,
            risk_strategy=AlwaysRejectRisk(),
        )

        customer = make_customer(customer_service)
        acc = make_account(account_service, customer.id.value)

        # Deposit without risk (use default service)
        from app.services.transaction_service import TransactionService as TxSvc
        base_svc = TxSvc(account_repo, transaction_repo, ledger_repo, session)
        base_svc.deposit(acc.id.value, Decimal("500.00"))

        with pytest.raises(FraudDetected):
            svc.deposit(acc.id.value, Decimal("100.00"))

        # Balance should be unchanged at 500
        updated = account_service.get_account(acc.id.value)
        assert updated.balance.amount == Decimal("500.00")

    def test_fee_strategy_applied_on_deposit(
        self, customer_service, account_service, account_repo, transaction_repo, ledger_repo, session
    ):
        """A flat fee strategy should reduce net credited amount."""
        from app.services.transaction_service import TransactionService
        from app.domain.value_objects import Money
        from app.domain.enums import CurrencyType

        class FlatOneDollarFee:
            def calculate_fee(self, amount: Money) -> Money:
                return Money(Decimal("1.00"), amount.currency)

        svc = TransactionService(
            account_repo=account_repo,
            transaction_repo=transaction_repo,
            ledger_repo=ledger_repo,
            session=session,
            fee_strategy=FlatOneDollarFee(),
        )

        customer = make_customer(customer_service, "FeeTest", "fee@test.com")
        acc = make_account(account_service, customer.id.value)

        svc.deposit(acc.id.value, Decimal("100.00"))
        updated = account_service.get_account(acc.id.value)
        # Net = 100 - 1 fee = 99
        assert updated.balance.amount == Decimal("99.00")
        