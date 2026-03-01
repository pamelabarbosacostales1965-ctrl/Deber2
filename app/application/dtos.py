# data transfer objects (dto) con Pydantic

from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional
from datetime import datetime


# REQUEST OBJECTS
class CreateCustomerRequest(BaseModel):
    # request para crear cliente
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class CreateAccountRequest(BaseModel):
    # request para crear cuenta
    customer_id: str
    currency: str = "USD"


class DepositRequest(BaseModel):
    # request para deposito
    account_id: str
    amount: float = Field(..., gt=0)
    currency: str = "USD"


class WithdrawRequest(BaseModel):
    # request para retiro
    account_id: str
    amount: float = Field(..., gt=0)
    currency: str = "USD"


class TransferRequest(BaseModel):
    # request para transferencia
    from_account_id: str
    to_account_id: str
    amount: float = Field(..., gt=0)
    currency: str = "USD"


# RESPONSE OBJECTS
class CreateCustomerResponse(BaseModel):
    # response para crear cliente
    customer_id: str
    name: str
    email: str
    created_at: datetime


class CreateAccountResponse(BaseModel):
    # response para crear cuenta
    account_id: str
    customer_id: str
    balance: float
    currency: str
    status: str


class DepositResponse(BaseModel):
    # response para deposito
    transaction_id: str
    account_id: str
    new_balance: float
    status: str
    fee_applied: float = 0


class WithdrawResponse(BaseModel):
    # response para retiro
    transaction_id: str
    account_id: str
    new_balance: float
    status: str
    fee_applied: float = 0


class TransferResponse(BaseModel):
    # response para transferencia
    transaction_id: str
    from_account_id: str
    to_account_id: str
    amount: float
    status: str
    fee_applied: float = 0


class TransactionResponse(BaseModel):
    # response de una transaccion
    transaction_id: str
    transaction_type: str
    amount: float
    currency: str
    status: str
    created_at: datetime


class AccountDetailResponse(BaseModel):
    # response con detalles completos de cuenta
    account_id: str
    customer_id: str
    balance: float
    currency: str
    status: str
    created_at: datetime
    transactions: List[TransactionResponse]