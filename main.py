from csv_handler import CSVHandler

path_to_csv = '/Users/sylwestersojka/Documents/HomeBudget/Transactions.csv'
csv_instance = CSVHandler(path_to_csv)


if __name__ == '__main__':
    print(csv_instance.validate_csv())
    df = csv_instance.load_csv()
    print(df.head(5))
    
