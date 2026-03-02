"""
AccountService — use cases for account lifecycle.
"""
from __future__ import annotations

import uuid
from typing import List

from app.domain.entities import Account
from app.domain.enums import AccountStatus, CurrencyType
from app.domain.exceptions import DomainError
from app.domain.value_objects import AccountId, CustomerId, Money
from app.repositories.interfaces import AccountRepository, CustomerRepository

from decimal import Decimal


class AccountService:
    def __init__(
        self,
        account_repo: AccountRepository,
        customer_repo: CustomerRepository,
    ) -> None:
        self._accounts = account_repo
        self._customers = customer_repo

    # ------------------------------------------------------------------
    # Use case: create account
    # ------------------------------------------------------------------
    def create_account(
        self,
        customer_id: str,
        currency: str = "USD",
    ) -> Account:
        """
        Creates a new wallet for an existing customer.
        Raises DomainError if the customer doesn't exist.
        """
        customer = self._customers.find_by_id(CustomerId(customer_id))
        if customer is None:
            raise DomainError(f"Cliente no encontrado: {customer_id}")

        try:
            currency_enum = CurrencyType(currency.upper())
        except ValueError:
            raise DomainError(f"Moneda no soportada: {currency}")

        account = Account(
            id=AccountId(str(uuid.uuid4())),
            customer_id=CustomerId(customer_id),
            currency=currency_enum,
            balance=Money(Decimal("0.00"), currency_enum),
            status=AccountStatus.ACTIVE,
        )
        return self._accounts.save(account)

    # ------------------------------------------------------------------
    # Use case: get account
    # ------------------------------------------------------------------
    def get_account(self, account_id: str) -> Account:
        account = self._accounts.find_by_id(AccountId(account_id))
        if account is None:
            raise DomainError(f"Cuenta no encontrada: {account_id}")
        return account

    # ------------------------------------------------------------------
    # Use case: get balance
    # ------------------------------------------------------------------
    def get_balance(self, account_id: str) -> Money:
        return self.get_account(account_id).balance

    # ------------------------------------------------------------------
    # Use case: list accounts for a customer
    # ------------------------------------------------------------------
    def list_accounts_for_customer(self, customer_id: str) -> List[Account]:
        return self._accounts.find_by_customer_id(CustomerId(customer_id))

    # ------------------------------------------------------------------
    # Ayudantes internos utilizados por TransactionService
    # ------------------------------------------------------------------
    def _require_active(self, account: Account) -> None:
        from app.domain.exceptions import AccountFrozen
        if account.status != AccountStatus.ACTIVE:
            raise AccountFrozen(
                f"Cuenta {account.id.value} no operable: {account.status.value}"
            )