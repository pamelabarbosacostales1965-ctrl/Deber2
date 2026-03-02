import streamlit as st
import requests
import os
API_URL = os.getenv("API_URL", "http://api:8000")

st.title("Fintech Mini Bank")

st.write("Bienvenido al sistema bancario fintech")

# Health check
try:
    response = requests.get(f"{API_URL}/health")
    if response.status_code == 200:
        st.success("API conectada correctamente")
    else:
        st.error("API no responde correctamente")
except:
    st.error("No se puede conectar a la API")