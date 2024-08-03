import streamlit as st
import requests
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go


FASTAPI_URL = 'http://127.0.0.1:8000'
wallet_endpoints = {

    "ViennaLife": "/vienna/get_all_vienna",
    "Nokia": "/nokia/get_all_nokia",
    "Generali": "/generali/get_all_generali",
    "Revolut": "/revolut/get_all_revolut",
    "Etoro": "/transactions/get_all_etoro",
    "Obligacje": "/obligacje/get_all_obligacje",
    "XTB" : "/xtb/get_all_xtb"

}

def fetch_wallet_totals(tab):

    endpoint = wallet_endpoints[tab]

    response = requests.get(f"{FASTAPI_URL}{endpoint}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return []
    
def generate_wallet_chart(df):
    pass



