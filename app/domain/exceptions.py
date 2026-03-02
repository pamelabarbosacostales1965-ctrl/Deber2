class DomainError(Exception):
    """Error base del dominio."""


class InvalidTransaction(DomainError):
    pass


class InsufficientFundsError(DomainError):
    pass


class AccountFrozen(DomainError):
    pass


class FraudDetected(DomainError):
    pass
