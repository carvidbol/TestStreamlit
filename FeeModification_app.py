import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
import json

def get_liquidation_address_id(customer_id, address_to_find, api_key):
    url = f"https://api.bridge.xyz/v0/customers/{customer_id}/liquidation_addresses"
    headers = {
        "accept": "application/json",
        "Api-Key": api_key
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error al hacer la petición: {response.status_code}")
        print(response.text)
        return None

    data = response.json()
    for item in data.get("data", []):
        if item["address"].lower() == address_to_find.lower():
            return item["id"]
    
    print(f"No se encontró ningún ID para la address {address_to_find}")
    return None


# --- Layout con imagen y título ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("UNITY FINANCIAL SERVICES")
with col2:
    try:
        st.image("Logo.png", use_container_width=True)
    except:
        st.warning("No se encontró la imagen 'Logo.png'")

st.markdown("### Developer fee")

# --- Entradas del formulario ---
customer_id = st.text_input("Customer ID") #UUID
liq_address = st.text_input("Wallet/Liquidation address") #Liquidation address
fee_val = st.text_input("Developer Fee") #Fee as percentage 
api_key = st.text_input("API Key", type="password") #API Key

# --- Ejecutar ---
if st.button("Update developer fee"):
    if not all([customer_id, liq_address, fee_val, api_key]):
        st.error("There are empty fields")
    else:
        liq_address_ID = get_liquidation_address_id(customer_id, liq_address, api_key)
        url = f"https://api.bridge.xyz/v0/customers/{customer_id}/liquidation_addresses/{liq_address_ID}"
        payload = {"custom_developer_fee_percent": fee_val}
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Api-Key": api_key
        }

        try:
            response = requests.put(url, json=payload, headers=headers)
            response_text = response.text
            status = response.status_code

            st.subheader("Respuesta de la API")
            st.code(response_text)

            # --- Guardar registro en CSV ---
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "customer_id": customer_id,
                "liq_address": liq_address,
                "fee_val": fee_val,
                "status_code": status,
                "response": response_text
            }

            csv_file = "registro_fees.csv"
            df_log = pd.DataFrame([log_entry])
            if os.path.isfile(csv_file):
                df_log.to_csv(csv_file, mode='a', header=False, index=False)
            else:
                df_log.to_csv(csv_file, index=False)

            st.success("Developer fee actualizado y registro guardado.")
        except Exception as e:
            st.error(f"Error inesperado: {e}")
