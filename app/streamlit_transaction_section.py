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
    tr_tab1, tr_tab2, tr_tab3 = st.tabs(["Load CSV", "Details of transactions", "Summary"])

    with tr_tab1:
        st.title('Load CSV to DB')
        print(f'1/2::: trying to upload a file')
        uploaded_file = st.file_uploader("Choose CSV file", type="csv")
        print(f'Uploaded file is: {uploaded_file}')
        print(f'2/2::: Code after file uploading')

        all_transactions = get_all_transactions()
        

        if uploaded_file is not None:
            response = add_csv_to_db(uploaded_file)
            if response is not None:
                st.success(response)
                all_transactions = get_all_transactions()
                if all_transactions:
                    df_tr = pd.DataFrame(all_transactions)
                    print("DataFrame created after file upload.")

        elif len(all_transactions) > 0:
            df_tr = pd.DataFrame(all_transactions)

        else:
            st.info("Please upload a CSV file")

        if df_tr is not None and not df_tr.empty:
            df_tr = csv_handler.remove_dupl(df=df_tr)
            time_lines = get_timeline()
            # timelines = list(time_lines.values())

            timeline_selection = st.multiselect(
                "Select timeline to display:",
                time_lines,
                key=f"transaction_timelines"
            )

            print(f'timeline_selection is : {timeline_selection}')

            if timeline_selection:
                print(f'Timeline selection is: {timeline_selection}')
                filtered_df = df_tr[df_tr['exec_month'].isin(timeline_selection)]
                st.dataframe(filtered_df)
            else:
                st.warning("No timeline selected. Showing all data.")
                st.dataframe(df_tr)
        else:
            st.info("No transactions available in the database.")

    if df_tr is not None and not df_tr.empty:
        with tr_tab2:
            met_col1, met_col2, met_col3 = st.columns(3)
            tr_col1, tr_col2 = st.columns(2)

            timeline_selection_details = st.multiselect(
                "Select timeline to display:",
                time_lines,
                key=f"timeline_selection_details"
            )

            filtered_df_summary = df_tr[df_tr['exec_month'].isin(timeline_selection_details)]

            with tr_col1:
                st.title(f'Expenses')
                grouped_df = filtered_df_summary.groupby('receiver')['amount'].sum().reset_index()
                grouped_df_exp = grouped_df[grouped_df['amount'] < 0]
                grouped_df_exp.columns = ['Reciever', 'Value']

                # Reseting index
                grouped_df_exp.reset_index(drop=True, inplace=True)
                grouped_df_exp.index = grouped_df_exp.index + 1
                grouped_df_exp.index.name = "Row Number"

                st.dataframe(grouped_df_exp, use_container_width=True)

            with tr_col2:
                st.title(f'Income')
                grouped_df = filtered_df_summary.groupby('receiver')['amount'].sum().reset_index()
                grouped_df_inc = grouped_df[grouped_df['amount'] > 0]
                grouped_df_inc.columns = ['Reciever', 'Value']

                # Reseting index
                grouped_df_inc.reset_index(drop=True, inplace=True)
                grouped_df_inc.index = grouped_df_inc.index + 1
                grouped_df_inc.index.name = "Row Number"

                st.dataframe(grouped_df_inc)

            with met_col1:
                if timeline_selection_details:
                    sum_of_exp = round(grouped_df_exp['Value'].sum(), 2)
                    st.metric(label='Expenses', value=sum_of_exp)

            with met_col2:
                if timeline_selection_details:
                    sum_of_inc = round(grouped_df_inc['Value'].sum(), 2)
                    st.metric(label='Income', value=sum_of_inc)

            with met_col3:
                st.write("Savings")

            add_left, add_middle, add_right = st.columns(3, vertical_alignment="bottom")

            rule_key = add_left.text_input("New Value:")
            rule_val = add_middle.text_input("Text to replace (contain New Value):")

            if add_right.button("Add Rule", use_container_width=True):
                print(f"Pressing add rule button adding following key:{rule_key} and val:{rule_val}")
                csv_handler.add_rule(rule_key=rule_key, rule_value=rule_val)
                st.rerun()

    with tr_tab3:
        pass