import streamlit as st
import requests
import pandas as pd
import numpy as np
import time

from io import StringIO
from streamlit_summary_section import render_summary_section
from streamlit_transaction_section import render_transaction_section

st.set_page_config(layout="wide")

        

def main():

    

    st.sidebar.title('Navigation')
    selection = st.sidebar.radio("Go to", ['Summary', "Transactions", "Pornosy",], index=0)


    if selection == 'Summary':
        render_summary_section()
 

    elif selection == "Pornosy":

        tab1, tab2, tab3 = st.tabs(["Lorem Ipsum xd", "Wazne", "Sojka Sylwester Portfolio Project CV"])

        with tab1:
            st.title("Jan Router 3")
            st.image('/Users/sylwestersojka/Documents/HomeBudget/app/papaj3.png')

        with tab2:
            st.title('Powazna Strona.')

            if 'trigger_sleep' not in st.session_state:
                st.session_state['trigger_sleep'] = False

            if st.button("Don't click"):
                st.session_state['trigger_sleep'] = True

            if st.session_state['trigger_sleep']:
                with st.spinner('Warto czekac ...'):
                    time.sleep(5)
                
                st.success('Jednak nie warto 😅 Ale nastepna juz na powaznie serio.')
                st.image('/Users/sylwestersojka/Documents/HomeBudget/app/papaj2.png')

        with tab3:
            st.warning('You have been pranked!!!',icon="⚠️")
            st.image('/Users/sylwestersojka/Documents/HomeBudget/app/prenk.png')

    elif selection == "Transactions": 
        render_transaction_section()
       

if __name__ == "__main__":
    main()