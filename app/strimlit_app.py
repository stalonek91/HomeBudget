import streamlit as st
import requests
import pandas as pd
import numpy as np

import plotly.graph_objects as go
import time

from io import StringIO
from streamlit_summary_section import render_summary_section
from streamlit_transaction_section import render_transaction_section
from streamlit_wallets import *

import datetime


st.set_page_config(layout="wide")

        

def main():

 

    st.sidebar.title('Navigation')
    selection = st.sidebar.radio("Go to", ['Summary', "Transactions", "Pornosy",], index=0)


    if selection == 'Summary':

        summary_tab, vienna_tab, nokia_tab, generali_tab, revolut_tab, etoro_tab, obligacje_tab, xtb_tab = st.tabs(
            ["Summary", "ViennaLife", "Nokia", "Generali", "Revolut", "Etoro", "Obligacje", "XTB"]
        )

        with summary_tab:
            render_summary_section()
        
        with vienna_tab:

            
            

            print(f'VIENNA SECTION TAB')
            st.session_state['tab'] = 'ViennaLife'
            st.write(f"{st.session_state['tab']}")


            vienna_wallet = fetch_wallet_totals(st.session_state['tab'])
            print(f'Vienna_wallet DF type is: {type(vienna_wallet)} with values: {vienna_wallet}')

            
            
            # generate_wallet_chart(vienna_wallet, get_time_delta(st.session_state['tab']))
            generate_wallet_chart_2nd_with_legend(vienna_wallet)

            st.write('Add Vienna entry:')

            col1, col2, col3, col4, col5 = st.columns(5, vertical_alignment="bottom")

            with col1:
                v_date = st.date_input("Date of entry")
                f_date = v_date.strftime('%Y-%m-%d')

            with col2:
                initial_amount = float(st.number_input("Pre deposit amount:", step=100))

            with col3:
                deposit_amount = float(st.number_input("Deposit amount:",step=100))
            
            with col4:
                total_amount = float(st.number_input("Total now:",step=100))

            with col5:
                button_clicked = st.button("Add Vienna to DB")



            if button_clicked:
                print(f'BUTTON_vienna KLIKNIETY')

                data = {
                        "date": f_date,
                        "initial_amount": initial_amount,
                        "deposit_amount": deposit_amount,
                        "total_amount": total_amount
                }

                add_transcation(tab=st.session_state['tab'], data=data)
                st.write(f'Following data will be send to DB: {data}')
                st.rerun()
            
            st.dataframe(vienna_wallet)

        with nokia_tab:
            st.session_state['tab'] = 'Nokia'
            st.write(f"{st.session_state['tab']}")

            nokia_wallet = fetch_wallet_totals(st.session_state['tab'])
            st.dataframe(nokia_wallet)

        with generali_tab:
            st.session_state['tab'] = 'Generali'
            st.write(f"{st.session_state['tab']}")

            generali_wallet = fetch_wallet_totals(st.session_state['tab'])
            st.dataframe(generali_wallet)

        with revolut_tab:
            st.session_state['tab'] = 'Revolut'
            st.write(f"{st.session_state['tab']}")

            revolut_wallet = fetch_wallet_totals(st.session_state['tab'])
            st.dataframe(revolut_wallet)

        with etoro_tab:
            st.session_state['tab'] = 'Etoro'
            st.write(f"{st.session_state['tab']}")

            etoro_wallet = fetch_wallet_totals(st.session_state['tab'])
            st.dataframe(etoro_wallet)

        with obligacje_tab:
            st.session_state['tab'] = 'Obligacje'
            st.write(f"{st.session_state['tab']}")

            obligacje_wallet = fetch_wallet_totals(st.session_state['tab'])
            st.dataframe(obligacje_wallet)

        with xtb_tab:
            st.session_state['tab'] = 'XTB'
            st.write(f"{st.session_state['tab']}")

            xtb_wallet = fetch_wallet_totals(st.session_state['tab'])
            st.dataframe(xtb_wallet)


        
 

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