"""
Banking Facade - Orchestrates application services

Implements the Facade pattern to provide a unified interface for:
- Customer management
- Account operations
- Transaction processing (deposit, withdraw, transfer)
- Fee and risk strategy management

This facade abstracts the complexity of multiple services and protocols.
"""

from decimal import Decimal
from typing import List, Optional

from app.application.dtos import (
    AccountDetailResponse, CreateAccountRequest, CreateAccountResponse,
    CreateCustomerRequest, CreateCustomerResponse,
    DepositRequest, DepositResponse,
    TransactionResponse, TransferRequest, TransferResponse,
    WithdrawRequest, WithdrawResponse,
)
from app.domain.enums import CurrencyType
from app.domain.exceptions import DomainError
from app.domain.value_objects import Money


class BankingFacade:
    def __init__(
        self,
        customer_service,
        account_service,
        transaction_service,
        fee_strategy,
        risk_strategy,
    ):
        self.customer_service = customer_service
        self.account_service = account_service
        self.transaction_service = transaction_service
        self.fee_strategy = fee_strategy
        self.risk_strategy = risk_strategy

    def create_customer(self, request: CreateCustomerRequest) -> CreateCustomerResponse:
        try:
            customer = self.customer_service.create_customer(
                name=request.name,
                email=request.email,
            )
            return CreateCustomerResponse(
                customer_id=customer.id.value,
                name=customer.name,
                email=customer.email.value,
            )
        except Exception as e:
            raise DomainError(f"Error creating customer: {str(e)}")

    def create_account(self, request: CreateAccountRequest) -> CreateAccountResponse:
        try:
            account = self.account_service.create_account(
                customer_id=request.customer_id,
                currency=request.currency,
            )
            return CreateAccountResponse(
                account_id=account.id.value,
                customer_id=account.customer_id.value,
                balance=float(account.balance.amount),
                currency=account.currency.value,
                status=account.status.value,
            )
        except Exception as e:
            raise DomainError(f"Error creating account: {str(e)}")

    def deposit(self, request: DepositRequest) -> DepositResponse:
        try:
            amount_decimal = Decimal(str(request.amount))
            currency = CurrencyType(request.currency.upper())

            transaction = self.transaction_service.deposit(
                account_id=request.account_id,
                amount=amount_decimal,
                currency=request.currency,
            )

            # calculate_fee expects Money
            fee_money = self.fee_strategy.calculate_fee(Money(amount_decimal, currency))
            account = self.account_service.get_account(request.account_id)

            return DepositResponse(
                transaction_id=transaction.id,
                account_id=account.id.value,
                new_balance=float(account.balance.amount),
                status=transaction.status.value,
                fee_applied=float(fee_money.amount),
            )
        except Exception as e:
            raise DomainError(f"Error in deposit: {str(e)}")

    def withdraw(self, request: WithdrawRequest) -> WithdrawResponse:
        try:
            amount_decimal = Decimal(str(request.amount))
            currency = CurrencyType(request.currency.upper())

            account = self.account_service.get_account(request.account_id)
            if float(account.balance.amount) < request.amount:
                raise DomainError("Insufficient funds")

            transaction = self.transaction_service.withdraw(
                account_id=request.account_id,
                amount=amount_decimal,
                currency=request.currency,
            )

            fee_money = self.fee_strategy.calculate_fee(Money(amount_decimal, currency))
            account = self.account_service.get_account(request.account_id)

            return WithdrawResponse(
                transaction_id=transaction.id,
                account_id=account.id.value,
                new_balance=float(account.balance.amount),
                status=transaction.status.value,
                fee_applied=float(fee_money.amount),
            )
        except Exception as e:
            raise DomainError(f"Error in withdraw: {str(e)}")

    def transfer(self, request: TransferRequest) -> TransferResponse:
        try:
            amount_decimal = Decimal(str(request.amount))
            currency = CurrencyType(request.currency.upper())

            from_account = self.account_service.get_account(request.from_account_id)
            if float(from_account.balance.amount) < request.amount:
                raise DomainError("Insufficient funds")

            transaction = self.transaction_service.transfer(
                from_account_id=request.from_account_id,
                to_account_id=request.to_account_id,
                amount=amount_decimal,
                currency=request.currency,
            )

            fee_money = self.fee_strategy.calculate_fee(Money(amount_decimal, currency))

            return TransferResponse(
                transaction_id=transaction.id,
                from_account_id=request.from_account_id,
                to_account_id=request.to_account_id,
                amount=request.amount,
                status=transaction.status.value,
                fee_applied=float(fee_money.amount),
            )
        except Exception as e:
            raise DomainError(f"Error in transfer: {str(e)}")

    def get_account(self, account_id: str) -> AccountDetailResponse:
        try:
            account = self.account_service.get_account(account_id)
            transactions = self.transaction_service.list_transactions(account_id)

            transaction_responses = [
                TransactionResponse(
                    transaction_id=t.id,
                    transaction_type=t.type.value,
                    amount=float(t.amount.amount),
                    currency=t.amount.currency.value,  # .value
                    status=t.status.value,
                    created_at=t.created_at,           # datetime, no str
                )
                for t in transactions
            ]

            return AccountDetailResponse(
                account_id=account.id.value,
                customer_id=account.customer_id.value,
                balance=float(account.balance.amount),
                currency=account.currency.value,       # .value
                status=account.status.value,
                created_at=None,
                transactions=transaction_responses,
            )
        except Exception as e:
            raise DomainError(f"Error getting account: {str(e)}")

    def list_transactions(self, account_id: str) -> List[TransactionResponse]:
        try:
            transactions = self.transaction_service.list_transactions(account_id)

            return [
                TransactionResponse(
                    transaction_id=t.id,
                    transaction_type=t.type.value,
                    amount=float(t.amount.amount),
                    currency=t.amount.currency.value,  # .value
                    status=t.status.value,
                    created_at=t.created_at,           # datetime, no str
                )
                for t in transactions
            ]
        except Exception as e:
            raise DomainError(f"Error listing transactions: {str(e)}")