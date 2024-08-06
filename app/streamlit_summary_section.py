import streamlit as st
import requests
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go


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
    
def add_portfolio_entry():
    response = requests.post(f"{FASTAPI_URL}/portfolio/generate_summary")
    if response.status_code == 201:
        return response.json()
    else:
        st.error(f"Failed to fetch response data: {response.status_code}")
        return []
    
def delete_portfolio(date_obj):
    print(f'DEBUG: delete_portfolio endpoint function called')
    url = f"{FASTAPI_URL}/portfolio/delete_portfolio/{date_obj}"

    print(f'DELETE_TRANSACTION: Entry with date: {date_obj} will be removed')

    response = requests.delete(url=url)

    if response.status_code == 200:
        return 'Entry Deleted'
    else:
        st.error(f"Failed to process POST request: {response.status_code}")
        return []

    


def generate_summary_chart(df):
    fig = go.Figure()

    # Add a trace for the area chart
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['sum_of_acc'],
        mode='lines+markers',
        line=dict(color='#2E86C1', width=2),  # A pleasing blue color for the line
        fill='tozeroy',  # Fill area to x-axis
        fillcolor='rgba(46, 134, 193, 0.3)',  # Matching fill color with transparency
        marker=dict(size=6, color='#2E86C1')  # Smaller, matching markers
    ))

    # Customize the layout
    fig.update_layout(

        xaxis_title=dict(
            text='Date',
            font=dict(size=14, family='Arial, sans-serif', color='#FFFFFF'),
        ),
        yaxis_title=dict(
            text='Value',
            font=dict(size=14, family='Arial, sans-serif', color='#FFFFFF'),
        ),
        xaxis=dict(
            showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)',  # Light grid lines
            tickangle=-45,  # Rotate x-axis labels for better readability
            color='#FFFFFF',
            tickformat='%Y-%m-%d'  # Display only date without time
        ),
        yaxis=dict(
            showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)',  # Light grid lines
            color='#FFFFFF'
        ),
        plot_bgcolor='#1E1E1E',  # Set background color to dark grey
        paper_bgcolor='#1E1E1E',  # Set the paper background color
        margin=dict(l=40, r=40, t=60, b=40),  # Adjust margins
        height=400,  # Adjust the height of the chart
    )

    st.plotly_chart(fig)

def render_summary_section():
   
    st.markdown("<h1 style='text-align: center;'>Portfolio summary</h1>", unsafe_allow_html=True)



    portfolio_summary = fetch_portfolio_summary()
    dates_to_delete = [d['date'] for d in portfolio_summary]
    portfolio_percentage = get_portfolio_perc()

    if portfolio_summary:
        df = pd.DataFrame(portfolio_summary)
        generate_summary_chart(df)
        st.dataframe(df)

        
        
        
    else:
        st.warning("No data to display")

    col1, col2, col3 = st.columns(3, vertical_alignment="bottom")

    with col1:
        
        button_clicked = st.button("Generate Monthly report")
        if button_clicked:
            print(f'BUTTON KLIKNIETY')
            add_portfolio_entry()
            st.rerun()

    with col2:
        
        selected_portfolio_dates = st.multiselect(
            "Select date for delete:",
            dates_to_delete,
            key="summary_dates_to_delete"
        )


    with col3:
        
        button_delete = st.button("Delete entry")
        if button_delete:
            if selected_portfolio_dates:
                for date in selected_portfolio_dates:
                    delete_portfolio(date)
            st.rerun()
            

#FIXME: fix refreshing problem
    if portfolio_percentage:

        df_perc = pd.DataFrame(portfolio_percentage)
        fig = px.pie(
        df_perc, values='Percentage', names='Wallet',
        title='Portfolio split',
        labels={'Wallet': 'Wallet'}
        )

        # Update the traces
        fig.update_traces(textposition='inside', textinfo='percent+label')

        # Show the figure
        st.plotly_chart(fig)


