# facade para orquestar servicios

from typing import List, Optional
from app.application.dtos import (
    CreateCustomerRequest, CreateCustomerResponse,
    CreateAccountRequest, CreateAccountResponse,
    DepositRequest, DepositResponse,
    WithdrawRequest, WithdrawResponse,
    TransferRequest, TransferResponse,
    AccountDetailResponse, TransactionResponse
)
from app.domain.exceptions import DomainError


class BankingFacade:
    # facade que orquesta toda la logica del banco
    # es el unico entry point para la API
    
    def __init__(
        self,
        customer_service,
        account_service,
        transaction_service,
        fee_strategy,
        risk_strategy
    ):
        # inyectar dependencias
        self.customer_service = customer_service
        self.account_service = account_service
        self.transaction_service = transaction_service
        self.fee_strategy = fee_strategy
        self.risk_strategy = risk_strategy
    
    def create_customer(self, request: CreateCustomerRequest) -> CreateCustomerResponse:
        # crear nuevo cliente
        try:
            customer = self.customer_service.create_customer(
                name=request.name,
                email=request.email
            )
            return CreateCustomerResponse(
                customer_id=str(customer.id),
                name=customer.name,
                email=customer.email,
                created_at=str(customer.created_at) if hasattr(customer, 'created_at') else ""
            )
        except Exception as e:
            raise DomainError(f"Error creating customer: {str(e)}")
    
    def create_account(self, request: CreateAccountRequest) -> CreateAccountResponse:
        # crear nueva cuenta
        try:
            account = self.account_service.create_account(
                customer_id=request.customer_id,
                currency=request.currency
            )
            return CreateAccountResponse(
                account_id=str(account.id),
                customer_id=str(account.customer_id),
                balance=float(account.balance.amount),
                currency=account.balance.currency,
                status=account.status.value
            )
        except Exception as e:
            raise DomainError(f"Error creating account: {str(e)}")
    
    def deposit(self, request: DepositRequest) -> DepositResponse:
        # realizar deposito
        try:
            # validar riesgo
            self.risk_strategy.validate(request.amount)
            
            # depositar
            transaction = self.transaction_service.deposit(
                account_id=request.account_id,
                amount=request.amount
            )
            
            # calcular comision
            fee = self.fee_strategy.calculate_fee(request.amount)
            
            # obtener saldo actualizado
            account = self.account_service.get_account(request.account_id)
            
            return DepositResponse(
                transaction_id=str(transaction.id),
                account_id=str(account.id),
                new_balance=float(account.balance.amount),
                status=transaction.status.value,
                fee_applied=fee
            )
        except Exception as e:
            raise DomainError(f"Error in deposit: {str(e)}")
    
    def withdraw(self, request: WithdrawRequest) -> WithdrawResponse:
        # realizar retiro
        try:
            # obtener cuenta
            account = self.account_service.get_account(request.account_id)
            
            # validar saldo suficiente
            if float(account.balance.amount) < request.amount:
                raise DomainError("Insufficient funds")
            
            # validar riesgo
            self.risk_strategy.validate(request.amount)
            
            # retirar
            transaction = self.transaction_service.withdraw(
                account_id=request.account_id,
                amount=request.amount
            )
            
            # calcular comision
            fee = self.fee_strategy.calculate_fee(request.amount)
            
            # obtener saldo actualizado
            account = self.account_service.get_account(request.account_id)
            
            return WithdrawResponse(
                transaction_id=str(transaction.id),
                account_id=str(account.id),
                new_balance=float(account.balance.amount),
                status=transaction.status.value,
                fee_applied=fee
            )
        except Exception as e:
            raise DomainError(f"Error in withdraw: {str(e)}")
    
    def transfer(self, request: TransferRequest) -> TransferResponse:
        # realizar transferencia
        try:
            # obtener cuentas
            from_account = self.account_service.get_account(request.from_account_id)
            to_account = self.account_service.get_account(request.to_account_id)
            
            # validar saldo suficiente
            if float(from_account.balance.amount) < request.amount:
                raise DomainError("Insufficient funds")
            
            # validar riesgo
            self.risk_strategy.validate(request.amount)
            
            # transferir
            transaction = self.transaction_service.transfer(
                from_account_id=request.from_account_id,
                to_account_id=request.to_account_id,
                amount=request.amount
            )
            
            # calcular comision
            fee = self.fee_strategy.calculate_fee(request.amount)
            
            return TransferResponse(
                transaction_id=str(transaction.id),
                from_account_id=str(from_account.id),
                to_account_id=str(to_account.id),
                amount=request.amount,
                status=transaction.status.value,
                fee_applied=fee
            )
        except Exception as e:
            raise DomainError(f"Error in transfer: {str(e)}")
    
    def get_account(self, account_id: str) -> AccountDetailResponse:
        # obtener detalles de una cuenta
        try:
            account = self.account_service.get_account(account_id)
            transactions = self.transaction_service.list_transactions(account_id)
            
            transaction_responses = [
                TransactionResponse(
                    transaction_id=str(t.id),
                    transaction_type=t.type.value,
                    amount=float(t.amount.amount),
                    currency=t.amount.currency,
                    status=t.status.value,
                    created_at=str(t.created_at)
                )
                for t in transactions
            ]
            
            return AccountDetailResponse(
                account_id=str(account.id),
                customer_id=str(account.customer_id),
                balance=float(account.balance.amount),
                currency=account.balance.currency,
                status=account.status.value,
                created_at=str(account.created_at) if hasattr(account, 'created_at') else "",
                transactions=transaction_responses
            )
        except Exception as e:
            raise DomainError(f"Error getting account: {str(e)}")
    
    def list_transactions(self, account_id: str) -> List[TransactionResponse]:
        # listar transacciones de una cuenta
        try:
            transactions = self.transaction_service.list_transactions(account_id)
            
            return [
                TransactionResponse(
                    transaction_id=str(t.id),
                    transaction_type=t.type.value,
                    amount=float(t.amount.amount),
                    currency=t.amount.currency,
                    status=t.status.value,
                    created_at=str(t.created_at)
                )
                for t in transactions
            ]
        except Exception as e:
            raise DomainError(f"Error listing transactions: {str(e)}")