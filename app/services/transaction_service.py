"""
Servicio de Transacción: casos de uso financieros clave.

Las estrategias de comisiones y riesgos se inyectan durante la construcción.
Si no se proporciona ninguna estrategia, se establece el comportamiento 
predeterminado sin comisiones ni verificación de riesgos.
"""
from __future__ import annotations

import uuid
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.aggregates import BankingAggregate
from app.domain.entities import Account, LedgerEntry, Transaction
from app.domain.enums import CurrencyType, TransactionStatus, TransactionType
from app.domain.exceptions import DomainError, FraudDetected, InsufficientFundsError
from app.domain.value_objects import AccountId, Money
from app.repositories.interfaces import (
    AccountRepository,
    LedgerRepository,
    TransactionRepository,
)
from app.services.strategies import FeeStrategy, RiskStrategy


class _NoFee:
    """Null-object fee strategy — applies zero fee."""
    def calculate_fee(self, amount: Money) -> Money:
        return Money(Decimal("0.00"), amount.currency)


class _NoRisk:
    """Null-object risk strategy — always passes."""
    def evaluate(self, transaction: Transaction) -> None:
        return None


class TransactionService:
    def __init__(
        self,
        account_repo: AccountRepository,
        transaction_repo: TransactionRepository,
        ledger_repo: LedgerRepository,
        session: Session,
        fee_strategy: Optional[FeeStrategy] = None,
        risk_strategy: Optional[RiskStrategy] = None,
    ) -> None:
        self._accounts = account_repo
        self._transactions = transaction_repo
        self._ledger = ledger_repo
        self._session = session
        self._fee: FeeStrategy = fee_strategy or _NoFee()  # type: ignore[assignment]
        self._risk: RiskStrategy = risk_strategy or _NoRisk()  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Use case: deposit
    # ------------------------------------------------------------------
    def deposit(self, account_id: str, amount: Decimal, currency: str = "USD") -> Transaction:
        try:
            currency_enum = CurrencyType(currency.upper())
            money = Money(amount, currency_enum)
            acc = self._require_account(account_id)

            tx = Transaction(
                id=str(uuid.uuid4()),
                type=TransactionType.DEPOSIT,
                amount=money,
                currency=currency_enum,
                status=TransactionStatus.PENDING,
                to_account_id=AccountId(account_id),
            )

            self._risk.evaluate(tx)

            fee = self._fee.calculate_fee(money)
            net = money.sub(fee) if fee.amount > Decimal("0.00") else money

            tx.amount = net
            aggregate = BankingAggregate(account=acc)
            credit_entry = self._make_ledger(acc.id.value, tx.id, "CREDIT", net)
            aggregate.apply_deposit(tx, credit_entry)
            aggregate.mark_tx(tx, TransactionStatus.APPROVED)

            self._persist_deposit(acc, tx, credit_entry, fee)

            return tx

        except (FraudDetected, InsufficientFundsError) as e:
            self._reject_if_persisted(account_id, str(e))
            raise
        except DomainError:
            raise
        except Exception as e:
            raise DomainError(f"Error inesperado en deposit: {e}") from e

    # ------------------------------------------------------------------
    # Use case: withdraw
    # ------------------------------------------------------------------
    def withdraw(self, account_id: str, amount: Decimal, currency: str = "USD") -> Transaction:
        try:
            currency_enum = CurrencyType(currency.upper())
            money = Money(amount, currency_enum)
            acc = self._require_account(account_id)

            fee = self._fee.calculate_fee(money)
            total_debit = money.add(fee) if fee.amount > Decimal("0.00") else money

            tx = Transaction(
                id=str(uuid.uuid4()),
                type=TransactionType.WITHDRAW,
                amount=total_debit,
                currency=currency_enum,
                status=TransactionStatus.PENDING,
                from_account_id=AccountId(account_id),
            )

            self._risk.evaluate(tx)

            aggregate = BankingAggregate(account=acc)
            debit_entry = self._make_ledger(acc.id.value, tx.id, "DEBIT", total_debit)
            aggregate.apply_withdraw(tx, debit_entry)
            aggregate.mark_tx(tx, TransactionStatus.APPROVED)

            self._persist_single(acc, tx, debit_entry)

            return tx

        except (FraudDetected, InsufficientFundsError):
            raise
        except DomainError:
            raise
        except Exception as e:
            raise DomainError(f"Error inesperado en withdraw: {e}") from e

    # ------------------------------------------------------------------
    # Use case: transfer (atomic — single DB transaction)
    # ------------------------------------------------------------------
    def transfer(
        self,
        from_account_id: str,
        to_account_id: str,
        amount: Decimal,
        currency: str = "USD",
    ) -> Transaction:
        """
        Atomic transfer: debit source + credit destination in one DB transaction.
        Rolls back entirely if any step fails.
        """
        if from_account_id == to_account_id:
            raise DomainError("No se puede transferir a la misma cuenta")

        try:
            currency_enum = CurrencyType(currency.upper())
            money = Money(amount, currency_enum)

            source = self._require_account(from_account_id)
            dest = self._require_account(to_account_id)

            fee = self._fee.calculate_fee(money)
            total_debit = money.add(fee) if fee.amount > Decimal("0.00") else money

            tx = Transaction(
                id=str(uuid.uuid4()),
                type=TransactionType.TRANSFER,
                amount=money,
                currency=currency_enum,
                status=TransactionStatus.PENDING,
                from_account_id=AccountId(from_account_id),
                to_account_id=AccountId(to_account_id),
            )

            self._risk.evaluate(tx)

            # Build aggregates and apply movements
            source_agg = BankingAggregate(account=source)
            dest_agg = BankingAggregate(account=dest)

            debit_entry = self._make_ledger(from_account_id, tx.id, "DEBIT", total_debit)
            credit_entry = self._make_ledger(to_account_id, tx.id, "CREDIT", money)

            source_agg.apply_withdraw(
                Transaction(
                    id=tx.id,
                    type=TransactionType.WITHDRAW,
                    amount=total_debit,
                    currency=currency_enum,
                    from_account_id=AccountId(from_account_id),
                ),
                debit_entry,
            )
            dest_agg.apply_deposit(
                Transaction(
                    id=tx.id,
                    type=TransactionType.DEPOSIT,
                    amount=money,
                    currency=currency_enum,
                    to_account_id=AccountId(to_account_id),
                ),
                credit_entry,
            )

            tx.status = TransactionStatus.APPROVED

            # Persist everything atomically
            self._transactions.save(tx)
            self._accounts.save(source_agg.account)
            self._accounts.save(dest_agg.account)
            self._ledger.save(debit_entry)
            self._ledger.save(credit_entry)
            self._session.commit()

            return tx

        except (FraudDetected, InsufficientFundsError):
            self._session.rollback()
            raise
        except DomainError:
            self._session.rollback()
            raise
        except Exception as e:
            self._session.rollback()
            raise DomainError(f"Error inesperado en transfer: {e}") from e

    # ------------------------------------------------------------------
    # Use case: list transactions
    # ------------------------------------------------------------------
    def list_transactions(
        self, account_id: str, limit: int = 50, offset: int = 0
    ) -> List[Transaction]:
        return self._transactions.find_by_account_id(
            AccountId(account_id), limit=limit, offset=offset
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _require_account(self, account_id: str) -> Account:
        acc = self._accounts.find_by_id(AccountId(account_id))
        if acc is None:
            raise DomainError(f"Cuenta no encontrada: {account_id}")
        return acc

    def _make_ledger(
        self, account_id: str, tx_id: str, direction: str, amount: Money
    ) -> LedgerEntry:
        return LedgerEntry(
            id=str(uuid.uuid4()),
            account_id=AccountId(account_id),
            transaction_id=tx_id,
            direction=direction,
            amount=amount,
        )

    def _persist_deposit(
        self,
        acc: Account,
        tx: Transaction,
        entry: LedgerEntry,
        fee: Money,
    ) -> None:
        self._transactions.save(tx)
        self._accounts.save(acc)
        self._ledger.save(entry)
        # If there's a fee, create a fee ledger entry as a debit
        if fee.amount > Decimal("0.00"):
            fee_entry = self._make_ledger(acc.id.value, tx.id, "DEBIT", fee)
            self._ledger.save(fee_entry)
        self._session.commit()

    def _persist_single(
        self, acc: Account, tx: Transaction, entry: LedgerEntry
    ) -> None:
        self._transactions.save(tx)
        self._accounts.save(acc)
        self._ledger.save(entry)
        self._session.commit()

    def _reject_if_persisted(self, account_id: str, reason: str) -> None:
        """
        If a transaction was saved before rejection, this is where
        we'd update its status. For PENDING->REJECTED transitions
        the Facade handles this; here we just rollback.
        """
        self._session.rollback()