import streamlit as st
import requests
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

from datetime import datetime, timedelta

FASTAPI_URL = 'http://127.0.0.1:8000'
wallet_endpoints = {

    "ViennaLife": "/vienna/get_all_vienna",
    "Nokia": "/nokia/get_all_nokia",
    "Generali": "/generali/get_all_generali",
    "Revolut": "/revolut/get_all_revolut",
    "Etoro": "/etoro/get_all_etoro",
    "Obligacje": "/obligacje/get_all_obligacje",
    "XTB" : "/xtb/get_all_xtb"

}

date_wallet_endpoints = {

    "ViennaLife": "/vienna/get_all_dates"

}

add_transaction_endpoints = {
    "ViennaLife": "/vienna/add_vienna_transaction",
    "Nokia": "/nokia/add_nokia_transaction",
    "Generali": "/generali/add_generali_transaction",
    "Revolut": "/revolut/add_revolut_transaction",
    "Etoro": "/etoro/add_etoro_transaction",
    "Obligacje": "/obligacje/add_obligacje_transaction",
    "XTB" : "/xtb/add_xtb_transaction"
}

delete_transaction_endpoints = {
    "ViennaLife": "/vienna/delete_vienna_transaction/",
    "Nokia": "/nokia/delete_nokia/",
    "Generali": "/generali/delete_generali/",
    "Revolut": "/revolut/delete_revolut/",
    "Etoro": "/etoro/delete_etoro/",
    "Obligacje": "/obligacje/delete_obligacje/",
    "XTB" : "/xtb/delete_xtb/"
}


def get_wallet_all(tab):
    endpoint = wallet_endpoints[tab]
    response = requests.get(f"{FASTAPI_URL}{endpoint}")

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return []

def get_wallet_dates(tab):

    endpoint = date_wallet_endpoints[tab]
    response = requests.get(f"{FASTAPI_URL}{endpoint}")

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return []
    

def fetch_wallet_totals(tab):

    endpoint = wallet_endpoints[tab]

    response = requests.get(f"{FASTAPI_URL}{endpoint}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return []
    
def add_transcation(tab, data):

    print(f'DEBUG: add_transaction endpoint function called')
    endpoint = add_transaction_endpoints[tab]
    url = f"{FASTAPI_URL}{endpoint}"

    payload = {
        "date": data.get('date'),
        "deposit_amount": data.get('deposit_amount'),
        "total_amount": data.get('total_amount')
    }

    print(f'ADD_TRANSACTION: Following data will be send: {payload}')

    response = requests.post(url=url, json=payload)

    if response.status_code == 201:
        return response.json()
    else:
        st.error(f"Failed to process POST request: {response.status_code}")
        return []
    
def delete_transaction(tab, date_obj):
    print(f'DEBUG: delete_transaction endpoint function called with tab {tab}')
    endpoint = delete_transaction_endpoints[tab]
    
    url = f"{FASTAPI_URL}{endpoint}{date_obj}"

    print(f'SELECTED ENDPOINT: {url}')

    response = requests.delete(url = url)

    if response.status_code == 200:
        return 'Entry Deleted'
    else:
        st.error(f"Failed to process POST request: {response.status_code}")
        return []
    




def generate_wallet_chart_2nd_with_legend(wallet_data):

    df = pd.DataFrame(wallet_data)


    # Check if the necessary columns exist
    if 'total_amount' not in df.columns or 'deposit_amount' not in df.columns:
        st.error("DataFrame must contain 'total_amount' and 'deposit_amount' columns.")
        return

    # Calculate profit as a separate column
    df['profit'] = df['total_amount'] - df['deposit_amount']
    df['color'] = df['profit'].apply(lambda x: 'blue' if x>= 0 else 'red')
    

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['date'], 
        y=df['deposit_amount'], 
        name='Deposit Amount',
        marker=dict(
            color='rgba(70, 130, 180, 0.8)',  # steelblue with some transparency
            line=dict(color='rgba(70, 130, 180, 1.0)', width=2)  # darker border
        ),
        hoverinfo='y'
    ))

    fig.add_trace(go.Bar(
        x=df['date'], 
        y=df['profit'], 
        name='Profit',
        marker=dict(
            color='rgba(0, 128, 0, 0.8)',  # green with some transparency
            line=dict(color='rgba(0, 128, 0, 1.0)', width=2)  # darker border
        ),
        text=[f'{val:,.2f}' for val in df['total_amount']],  # format text with commas and two decimals
        textposition='outside',
        hoverinfo='y'
    ))

    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['total_amount'], 
        mode='lines+markers', 
        name='Total Amount Trend',
        line=dict(color='grey', width=2),
        marker=dict(size=6)
    ))

    y_min = df['total_amount'].min() * 0.95
    y_max = df['total_amount'].max() * 1.05

    fig.update_layout(
        barmode='stack',
        xaxis_title='Date',
        yaxis_title='Value',
        title='Wallet Chart',
        yaxis=dict(range=[y_min, y_max]),
        xaxis=dict(
            tickformat="%b %Y",  # Adjusted to display month and year more clearly
            tickmode="array",
            tickvals=df['date'].tolist(),
        )
    )

    # Show the figure
    st.plotly_chart(fig)

    
def generate_wallet_chart(df, time_delta):

    
    fig = px.bar(df, x='date', y='total_amount',
                 labels={'total_amount': 'Value'}
                 )
    # Adjust bar width and other properties if necessary
    fig.update_traces(marker_line_width=0.3)



    # Ensure tickvals receives a list of values, not being mistakenly indexed
    fig.update_xaxes(
        tickformat="%Y-%m-%d",  
        tickmode="array",
        # tickvals=time_delta,
        # rangebreaks=[
        #     dict(values=time_delta)
        # ]
    )

    
    st.plotly_chart(fig)


def get_time_delta(tab):

    dates = get_wallet_dates(tab)
    dates_list = []
    
    for date in dates:
        for k,v in date.items():
            dates_list.append(v)
    dates_list.sort()
    
    date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in dates_list]

    all_dates = []

    for i in range(len(date_objects) -1):
        start_date = date_objects[i]
        end_date = date_objects[i+1]

        current_date = start_date + timedelta(days=1)

        while current_date < end_date:
            all_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

    
    return all_dates

def get_wallet_metrics(df, tab):
    wallet_data = fetch_wallet_totals(tab)
    
    last_entry, last_month_entry = wallet_data[-1], wallet_data[-2]
    
    total_amount = last_entry['total_amount']
    total_deposits = last_entry['deposit_amount']
    total_profit = total_amount-total_deposits

    last_month_total = last_month_entry['total_amount']
    last_moth_deposits = last_month_entry['deposit_amount']
    last_month_profit = last_month_total-last_moth_deposits

    total_delta = total_amount - last_month_total
    deposits_delta = total_deposits - last_moth_deposits
    profot_delta = total_profit - last_month_profit

    return total_amount, total_deposits, total_profit, total_delta, deposits_delta, profot_delta
    
    

def generate_wallet_tab(tab):
    st.title(f"{tab}")
    wallet_data = fetch_wallet_totals(tab)
    get_wallet_metrics(df=wallet_data, tab=tab)

    wallet_total, wallet_deposits, wallet_profit, total_delta, deposits_delta, profot_delta  = get_wallet_metrics(df=wallet_data, tab=tab)
    

    metric1, metric2, metric3 = st.columns(3, vertical_alignment="bottom")

    with metric1:
        st.metric(label='Total Value', value=f"{wallet_total} PLN" , delta=f"{total_delta} PLN")

    with metric2:
        st.metric(label='Total deposits', value=f"{wallet_deposits} PLN" , delta=f"{deposits_delta} PLN last month")
    
    with metric3:
        st.metric(label='Total Profit', value=f"{wallet_profit} PLN" , delta=f"{profot_delta} PLN last month")

    
    wallet_data = fetch_wallet_totals(tab)
    generate_wallet_chart_2nd_with_legend(wallet_data)

    st.write(f'Add {tab} entry:')

    col1, col3, col4, col5 = st.columns(4, vertical_alignment="bottom")

    with col1:
        v_date = st.date_input("Date of entry", key=f"{tab}_date_input")
        f_date = v_date.strftime('%Y-%m-%d')

    with col3:
        deposit_amount = float(st.number_input("Deposit amount:",step=100, key=f"{tab}_deposit_amount"))
    
    with col4:
        total_amount = float(st.number_input("Total now:",step=100, key=f"{tab}_total_amount"))

    with col5:
        button_clicked = st.button(f"Add {tab} to DB", key=f"{tab}_add_button")

    if button_clicked:
        print(f'BUTTON_{tab} KLIKNIETY')

        data = {
                "date": f_date,
                "deposit_amount": deposit_amount,
                "total_amount": total_amount
        }

        add_transcation(tab=tab, data=data)
        st.write(f'Following data will be send to DB: {data}')
        st.rerun()
    
    st.dataframe(wallet_data)

    dates_to_delete = [d['date'] for d in wallet_data]
    

    del1, del2 = st.columns(2, vertical_alignment="bottom")

    with del1:
        selected_dates = st.multiselect(
            "Select date for delete:",
            dates_to_delete,
            key=f"{tab}_dates_to_delete"
        )

    with del2:
        button_delete = st.button('Delete entry from DB', key=f"{tab}_delete_button")

        if button_delete:
            if selected_dates:
                for date in selected_dates:
                    delete_transaction(tab=tab, date_obj=date)
            st.rerun()
 
    



