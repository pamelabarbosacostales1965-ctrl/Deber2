# tests para factory, builder, facade y dtos

import pytest
from decimal import Decimal
from app.patterns.transaction_factory import TransactionFactory
from app.patterns.transaction_builder import TransactionBuilder
from app.application.dtos import (
    CreateCustomerRequest, DepositRequest, TransferRequest
)
from app.domain.enums import TransactionType, TransactionStatus, CurrencyType
from app.domain.value_objects import Money, AccountId
from app.domain.exceptions import InvalidTransaction

# tests para factory
class TestTransactionFactory:
    
    def test_create_valid_transaction(self):
        # factory crea transaccion valida
        transaction = TransactionFactory.create(
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("100.00"),
            currency=CurrencyType.USD
        )
        
        assert transaction is not None
        assert transaction.type == TransactionType.DEPOSIT
        assert transaction.amount.amount == Decimal("100.00")
        assert transaction.status == TransactionStatus.PENDING
    
    def test_create_negative_amount(self):
        # factory rechaza monto negativo
        with pytest.raises(InvalidTransaction):
            TransactionFactory.create(
                transaction_type=TransactionType.DEPOSIT,
                amount=Decimal("-50.00"),
                currency=CurrencyType.USD
            )


# tests para builder
class TestTransactionBuilder:
    
    def test_build_complete_transaction(self):
        # builder construye transaccion con todos los campos
        from_account = AccountId("account-1")
        to_account = AccountId("account-2")
        
        transaction = (TransactionBuilder()
            .with_type(TransactionType.TRANSFER)
            .with_amount(Decimal("100.00"))
            .with_currency(CurrencyType.USD)
            .with_from_account(from_account)
            .with_to_account(to_account)
            .build()
        )
        
        assert transaction is not None
        assert transaction.type == TransactionType.TRANSFER
        assert transaction.amount.amount == Decimal("100.00")
        assert transaction.from_account_id == from_account
        assert transaction.to_account_id == to_account
        assert transaction.status == TransactionStatus.PENDING
    
    def test_build_missing_fields(self):
        # builder lanza excepcion sin campos requeridos
        with pytest.raises(InvalidTransaction):
            TransactionBuilder().build()


# tests para validacion de dtos
class TestDTOs:
    
    def test_create_customer_request_valid(self):
        # dto valida datos correctos
        request = CreateCustomerRequest(
            name="Ana Naranjo",
            email="ana@usfq.com"
        )
        
        assert request.name == "Ana Naranjo"
        assert request.email == "ana@usfq.com"
    
    def test_transfer_request_positive_amount(self):
        # dto rechaza monto negativo
        with pytest.raises(ValueError):
            TransferRequest(
                from_account_id="account-1",
                to_account_id="account-2",
                amount=-300.00,
                currency="USD"
            )