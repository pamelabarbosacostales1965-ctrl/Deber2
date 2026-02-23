# builder para construir transacciones como cadena

from app.domain.entities import Transaction
from app.domain.enums import TransactionType, TransactionStatus, CurrencyType
from app.domain.value_objects import Money, AccountId
from app.domain.exceptions import InvalidTransaction
from decimal import Decimal
import uuid


class TransactionBuilder:
    # builder para construir transacciones
    
    def __init__(self):
        # inicializar builder con valores None
        self._type = None
        self._amount = None
        self._currency = None
        self._from_account_id = None
        self._to_account_id = None
    
    def with_type(self, transaction_type: TransactionType) -> 'TransactionBuilder':
        # establecer tipo de transaccion
        self._type = transaction_type
        return self
    
    def with_amount(self, amount: Decimal) -> 'TransactionBuilder':
        # establecer monto
        self._amount = amount
        return self
    
    def with_currency(self, currency: CurrencyType) -> 'TransactionBuilder':
        # establecer moneda
        self._currency = currency
        return self
    
    def with_from_account(self, account_id: AccountId) -> 'TransactionBuilder':
        # establecer cuenta origen
        self._from_account_id = account_id
        return self
    
    def with_to_account(self, account_id: AccountId) -> 'TransactionBuilder':
        # establecer cuenta destino
        self._to_account_id = account_id
        return self
    
    def build(self) -> Transaction:
        # construir y retornar transaccion validada
        
        # validar que todos los campos requeridos esten presentes
        if not self._type or not self._amount or not self._currency:
            raise InvalidTransaction("Missing required fields: type, amount, currency")
        
        # validar que el tipo coincida con las cuentas (TRANSFER necesita ambas)
        if self._type == TransactionType.TRANSFER:
            if not self._from_account_id or not self._to_account_id:
                raise InvalidTransaction("TRANSFER requires from_account_id and to_account_id")
            
            if self._from_account_id == self._to_account_id:
                raise InvalidTransaction("Cannot transfer to same account")
        
        # validar amount > 0
        if self._amount <= Decimal("0.00"):
            raise InvalidTransaction("Amount must be positive")
        
        # crear Money
        money = Money(amount=self._amount, currency=self._currency)
        
        # retornar Transaction con status PENDING
        return Transaction(
            id=str(uuid.uuid4()),
            type=self._type,
            amount=money,
            currency=self._currency,
            status=TransactionStatus.PENDING,
            from_account_id=self._from_account_id,
            to_account_id=self._to_account_id
        )