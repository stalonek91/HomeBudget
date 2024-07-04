import pandas as pd

def load_csv(file_path):
    

    try:
        df = pd.read_csv(file_path)
        print('CSV file loaded succesfully')
        return df
    except pd.errors.EmptyDataError:
        print('The file is empty!')
        return None
    except pd.errors.ParserError:
        print('The file is not a valid CSV file or is malformed!')
        return None
    except FileNotFoundError:
        print ("The file was not found. Please check file location and try again")
        return None
    except Exception as e:
        print(f'Error occurred: {str(e)}')
        return None
    
filepath = '/Users/sylwestersojka/Documents/HomeBudget/Transactions.csv' #will be changed later so user can select it
df = load_csv(file_path=filepath)

if df is not None:
    print(df.head())