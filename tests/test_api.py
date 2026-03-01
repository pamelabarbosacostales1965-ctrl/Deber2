import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_customer_and_account():
    # Crear cliente
    response = client.post(
        "/customers",
        json={"name": "Alice", "email": "alice@test.com"},
    )
    assert response.status_code == 200
    customer_id = response.json()["customer_id"]

    # Crear cuenta
    response = client.post(
        "/accounts",
        json={"customer_id": customer_id, "currency": "USD"},
    )
    assert response.status_code == 200
    account_id = response.json()["account_id"]

    return account_id


def test_deposit_happy_path():
    account_id = create_customer_and_account()

    response = client.post(
        "/transactions/deposit",
        json={"account_id": account_id, "amount": 100},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"
    assert response.json()["new_balance"] == 100.0


def test_transfer_happy_path():
    # Crear dos cuentas
    acc1 = create_customer_and_account()
    acc2 = create_customer_and_account()

    # Depositar en primera
    client.post(
        "/transactions/deposit",
        json={"account_id": acc1, "amount": 200},
    )

    # Transferir
    response = client.post(
        "/transactions/transfer",
        json={
            "from_account_id": acc1,
            "to_account_id": acc2,
            "amount": 50,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"


def test_insufficient_funds():
    account_id = create_customer_and_account()

    response = client.post(
        "/transactions/withdraw",
        json={"account_id": account_id, "amount": 500},
    )

    assert response.status_code == 400
    assert "Insufficient" in response.json()["detail"]


def test_risk_rejection():
    account_id = create_customer_and_account()

    # Si max_amount en strategy es 10000
    response = client.post(
        "/transactions/deposit",
        json={"account_id": account_id, "amount": 50000},
    )

    assert response.status_code == 400


def test_get_account_details():
    account_id = create_customer_and_account()

    response = client.get(f"/accounts/{account_id}")

    assert response.status_code == 200
    assert response.json()["account_id"] == account_id