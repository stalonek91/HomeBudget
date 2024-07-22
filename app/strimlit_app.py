import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

FASTAPI_URL = 'http://127.0.0.1:8000'

def fetch_portfolio_summary():
    response = requests.get(f"{FASTAPI_URL}/portfolio/get_all_portfolio")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return []
    
def get_portfolio_perc():
    response = requests.get(f"{FASTAPI_URL}/portfolio/calculate_perc/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch response data: {response.status_code}")
        return []

def main():
    st.title("Portfolio :blue[Summary] 🤫🤫🤫🤫🤫🤫")

    portfolio_summary = fetch_portfolio_summary()
    portfolio_percentage = get_portfolio_perc()

    if portfolio_summary:
        df = pd.DataFrame(portfolio_summary)
        st.dataframe(df)
    else:
        st.warning("No data to display")

    if portfolio_percentage:
        fig, ax = plt.subplots(figsize=(6,3), subplot_kw=dict(aspect="equal"))
        df_perc = pd.DataFrame(portfolio_percentage)
        st.write(df_perc)

        fig, ax = plt.subplots()
        ax.pie(df_perc['Percentage'], labels=df_perc['Wallet'], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)




if __name__ == "__main__":
    main()