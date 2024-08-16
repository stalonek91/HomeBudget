import streamlit as st
import requests
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go


FASTAPI_URL = 'http://127.0.0.1:8000'

def generate_summary_overall():
    response = requests.get(f"{FASTAPI_URL}/portfolio/generate_summary_overall")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return []

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


def calculate_profit_for_metric(df):
    pass

    



#NEW CHART FOR PORTFOLIO WITHOUT DB

def create_portfolio_summary_chart(df):
    dates  = [entry['Date'] for entry in df]
    total_values  = [entry['Total_Value'] for entry in df]
    total_deposits  = [entry['Deposits'] for entry in df]
    profits = [total - deposit for total, deposit in zip(total_values, total_deposits)]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=dates,
        y=total_deposits,
        name='Deposits',
        marker=dict(color='lightblue'),
    
    ))

    fig.add_trace(go.Bar(
        x=dates, 
        y=profits, 
        name='Profit',
        marker=dict(color='blue'),
        text=total_values,
        textposition='outside'
        
    ))

    fig.update_layout(barmode='stack')
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Value')

    st.plotly_chart(fig)

def render_summary_section():

    col1_title, col2_title = st.columns(2, vertical_alignment="bottom")
    with col1_title:
        st.markdown("<h1 style='text-align: center;'>Portfolio summary</h1>", unsafe_allow_html=True)
    with col2_title:
        st.metric(label='Profit since last month', value="180823", delta="-1223 zł (to be implemented xd)")

    portfolio_summary = generate_summary_overall()
    create_portfolio_summary_chart(portfolio_summary)
    
    portfolio_percentage = get_portfolio_perc()


            

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


