from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import re
from .enums import CurrencyType
from .exceptions import DomainError


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class CustomerId:
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise DomainError("CustomerId vacío")


@dataclass(frozen=True)
class AccountId:
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise DomainError("AccountId vacío")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        v = (self.value or "").strip().lower()
        if not _EMAIL_RE.match(v):
            raise DomainError("Email inválido")
        object.__setattr__(self, "value", v)


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: CurrencyType

    def __post_init__(self):
        if self.amount is None:
            raise DomainError("Money.amount es None")
        if not isinstance(self.amount, Decimal):
            raise DomainError("Money.amount debe ser Decimal")

        # normalizar a 2 decimales
        normalized = self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if normalized < Decimal("0.00"):
            raise DomainError("Money.amount no puede ser negativo")

        object.__setattr__(self, "amount", normalized)

    def add(self, other: "Money") -> "Money":
        self._check_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def sub(self, other: "Money") -> "Money":
        self._check_currency(other)
        if self.amount < other.amount:
            raise DomainError("Resultado negativo en Money.sub()")
        return Money(self.amount - other.amount, self.currency)

    def _check_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise DomainError("Monedas distintas")
