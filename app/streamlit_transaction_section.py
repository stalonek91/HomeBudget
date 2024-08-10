import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from csv_handler import CSVHandler

FASTAPI_URL = 'http://127.0.0.1:8000'

#TODO: To add some varaible stored in session that will unblock the button
def add_csv_to_db(file):

    files = {"file": (file.name, file, "text/csv")}
    response = requests.post(f"{FASTAPI_URL}/transactions/add_csv", files=files)
    if response.status_code == 201:
        return response.json()
    else:
        st.error(f"Failed to process the POST request: {response.status_code} \n with details: {response.json().get('detail', 'Unknown error')}")
        return None
    
def get_all_transactions():
    response = requests.get(f"{FASTAPI_URL}/transactions/get_transactions/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch response data: {response.status_code}")


def render_transaction_section():
        st.image('/Users/sylwestersojka/Documents/HomeBudget/app/belka.png')
        csv_handler = CSVHandler()
        df_tr = None
        tr_tab1, tr_tab2, tr_tab3  = st.tabs(["Load CSV", "Summary", "Details of transactions"])
        #FIXME: after addding the transaction additional reset is needed as looks like other transactions are not being added.

        with tr_tab1:
            st.title('Load CSV to DB')
            print(f'1/2::: trying to upload a file')
            uploaded_file = st.file_uploader("Choose CSV file", type="csv")
            print(f'2/2::: Code after file uploading')
            
            all_transactions = get_all_transactions()
            print(all_transactions)
            

            if uploaded_file is not None:
                response = add_csv_to_db(uploaded_file)
                if response is not None:
                    st.success(response)
            else:
                st.info("Please upload a CSV file")

            if all_transactions:
                df_tr = pd.DataFrame(all_transactions)
                print(f"df_tr loaded: {df_tr.head(5)}")

                if not df_tr.empty and 'receiver' in df_tr.columns:
                    df_tr = csv_handler.remove_dupl(df=df_tr)
                    st.dataframe(df_tr)
                else:
                    st.warning("DataFrame is empty or 'receiver' column not found.")

            else:
                st.info("No transactions available in the database.")

                    
            

        with tr_tab2:
            pass

        with tr_tab3:
            tr_col1, tr_col2 = st.columns(2)

            with tr_col1:

                st.title(f'Expenses')
                grouped_df = df_tr.groupby('receiver')['amount'].sum().reset_index()
                grouped_df = grouped_df[grouped_df['amount'] < 0]
                grouped_df.columns = ['Reciever', 'Value']

                #Reseting index
                grouped_df.reset_index(drop=True, inplace=True)
                grouped_df.index = grouped_df.index + 1
                grouped_df.index.name = "Row Number"

                st.dataframe(grouped_df, use_container_width=True)

            with tr_col2:

                st.title(f'Income')
                grouped_df = df_tr.groupby('receiver')['amount'].sum().reset_index()
                grouped_df = grouped_df[grouped_df['amount'] > 0]
                grouped_df.columns = ['Reciever', 'Value']

                #Reseting index
                grouped_df.reset_index(drop=True, inplace=True)
                grouped_df.index = grouped_df.index + 1
                grouped_df.index.name = "Row Number"

                st.dataframe(grouped_df)