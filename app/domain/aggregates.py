from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from decimal import Decimal

from .entities import Account, LedgerEntry, Transaction
from .enums import AccountStatus, TransactionStatus, TransactionType
from .value_objects import Money
from .exceptions import AccountFrozen, InsufficientFundsError, DomainError


@dataclass
class BankingAggregate:
    """Aggregate raíz simplificado para operaciones sobre una cuenta."""
    account: Account
    ledger: List[LedgerEntry] = field(default_factory=list)

    def _assert_operable(self) -> None:
        if self.account.status != AccountStatus.ACTIVE:
            raise AccountFrozen(f"Cuenta no operable: {self.account.status}")

    def apply_deposit(self, tx: Transaction, credit_entry: LedgerEntry) -> None:
        self._assert_operable()
        if tx.type != TransactionType.DEPOSIT:
            raise DomainError("apply_deposit requiere tx DEPOSIT")

        self.account.balance = self.account.balance.add(tx.amount)
        self.ledger.append(credit_entry)

    def apply_withdraw(self, tx: Transaction, debit_entry: LedgerEntry) -> None:
        self._assert_operable()
        if tx.type != TransactionType.WITHDRAW:
            raise DomainError("apply_withdraw requiere tx WITHDRAW")

        if self.account.balance.amount < tx.amount.amount:
            raise InsufficientFundsError("Fondos insuficientes")

        self.account.balance = self.account.balance.sub(tx.amount)
        self.ledger.append(debit_entry)

    def mark_tx(self, tx: Transaction, status: TransactionStatus) -> None:
        tx.status = status
