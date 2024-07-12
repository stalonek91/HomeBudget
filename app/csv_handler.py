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
        
        self.new_column_names = ['date',
                                'receiver',
                                'title',
                                'amount', 
                                'transaction_type',
                                'category']

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
        try:
            base_df.fillna("", inplace=True)
            new_df = base_df[self.columns_to_keep].copy()
        except Exception as e:
            print(f'Error occurred: {str(e)}')
            return None
        return new_df
    

    def rename_columns(self, last_df):
        try:
            columns_dict = dict(zip(self.columns_to_keep, self.new_column_names))
            last_df.rename(columns=columns_dict, inplace=True)
            last_df = self.change_date_type(last_df)
        except Exception as e:
                print(f'Error occurred: {str(e)}')
                return None
        return last_df
    
    
    def change_date_type(self, last_df):
        try:

            last_df.loc[:, 'date'] = pd.to_datetime(last_df['date'], format='%d.%m.%Y', errors='coerce')
            last_df['date'] = last_df['date'].astype('datetime64[ns]')

            if last_df['date'].isna().any():
                print("Some dates could not be converted and are set to NaT")

            last_df.loc[:, 'date'] = last_df['date'].dt.strftime('%Y-%m-%d')
            last_df['amount'] = last_df['amount'].str.replace(',', '.').str.replace(' ', '').astype(float)



        except Exception as e:
            print(f'Error occurred: {str(e)}')
            return None
        return last_df









