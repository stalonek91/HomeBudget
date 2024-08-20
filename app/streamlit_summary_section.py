import streamlit as st
import requests
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go


FASTAPI_URL = 'http://127.0.0.1:8000'

def get_profit():
    response = requests.get(f"{FASTAPI_URL}/portfolio/get_profit")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return []


def generate_summary_overall():
    response = requests.post(f"{FASTAPI_URL}/portfolio/generate_summary_overall")
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
    print(df)
    old, new = df[-2:]
    val_to_dis = new['Total_Value'] - old['Total_Value']
    deposits_to_dis = new['Deposits'] - old['Deposits']
    month_diff = float(val_to_dis)
    new_val = new['Total_Value']
    all_deposits = new['Deposits']
    all_profit = new['Total_Value'] - new['Deposits']
    profit_delta = all_profit - (old['Total_Value'] - old['Deposits'])

    return new_val, month_diff, deposits_to_dis, all_deposits, all_profit, profit_delta

    



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
        marker=dict(
            color='rgba(70, 130, 180, 0.8)',  # steelblue with some transparency
            line=dict(color='rgba(70, 130, 180, 1.0)', width=2)  # darker border
        ),
        hoverinfo='y'
    ))

    fig.add_trace(go.Bar(
        x=dates, 
        y=profits, 
        name='Profit',
        marker=dict(
            color='rgba(0, 128, 0, 0.8)',  # green with some transparency
            line=dict(color='rgba(0, 128, 0, 1.0)', width=2)  # darker border
        ),
        text=[f'{val:,.2f}' for val in total_values],  # format text with commas and two decimals
        textposition='outside',
        hoverinfo='y'
    ))

    fig.update_layout(barmode='stack')
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Value')

    st.plotly_chart(fig)

def render_summary_section():
    portfolio_summary = generate_summary_overall()
    st.markdown("<h1 style='text-align: center;'>Portfolio summary</h1>", unsafe_allow_html=True)
    

    col1_title, col2_title, col3_title  = st.columns(3, vertical_alignment="bottom")
    new_val, diff, deposits_diff, all_deposits, all_profit, profit_delta = calculate_profit_for_metric(portfolio_summary)
    
    with col1_title:
        
        st.metric(label='Total Value update', value=f"{new_val} zł" , delta=f"{diff} zł")
        
    with col2_title:
        profit_func = get_profit()
        profit = profit_func["profit"]
        profit_delta = profit_func["profit_delta"]
        st.metric(label='Profit', value=f"{profit} zł" , delta=f"{profit_delta} zł")
        

    with col3_title:
        st.metric(label='Sum of deposits update', value=f"{all_deposits} zł" , delta=f"{deposits_diff} zł")
        



    
    create_portfolio_summary_chart(portfolio_summary)
    
    portfolio_percentage = get_portfolio_perc()


    col3,col4 = st.columns(2, vertical_alignment="center")

    with col3:
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
    
    with col4:
        st.write("Tu bedzie sekcja + - portfeli")


