import streamlit as st
import requests
import pandas as pd

FASTAPI_URL = 'http://127.0.0.1:8000'

def fetch_portfolio_summary():
    response = requests.get(f"{FASTAPI_URL}/portfolio/get_all_portfolio")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return []

def main():
    st.title("Portfolio Summary")

    portfolio_summary = fetch_portfolio_summary()

    if portfolio_summary:
        df = pd.DataFrame(portfolio_summary)
        st.dataframe(df)
    else:
        st.warning("No data to display")

if __name__ == "__main__":
    main()