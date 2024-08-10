import streamlit as st
import requests
import pandas as pd
import numpy as np

import plotly.graph_objects as go
import time

from io import StringIO
from streamlit_summary_section import render_summary_section, delete_portfolio
from streamlit_transaction_section import render_transaction_section
from streamlit_wallets import *

import datetime




st.set_page_config(layout="wide")

        

def main():
    
    def Summary():
        
        render_summary_section()

    def Transactions():
        
        render_transaction_section()

    def ViennaLife():
        
        generate_wallet_tab('ViennaLife')

    def Nokia():
        
        generate_wallet_tab('Nokia')

    def Generali():
        
        generate_wallet_tab('Generali')

    def Revolut():
        
        generate_wallet_tab('Revolut')

    def Etoro():
        
        generate_wallet_tab('Etoro')

    def Obligacje():
        
        generate_wallet_tab('Obligacje')

    def XTB():
        
        generate_wallet_tab('XTB')

# Updated navigation section
    pg = st.navigation({
        "Portfolio": [st.Page(Summary), st.Page(Transactions)],
        "Wallets": [
            st.Page(ViennaLife),
            st.Page(Nokia),
            st.Page(Generali),
            st.Page(Revolut),
            st.Page(Etoro),
            st.Page(Obligacje),
            st.Page(XTB)
        ]
    })
    pg.run()

 

    # st.sidebar.title('Navigation')
    # selection = st.sidebar.radio("Go to", ["Summary", "ViennaLife", "Nokia", "Generali", "Revolut", "Etoro", "Obligacje", "XTB", "Transactions"], index=0)
    

    


       

if __name__ == "__main__":
    main()