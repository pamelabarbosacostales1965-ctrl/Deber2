import streamlit as st
import requests
import os
API_URL = os.getenv("API_URL", "http://api:8000")

st.title("Cuentas")

st.header("Crear Cliente")

name = st.text_input("Nombre")
email = st.text_input("Email")

if st.button("Crear Cliente"):

    response = requests.post(
        f"{API_URL}/customers",
        json={"name": name, "email": email}
    )

    if response.status_code == 200:
        st.success("Cliente creado")
        st.json(response.json())
    else:
        st.error("Error al crear cliente")


st.header("Crear Cuenta")

customer_id = st.text_input("Customer ID")

if st.button("Crear Cuenta"):

    response = requests.post(
        f"{API_URL}/accounts",
        json={"customer_id": customer_id}
    )

    if response.status_code == 200:
        st.success("Cuenta creada")
        st.json(response.json())
    else:
        st.error("Error al crear cuenta")
st.header("Ver Cuenta")

account_id_view = st.text_input("Account ID para ver")

if st.button("Ver Cuenta"):

    response = requests.get(f"{API_URL}/accounts/{account_id_view}")

    if response.status_code == 200:
        st.success("Cuenta encontrada")
        st.json(response.json())
    else:
        st.error("Cuenta no existe")