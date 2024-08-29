import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from csv_handler import CSVHandler

FASTAPI_URL = 'http://127.0.0.1:8000'


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

def get_timeline():
    response = requests.get(f"{FASTAPI_URL}/transactions/get_timeline/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch response data: {response.status_code}")


def render_transaction_section():
        
        csv_handler = CSVHandler()
        df_tr = None
        tr_tab1, tr_tab2, tr_tab3  = st.tabs(["Load CSV", "Summary", "Details of transactions"])
        

        with tr_tab1:
            st.title('Load CSV to DB')
            print(f'1/2::: trying to upload a file')
            uploaded_file = st.file_uploader("Choose CSV file", type="csv")
            print(f'Uploaded file is: {uploaded_file}')
            print(f'2/2::: Code after file uploading')
            
            all_transactions = get_all_transactions()
            print(all_transactions)
            

            if uploaded_file is not None:
                response = add_csv_to_db(uploaded_file)
                if response is not None:
                    st.success(response)

            elif len(all_transactions) > 0:
                pass

            else:
                st.info("Please upload a CSV file")

            time_lines = get_timeline()
            timelines = list(time_lines.values())
            
            timeline_selection = st.multiselect(
                "Select timeline to display:",
                timelines,
                key=f"transaction_timelines"
            )

            


            if all_transactions:
                
                df_tr = pd.DataFrame(all_transactions)
                
            

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

            add_left, add_middle, add_right = st.columns(3, vertical_alignment="bottom")
            
            rule_key = add_left.text_input("New Value:")
            rule_val = add_middle.text_input("Text to replace (contain New Value):")

            if add_right.button("Add Rule", use_container_width=True):
                print(f"Pressing add rule button adding folowing key:{rule_key} and val:{rule_val}")
                csv_handler.add_rule(rule_key=rule_key, rule_value=rule_val)
                st.rerun()