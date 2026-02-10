class DomainError(Exception):
    """Error base de capa de dominio"""

class NotFoundError(DomainError):
    pass

class ValidationError(DomainError):
    pass

class InvalidStatusTransition(DomainError):
    pass