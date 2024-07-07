import pandas as pd



class CSVHandler:

    def __init__(self, file_path: str) -> None:

        self.file_path = file_path
        self.columns_to_keep = [
            'Data księgowania',
            'Nadawca / Odbiorca',
            'Tytułem', 'Kwota operacji',
            'Typ operacji',
            'Kategoria']

    def load_csv(self):
        try:
            df = pd.read_csv(self.file_path, delimiter=';')
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
        
    def create_df_for_db(self, base_df):
        new_df = base_df[self.columns_to_keep]
        return new_df







