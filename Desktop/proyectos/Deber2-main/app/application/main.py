from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import uuid

app = FastAPI(
    title="Fintech Mini Bank API",
    description="API del banco fintech",
    version="1.0.0"
)

# Base de datos temporal (diccionario en memoria)
customers: Dict[str, dict] = {}
accounts: Dict[str, dict] = {}
transactions: Dict[str, dict] = {}

# MODELOS
class CreateCustomerRequest(BaseModel):
    name: str
    email: str


class CreateAccountRequest(BaseModel):
    
    customer_id: str
    currency: str = "USD"

class DepositRequest(BaseModel):
    account_id: str
    amount: float


class WithdrawRequest(BaseModel):
    account_id: str
    amount: float


class TransferRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float
    
# ENDPOINTS

@app.get("/")
def health_check():
    return {"status": "API funcionando correctamente"}


# Crear cliente
@app.post("/customers")
def create_customer(request: CreateCustomerRequest):

    customer_id = str(uuid.uuid4())

    customer = {
        "id": customer_id,
        "name": request.name,
        "email": request.email,
        "status": "ACTIVE"
    }

    customers[customer_id] = customer

    return customer


# Crear cuenta
@app.post("/accounts")
def create_account(request: CreateAccountRequest):



    if request.customer_id not in customers:
        raise HTTPException(status_code=404, detail="Customer no existe")

    account_id = str(uuid.uuid4())

    account = {
        "id": account_id,
        "customer_id": request.customer_id,
        "currency": request.currency,
        "balance": 0,
        "status": "ACTIVE"
    }

    accounts[account_id] = account

    return account


# Obtener cuenta

@app.get("/accounts/{account_id}")
def get_account(account_id: str):

    if account_id not in accounts:
        raise HTTPException(status_code=404, detail="Cuenta no existe")

    return accounts[account_id]

#deposito

@app.post("/transactions/deposit")
def deposit(request: DepositRequest):

    if request.account_id not in accounts:
        raise HTTPException(status_code=404, detail="Cuenta no existe")

    account = accounts[request.account_id]

    account["balance"] += request.amount

    transaction_id = str(uuid.uuid4())

    transaction = {
        "id": transaction_id,
        "type": "DEPOSIT",
        "account_id": request.account_id,
        "amount": request.amount,
        "status": "APPROVED"
    }

    transactions[transaction_id] = transaction

    return transaction

#transacción/retiro

@app.post("/transactions/withdraw")
def withdraw(request: WithdrawRequest):

    if request.account_id not in accounts:
        raise HTTPException(status_code=404, detail="Cuenta no existe")

    account = accounts[request.account_id]

    if account["balance"] < request.amount:
        raise HTTPException(status_code=400, detail="Fondos insuficientes")

    account["balance"] -= request.amount

    transaction_id = str(uuid.uuid4())

    transaction = {
        "id": transaction_id,
        "type": "WITHDRAW",
        "account_id": request.account_id,
        "amount": request.amount,
        "status": "APPROVED"
    }

    transactions[transaction_id] = transaction

    return transaction

#transferencia

@app.post("/transactions/transfer")
def transfer(request: TransferRequest):

    if request.from_account_id not in accounts:
        raise HTTPException(status_code=404, detail="Cuenta origen no existe")

    if request.to_account_id not in accounts:
        raise HTTPException(status_code=404, detail="Cuenta destino no existe")

    from_account = accounts[request.from_account_id]
    to_account = accounts[request.to_account_id]

    if from_account["balance"] < request.amount:
        raise HTTPException(status_code=400, detail="Fondos insuficientes")

    from_account["balance"] -= request.amount
    to_account["balance"] += request.amount

    transaction_id = str(uuid.uuid4())

    transaction = {
        "id": transaction_id,
        "type": "TRANSFER",
        "from": request.from_account_id,
        "to": request.to_account_id,
        "amount": request.amount,
        "status": "APPROVED"
    }

    transactions[transaction_id] = transaction

    return transaction

#obtener salud

@app.get("/health")
def health():
    return {"message": "OK"}