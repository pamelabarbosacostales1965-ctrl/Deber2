from __future__ import annotations

import uuid
from typing import List, Optional

from app.domain.entities import Customer
from app.domain.exceptions import DomainError
from app.domain.value_objects import CustomerId, Email
from app.repositories.interfaces import CustomerRepository


class CustomerService:
    def __init__(self, customer_repo: CustomerRepository) -> None:
        self._customers = customer_repo

    # ------------------------------------------------------------------
    # Use case: create customer
    # ------------------------------------------------------------------
    def create_customer(self, name: str, email: str) -> Customer:
        """
        Creates and persists a new customer.
        Raises DomainError if the email is already registered.
        """
        normalized_email = email.strip().lower()

        if self._customers.find_by_email(normalized_email) is not None:
            raise DomainError(f"Email ya registrado: {normalized_email}")

        customer = Customer(
            id=CustomerId(str(uuid.uuid4())),
            name=name.strip(),
            email=Email(normalized_email),
            status="ACTIVE",
        )
        return self._customers.save(customer)

    # ------------------------------------------------------------------
    # Use case: get customer
    # ------------------------------------------------------------------
    def get_customer(self, customer_id: str) -> Customer:
        customer = self._customers.find_by_id(CustomerId(customer_id))
        if customer is None:
            raise DomainError(f"Cliente no encontrado: {customer_id}")
        return customer

    # ------------------------------------------------------------------
    # Use case: list all customers
    # ------------------------------------------------------------------
    def list_customers(self) -> List[Customer]:
        return self._customers.list_all()

    # ------------------------------------------------------------------
    # Asistente interno utilizado por AccountService
    # ------------------------------------------------------------------
    def validate_email(self, email: str) -> bool:
        """Returns True if the email format is valid (delegates to VO)."""
        try:
            Email(email)
            return True
        except DomainError:
            return False