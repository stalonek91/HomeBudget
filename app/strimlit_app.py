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

 

    st.sidebar.title('Navigation')
    selection = st.sidebar.radio("Go to", ['Summary', "Transactions", "Pornosy",], index=0)
    st.image('/Users/sylwestersojka/Documents/HomeBudget/app/belka.png')

    if selection == 'Summary':

        summary_tab, vienna_tab, nokia_tab, generali_tab, revolut_tab, etoro_tab, obligacje_tab, xtb_tab = st.tabs(
            ["Summary", "ViennaLife", "Nokia", "Generali", "Revolut", "Etoro", "Obligacje", "XTB"]
        )

        with summary_tab:
            render_summary_section()
        
        with vienna_tab:
            tab = st.session_state['tab'] = 'ViennaLife'
            generate_wallet_tab(tab)

        with nokia_tab:
            tab = st.session_state['tab'] = 'Nokia'
            generate_wallet_tab(tab)

        with generali_tab:
            tab = st.session_state['tab'] = 'Generali'
            generate_wallet_tab(tab)

        with revolut_tab:
            tab = st.session_state['tab'] = 'Revolut'
            generate_wallet_tab(tab)

        with etoro_tab:
            tab = st.session_state['tab'] = 'Etoro'
            generate_wallet_tab(tab)

        with obligacje_tab:
            tab = st.session_state['tab'] = 'Obligacje'
            generate_wallet_tab(tab)

        with xtb_tab:
            tab = st.session_state['tab'] = 'XTB'
            generate_wallet_tab(tab)


        
 

    elif selection == "Pornosy":

        tab1, tab2, tab3 = st.tabs(["Lorem Ipsum xd", "Wazne", "Sojka Sylwester Portfolio Project CV"])

        with tab1:
            # Sample data
            data = {
                'date': pd.date_range(start='2021-05-01', periods=7, freq='M'),
                'value': [3000, 4500, 4000, 5000, 5500, 4800, 7000]
            }
            df = pd.DataFrame(data)

            # Create a Plotly figure
            fig = go.Figure()

            # Add a trace for the area chart
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['value'],
                mode='lines+markers',
                line=dict(color='green', width=4),
                fill='tozeroy',  # fill area to xaxis
                fillcolor='rgba(0,255,0,0.1)',  # Set the fill color with transparency
                marker=dict(size=8)  # Marker size
            ))

            # Customize the layout
            fig.update_layout(
                title='Sample Area Chart with Line',
                xaxis_title='Date',
                yaxis_title='Value',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                plot_bgcolor='white'  # Set background color to white
            )

            # Display the plot in Streamlit
            st.plotly_chart(fig)


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