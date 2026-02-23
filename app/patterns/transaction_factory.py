# factory method para crear transacciones

from app.domain.entities import Transaction
from app.domain.enums import TransactionType, TransactionStatus, CurrencyType
from app.domain.value_objects import Money, AccountId
from app.domain.exceptions import InvalidTransaction
from decimal import Decimal


class TransactionFactory:
    # factory para crear transacciones validadas
    
    @staticmethod
    def create(
        transaction_type: TransactionType,
        amount: Decimal,
        currency: CurrencyType,
        from_account_id: AccountId = None,
        to_account_id: AccountId = None
    ) -> Transaction:
        # crea una nueva transaccion validada
        
        # validar amount > 0
        if amount <= Decimal("0.00"):
            raise InvalidTransaction("Amount must be positive")
        
        # validar transaction_type valido
        if transaction_type not in [TransactionType.DEPOSIT, TransactionType.WITHDRAW, TransactionType.TRANSFER]:
            raise InvalidTransaction("Invalid transaction type")
        
        # validar TRANSFER necesita ambas cuentas
        if transaction_type == TransactionType.TRANSFER:
            if not from_account_id or not to_account_id:
                raise InvalidTransaction("TRANSFER requires from_account_id and to_account_id")
            
            if from_account_id == to_account_id:
                raise InvalidTransaction("Cannot transfer to same account")
        
        # crear Money
        money = Money(amount=amount, currency=currency)
        
        # crear transaction
        transaction = Transaction(
            id=str(__import__('uuid').uuid4()),
            type=transaction_type,
            amount=money,
            currency=currency,
            status=TransactionStatus.PENDING,
            from_account_id=from_account_id,
            to_account_id=to_account_id
        )
        
        return transaction