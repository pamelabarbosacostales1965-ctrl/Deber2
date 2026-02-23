# tests para factory, builder, facade y dto's

import pytest
from app.patterns.transaction_factory import TransactionFactory
from app.patterns.transaction_builder import TransactionBuilder
from app.application.dtos import (
    CreateCustomerRequest, DepositRequest, TransferRequest
)
from app.domain.enums import TransactionType, TransactionStatus
from app.domain.value_objects import Money
from app.domain.exceptions import InvalidTransactionError


class TestTransactionFactory:
    # tests para factory
    
    def test_create_valid_transaction(self):
        # factory crea transaccion valida
        pass
    
    def test_create_negative_amount(self):
        # factory rechaza monto negativo
        pass


class TestTransactionBuilder:
    # tests para builder
    
    def test_build_complete_transaction(self):
        # builder construye transaccion con todos los campos
        pass
    
    def test_build_missing_fields(self):
        # builder lanza excepcion sin campos requeridos
        pass


class TestDTOs:
    # tests para validacion de dto's
    
    def test_create_customer_request_valid(self):
        # dto valida datos correctos
        pass
    
    def test_transfer_request_positive_amount(self):
        # dto rechaza monto negativo
        pass