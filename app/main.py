from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.repositories.database import get_session
from app.repositories.sqlalchemy_impl import (
    SQLAlchemyCustomerRepository,
    SQLAlchemyAccountRepository,
    SQLAlchemyTransactionRepository,
)

from app.services.customer_service import CustomerService
from app.services.account_service import AccountService
from app.services.transaction_service import TransactionService

from app.patterns.fee_strategy import PercentFee
from app.patterns.risk_strategy import BasicRiskStrategy

from app.application.facade import BankingFacade
from app.application.dtos import (
    CreateCustomerRequest,
    CreateAccountRequest,
    DepositRequest,
    WithdrawRequest,
    TransferRequest,
)

from app.domain.exceptions import DomainError


app = FastAPI(
    title="Fintech Mini Bank API",
    version="1.0.0"
)

from app.repositories.database import engine, Base
Base.metadata.create_all(bind=engine)

# Dependency: build facade per request
def get_facade(session: Session = Depends(get_session)) -> BankingFacade:
    # repositories
    customer_repo = SQLAlchemyCustomerRepository(session)
    account_repo = SQLAlchemyAccountRepository(session)
    transaction_repo = SQLAlchemyTransactionRepository(session)

    # services
    customer_service = CustomerService(customer_repo)
    account_service = AccountService(account_repo, customer_repo)
    transaction_service = TransactionService(
        transaction_repo,
        account_repo
    )

    # strategies
    fee_strategy = PercentFee(percentage=0.01)
    risk_strategy = BasicRiskStrategy(max_amount=10000)

    # facade
    return BankingFacade(
        customer_service,
        account_service,
        transaction_service,
        fee_strategy,
        risk_strategy
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/customers")
def create_customer(
    request: CreateCustomerRequest,
    facade: BankingFacade = Depends(get_facade)
):
    try:
        return facade.create_customer(request)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts")
def create_account(
    request: CreateAccountRequest,
    facade: BankingFacade = Depends(get_facade)
):
    try:
        return facade.create_account(request)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/accounts/{account_id}")
def get_account(
    account_id: str,
    facade: BankingFacade = Depends(get_facade)
):
    try:
        return facade.get_account(account_id)
    except DomainError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/accounts/{account_id}/transactions")
def list_transactions(
    account_id: str,
    facade: BankingFacade = Depends(get_facade)
):
    try:
        return facade.list_transactions(account_id)
    except DomainError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/transactions/deposit")
def deposit(
    request: DepositRequest,
    facade: BankingFacade = Depends(get_facade)
):
    try:
        return facade.deposit(request)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/transactions/withdraw")
def withdraw(
    request: WithdrawRequest,
    facade: BankingFacade = Depends(get_facade)
):
    try:
        return facade.withdraw(request)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/transactions/transfer")
def transfer(
    request: TransferRequest,
    facade: BankingFacade = Depends(get_facade)
):
    try:
        return facade.transfer(request)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))