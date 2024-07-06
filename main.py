from csv_handler import CSVHandler

path_to_csv = 'Transactions.csv'
csv_instance = CSVHandler(path_to_csv)


if __name__ == '__main__':
    df = csv_instance.load_csv()
    print(df.head(5))
    new_df = csv_instance.create_df_for_db(df)
    print(new_df.head(15))

