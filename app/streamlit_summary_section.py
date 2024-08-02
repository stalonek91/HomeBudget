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
    


    
#Plotly
# def generate_summary_graph(df):
#     fig = px.line(df, x='date', y='sum_of_acc', markers=True)
#     fig.show()

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
        title=dict(
            text=None,
            font=dict(size=24, family='Arial, sans-serif', color='#FFFFFF'),  # Larger font size, white color
            x=0.5,  # Center the title
        ),
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
            color='#FFFFFF'
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
    portfolio_percentage = get_portfolio_perc()

    if portfolio_summary:
        df = pd.DataFrame(portfolio_summary)
        generate_summary_chart(df)
        
        st.dataframe(df)
        
        st.button("Add portfolio entry (from today)")
    else:
        st.warning("No data to display")


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


        options = st.selectbox(
        "Show wallet details",
        df_perc,
        index=None,
        placeholder="Select Your wallet",
        )
        st.write("You selected:", options)