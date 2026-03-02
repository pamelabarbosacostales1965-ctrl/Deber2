import streamlit as st
import requests
import os
API_URL = os.getenv("API_URL", "http://api:8000")

st.title("Transacciones")

st.header("Depositar")

account_id = st.text_input("Account ID")
amount = st.number_input("Monto", min_value=0.0)

if st.button("Depositar"):

    response = requests.post(
        f"{API_URL}/transactions/deposit",
        json={
            "account_id": account_id,
            "amount": amount
        }
    )

    if response.status_code == 200:
        st.success("Depósito exitoso")
        st.json(response.json())
    else:
        st.error("Error en depósito")


st.header("Retirar")

account_id_w = st.text_input("Account ID retiro")
amount_w = st.number_input("Monto retiro", min_value=0.0)

if st.button("Retirar"):

    response = requests.post(
        f"{API_URL}/transactions/withdraw",
        json={
            "account_id": account_id_w,
            "amount": amount_w
        }
    )

    if response.status_code == 200:
        st.success("Retiro exitoso")
        st.json(response.json())
    else:
        st.error("Error en retiro")

st.header("Transferir")

from_account = st.text_input("Cuenta origen")
to_account = st.text_input("Cuenta destino")
amount_t = st.number_input("Monto transferencia", min_value=0.0, key="transfer")

if st.button("Transferir"):

    response = requests.post(
        f"{API_URL}/transactions/transfer",
        json={
            "from_account_id": from_account,
            "to_account_id": to_account,
            "amount": amount_t
        }
    )

    if response.status_code == 200:
        st.success("Transferencia exitosa")
        st.json(response.json())
    else:
        st.error("Error en transferencia")        